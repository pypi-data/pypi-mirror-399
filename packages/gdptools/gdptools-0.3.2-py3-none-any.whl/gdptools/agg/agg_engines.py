"""Computational Engines for Spatial Aggregation and Interpolation.

This module provides the backend processing engines for performing spatial
aggregation and interpolation tasks within the `gdptools` package. It includes
abstract base classes and their concrete implementations for serial, parallel
(joblib), and distributed (Dask) computation.

The primary components are:

- **Aggregation Engines (for grid-to-polygon statistics):**
  - `AggEngine`: Abstract base class for area-weighted aggregation.
  - `SerialAgg`: A sequential implementation.
  - `ParallelAgg`: A parallel implementation using `joblib`.
  - `DaskAgg`: A distributed implementation using `Dask`.

- **Interpolation Engines (for grid-to-line statistics):**
  - `InterpEngine`: Abstract base class for line interpolation.
  - `SerialInterp`: A sequential implementation.
  - `ParallelInterp`: A parallel implementation using `joblib`.
  - `DaskInterp`: A distributed implementation using `Dask`.

These engines are typically not used directly but are called by the higher-level
`AggGen` and `InterpGen` classes from the `gdptools.agg_gen` module.

"""

import contextlib
import logging
import os
import time
import warnings
from abc import ABC, abstractmethod
from collections import namedtuple
from collections.abc import Generator
from typing import Union

import dask
import geopandas as gpd
import numpy as np
import numpy.typing as npt
import pandas as pd
import xarray as xr
from joblib import Parallel, delayed, parallel_backend
from pyproj import CRS

from gdptools.agg.stats_methods import (
    Count,
    MACount,
    MAMax,
    MAMin,
    MAWeightedMean,
    MAWeightedMedian,
    MAWeightedStd,
    Max,
    Min,
    StatsMethod,
    WeightedMean,
    WeightedMedian,
    WeightedStd,
)
from gdptools.data.agg_gen_data import AggData
from gdptools.data.user_data import UserData
from gdptools.utils import (
    _cal_point_stats,
    _dataframe_to_geodataframe,
    _get_default_val,
    _get_interp_array,
    _get_line_vertices,
    _get_weight_df,
    _interpolate_sample_points,
)

logger = logging.getLogger(__name__)

AggChunk = namedtuple("AggChunk", ["ma", "wghts", "def_val", "index"])


def _resolve_jobs(requested_jobs: int | None, *, half_default: bool = False) -> int:
    """Clamp requested jobs to available CPUs and emit warnings when adjusted."""
    available_cpus = os.cpu_count() or 1
    if requested_jobs == -1:
        jobs = max(1, int(available_cpus / 2)) if half_default else available_cpus
    elif requested_jobs is None:
        jobs = available_cpus
    else:
        jobs = requested_jobs
    if jobs > available_cpus:
        warnings.warn(
            (
                f"jobs={jobs} exceeds the available CPU count ({available_cpus}). "
                "Reducing jobs to match available processors."
            ),
            RuntimeWarning,
            stacklevel=3,
        )
        jobs = available_cpus
    elif jobs < 1:
        warnings.warn(
            "jobs must be a positive integer; defaulting to 1.",
            RuntimeWarning,
            stacklevel=3,
        )
        jobs = 1
    return jobs

STAT_TYPES = Union[
    type[MAWeightedMean],
    type[WeightedMean],
    type[MAWeightedStd],
    type[WeightedStd],
    type[MAWeightedMedian],
    type[WeightedMedian],
    type[MACount],
    type[Count],
    type[MAMin],
    type[Min],
    type[MAMax],
    type[Max],
]


class AggEngine(ABC):
    """Abstract base class for area-weighted aggregation engines.

    This class defines the common interface and workflow for all aggregation
    engines (serial, parallel, dask). It uses the template method pattern,
    where `calc_agg_from_dictmeta` orchestrates the aggregation process, and
    subclasses must implement the `agg_w_weights` method to provide the
    specific computational logic.
    """

    def calc_agg_from_dictmeta(
        self,
        user_data: UserData,
        weights: str | pd.DataFrame,
        stat: STAT_TYPES,
        jobs: int = -1,
    ) -> tuple[dict[str, AggData], gpd.GeoDataFrame, list[npt.NDArray[np.int_ | np.double]]]:
        """Calculate aggregations using user data, weights, and a statistic.

        This is the main entry point for the aggregation engines. It sets up the
        necessary instance variables from the user-provided data and calls the
        `agg_w_weights` method, which is implemented by the concrete subclasses
        (e.g., SerialAgg, ParallelAgg).

        Args:
            user_data: The user data object containing source and target data.
            weights: A DataFrame or path to a CSV file with pre-computed
                area-weighted intersection weights.
            stat: The statistical method to apply (e.g., WeightedMean).
            jobs: The number of parallel jobs to use for computation.
                Defaults to -1 (use all available cores).

        Returns:
            A tuple containing:
                - A dictionary of `AggData` objects for each processed variable.
                - A GeoDataFrame of the target geometries.
                - A list of NumPy arrays with the aggregated values.

        """
        self.usr_data = user_data
        self.target_id = user_data.get_feature_id()
        self.vars = user_data.get_vars()
        self.stat = stat
        self.source_time_period = None
        self.wghts = _get_weight_df(weights, self.target_id)
        self._jobs = _resolve_jobs(jobs, half_default=True)
        # logger.info(f"  ParallelWghtGenEngine using {self._jobs} jobs")

        return self.agg_w_weights()

    @abstractmethod
    def agg_w_weights(
        self,
    ) -> tuple[
        dict[str, AggData],
        gpd.GeoDataFrame,
        list[npt.NDArray[np.int_ | np.double]],
    ]:
        """Abstract method for performing the aggregation calculation.

        Concrete subclasses must implement this method to provide the specific
        logic for serial, parallel, or distributed computation.
        """
        pass


class SerialAgg(AggEngine):
    """A serial engine for area-weighted aggregation.

    This engine processes each target polygon and variable sequentially in a
    single thread. It is reliable and useful for smaller datasets or for
    debugging purposes.
    """

    def get_period_from_ds(self, data: AggData) -> list[str]:
        """Get start and end time strings from a subsetted Dataset.

        Extracts the first and last time coordinates from the DataArray within
        the `AggData` object.

        Args:
            data: The `AggData` object containing the xarray DataArray.

        Returns:
            A list containing the start and end time as strings. Returns an
            empty list if a time coordinate is not found.

        """
        try:
            tname = data.cat_cr.T_name
            tstrt = str(data.da.coords[tname].values[0])
            tend = str(data.da.coords[tname].values[-1])
            return [tstrt, tend]
        except IndexError:
            # Handle the error
            print(
                "IndexError: This error suggests that the source_time_period argument has not been properly specified."
            )
            # Return an appropriate value or re-raise the error
            # For example, return an empty list or specific error code/message
            return []

    def agg_w_weights(
        self,
    ) -> tuple[
        dict[str, AggData],
        gpd.GeoDataFrame,
        list[npt.NDArray[np.int_ | np.double]],
    ]:
        """Aggregate grid-to-polygon values serially.

        This method iterates through each variable specified in the user data,
        prepares the data for aggregation, performs the aggregation using the
        `calc_agg` method, and collects the results.

        Returns:
            A tuple containing:
                - A dictionary mapping variable names to their corresponding
                  `AggData` objects.
                - The dissolved GeoDataFrame representing the aggregated geometries.
                - A list of NumPy arrays, where each array contains the
                  aggregated values for a specific variable.

        """
        # ds_time = self.ds.coords[list(self.param_dict.values())[0]["T_name"]].values
        # date_bracket = np.array_split(ds_time, self.numdiv)
        # print(date_bracket)
        # date_bracket = list(_date_range(self.source_time_period[0], self.source_time_period[1], self.numdiv))
        r_gdf = []
        r_vals = []
        r_agg_dict = {}
        avars = self.usr_data.get_vars()
        for index, key in enumerate(avars):
            print(f"Processing: {key}")
            tstrt = time.perf_counter()
            agg_data: AggData = self.usr_data.prep_agg_data(key=key)
            tend = time.perf_counter()
            print(f"    Data prepped for aggregation in {tend - tstrt:0.4f} seconds")
            tstrt = time.perf_counter()
            newgdf, nvals = self.calc_agg(key=key, data=agg_data)
            tend = time.perf_counter()
            print(f"    Data aggregated in {tend - tstrt:0.4f} seconds")
            if index == 0:
                # all new GeoDataFrames will be the same so save and return only one.
                r_gdf.append(newgdf)
            r_vals.append(nvals)
            r_agg_dict[key] = agg_data
        return r_agg_dict, r_gdf[0], r_vals

    def calc_agg(
        self: "SerialAgg", key: str, data: AggData
    ) -> tuple[gpd.GeoDataFrame, npt.NDArray[np.int_ | np.double]]:
        """Perform the core aggregation calculation for a single variable.

        This method performs the spatial and temporal aggregation for a single
        gridded variable over a set of target geometries. It handles data
        loading, weight application, and statistical calculation.

        Args:
            key: A reference key for the variable being aggregated.
            data: An `AggData` object containing the `DataArray`,
                `GeoDataFrame`, and metadata required for aggregation.

        Returns:
            A tuple containing:
                - The dissolved GeoDataFrame of target geometries.
                - A NumPy array of aggregated values with shape
                  (time_steps, n_geometries).

        Raises:
            ValueError: If the data is too large to load into memory, which
                can occur when accessing large remote datasets.

        """
        cp = data.cat_cr
        gdf = data.target_gdf
        gdf.reset_index(drop=True, inplace=True)
        gdf = gdf.sort_values(data.target_id).dissolve(by=data.target_id, as_index=False)
        geo_index = np.asarray(gdf[data.target_id].values, dtype=type(gdf[data.target_id].values[0]))
        n_geo = len(geo_index)
        unique_geom_ids = self.wghts.groupby(self.target_id)
        t_name = cp.T_name
        da = data.da
        nts = len(da.coords[t_name].values)
        native_dtype = da.dtype
        # gdptools will handle floats and ints - catch if gridded type is different
        try:
            dfval = _get_default_val(native_dtype=native_dtype)
        except TypeError as e:
            print(e)

        val_interp = _get_interp_array(n_geo=n_geo, nts=nts, native_dtype=native_dtype, default_val=dfval)
        try:
            da = da.load()
        except Exception as e:
            raise ValueError(
                "This error likely arises when the data requested to aggregate is too large to be retrieved from "
                "a remote server. Please try to reduce the time-period, or work on a smaller subset."
            ) from e
        for i in np.arange(len(geo_index)):
            try:
                weight_id_rows = unique_geom_ids.get_group(str(geo_index[i]))
            except KeyError:
                continue
            tw = weight_id_rows.wght.values
            i_ind = np.array(weight_id_rows.i.values).astype(int)
            j_ind = np.array(weight_id_rows.j.values).astype(int)

            val_interp[:, i] = self.stat(array=da.values[:, i_ind, j_ind], weights=tw, def_val=dfval).get_stat()

        return gdf, val_interp


class ParallelAgg(AggEngine):
    """A parallel engine for area-weighted aggregation using joblib.

    This engine distributes the aggregation calculation for different target
    polygons across multiple CPU cores. It is well-suited for medium-to-large
    datasets on a single machine to improve performance over serial processing.
    """

    def get_period_from_ds(self, data: AggData) -> list[str]:
        """Get start and end time strings from a subsetted Dataset.

        Args:
            data: The `AggData` object containing the xarray DataArray.

        Returns:
            A list containing the start and end time as strings. Returns an
            empty list if a time coordinate is not found.

        """
        try:
            tname = data.cat_cr.T_name
            tstrt = str(data.da.coords[tname].values[0])
            tend = str(data.da.coords[tname].values[-1])
            return [tstrt, tend]
        except IndexError:
            # Handle the error
            print(
                "IndexError: This error suggests that the source_time_period argument has not been properly specified."
            )
            # Return an appropriate value or re-raise the error
            # For example, return an empty list or specific error code/message
            return []

    def agg_w_weights(
        self,
    ) -> tuple[
        dict[str, AggData],
        gpd.GeoDataFrame,
        list[npt.NDArray[np.int_ | np.double]],
    ]:
        """Aggregate grid-to-polygon values in parallel.

        This method iterates through each variable specified in the user data,
        prepares the data for aggregation, performs the aggregation using the
        `calc_agg` method, and collects the results.

        Returns:
            A tuple containing:
                - A dictionary mapping variable names to their corresponding
                  `AggData` objects.
                - The dissolved GeoDataFrame representing the aggregated geometries.
                - A list of NumPy arrays, where each array contains the
                  aggregated values for a specific variable.

        """
        # ds_time = self.ds.coords[list(self.param_dict.values())[0]["T_name"]].values
        # date_bracket = np.array_split(ds_time, self.numdiv)
        # print(date_bracket)
        # date_bracket = list(_date_range(self.source_time_period[0], self.source_time_period[1], self.numdiv))
        r_gdf = []
        r_vals = []
        r_agg_dict = {}
        avars = self.usr_data.get_vars()
        for index, key in enumerate(avars):
            print(f"Processing: {key}")
            tstrt = time.perf_counter()
            agg_data: AggData = self.usr_data.prep_agg_data(key=key)
            tend = time.perf_counter()
            print(f"    Data prepped for aggregation in {tend - tstrt:0.4f} seconds")
            tstrt = time.perf_counter()
            newgdf, nvals = self.calc_agg(key=key, data=agg_data)
            tend = time.perf_counter()
            print(f"    Data aggregated in {tend - tstrt:0.4f} seconds")
            if index == 0:
                # all new GeoDataFrames will be the same so save and return only one.
                r_gdf.append(newgdf)
            r_vals.append(nvals)
            r_agg_dict[key] = agg_data
        return r_agg_dict, r_gdf[0], r_vals

    def calc_agg(
        self: "ParallelAgg", key: str, data: AggData
    ) -> tuple[gpd.GeoDataFrame, npt.NDArray[np.int_ | np.double]]:
        """Perform the core aggregation calculation in parallel using joblib.

        This method chunks the target geometries and distributes the statistical
        calculations across multiple processes. It handles data loading, weight
        application, and parallel computation.

        Args:
            key: A reference key for the variable being aggregated.
            data: An `AggData` object containing the `DataArray`,
                `GeoDataFrame`, and metadata required for aggregation.

        Returns:
            A tuple containing:
                - The dissolved GeoDataFrame of target geometries.
                - A NumPy array of aggregated values with shape
                  (time_steps, n_geometries).

        Raises:
            ValueError: If the data is too large to load into memory, which
                can occur when accessing large remote datasets.

        """
        cp = data.cat_cr
        source_time_period = self.get_period_from_ds(data=data)
        gdf = data.target_gdf
        # gdf.reset_index(drop=True, inplace=True)
        gdf = gdf.sort_values(self.target_id, axis=0).dissolve(self.target_id, as_index=False)
        geo_index = np.asarray(gdf.index, dtype=type(gdf.index.values[0]))
        # geo_index_chunk = np.array_split(geo_index, self._jobs)
        n_geo = len(geo_index)
        unique_geom_ids = self.wghts.groupby(self.target_id, sort=True)
        t_name = cp.T_name
        selection = {t_name: slice(source_time_period[0], source_time_period[1])}
        da = data.da.sel(**selection)  # type: ignore
        nts = len(da.coords[t_name].values)
        native_dtype = da.dtype
        # gdptools will handle floats and ints - catch if gridded type is different
        try:
            dfval = _get_default_val(native_dtype=native_dtype)
        except TypeError as e:
            print(e)

        val_interp = _get_interp_array(n_geo=n_geo, nts=nts, native_dtype=native_dtype, default_val=dfval)

        # mdata = np.ma.masked_array(da.values, np.isnan(da.values))  # type: ignore
        try:
            mdata = da.values  # type: ignore
        except Exception as e:
            raise ValueError(
                "This error likely arrises when the data requested to aggregate is too large to be retrieved from,"
                " a remote server."
                "Please try to reduce the time-period, or work on a smaller subset."
            ) from e

        chunks = get_weight_chunks(
            unique_geom_ids=unique_geom_ids,
            target_gdf=gdf,
            target_id=self.target_id,
            mdata=mdata,
            dfval=dfval,
        )

        worker_out = get_stats_parallel(
            n_jobs=self._jobs,
            stat=self.stat,
            bag=bag_generator(jobs=self._jobs, chunks=chunks),
        )

        for index, val in worker_out:
            val_interp[:, index] = val

        return gdf, val_interp


def _stats(bag: list[AggChunk], method: StatsMethod) -> tuple[npt.NDArray[np.int_], npt.NDArray[np.int_ | np.double]]:
    """Worker function to calculate a statistic on a chunk of data.

    Args:
        bag: A list of `AggChunk` objects, where each object contains the
            data array, weights, default value, and index for a geometry.
        method: The statistical method to apply.

    Returns:
            A tuple containing:
            - An array of indices for the processed geometries.
            - A 2D array of the calculated statistic values, with shape
              (n_time_steps, n_geometries_in_chunk).

    """
    vals = np.zeros((bag[0].ma.shape[0], len(bag)), dtype=bag[0].ma.dtype)
    index = np.zeros(len(bag), dtype=np.int_)
    for idx, b in enumerate(bag):
        index[idx] = b.index
        vals[:, idx] = method(array=b.ma, weights=b.wghts, def_val=b.def_val).get_stat()  # type: ignore
    return (index, vals)


def get_stats_parallel(
    n_jobs: int, stat: STAT_TYPES, bag: Generator[list[AggChunk], None, None]
) -> list[tuple[npt.NDArray[np.int_], npt.NDArray[np.int_ | np.double]]]:
    """Calculate statistics for data chunks in parallel using joblib.

    Args:
        n_jobs: The number of parallel jobs to run.
        stat: The statistical method to apply to each chunk.
        bag: A generator that yields lists of `AggChunk` objects. Each
            `AggChunk` contains the data array, weights, default value,
            and index for a geometry.

    Returns:
            A list of tuples, where each tuple contains:
            - An array of indices corresponding to the processed geometries.
            - An array of calculated statistic values for each geometry in
              the chunk.

    """
    with parallel_backend("loky", inner_max_num_threads=1):
        worker_out = Parallel(n_jobs=n_jobs)(delayed(_stats)(chunk, method=stat) for chunk in bag)
    return worker_out


def get_weight_chunks(
    unique_geom_ids: gpd.GeoDataFrame.groupby,
    target_gdf: gpd.GeoDataFrame,
    target_id: str,
    # mdata: np.ma.MaskedArray,  # type: ignore
    mdata: npt.NDArray,  # type: ignore
    dfval: np.int_ | np.double,
) -> list[AggChunk]:
    """Prepare data chunks for parallel aggregation.

    This function iterates through unique geometries, extracts the
    corresponding weights and data, and packages them into `AggChunk`
    objects for parallel processing.

    Args:
        unique_geom_ids: A `groupby` object of weights, grouped by target ID.
        target_gdf: The GeoDataFrame of target geometries.
        target_id: The identifier column for target geometries.
        mdata: The source gridded data as a NumPy array.
        dfval: The default fill value for the data type.

    Returns:
        A list of `AggChunk` objects, one for each target geometry.

    """
    # keys = list(unique_geom_ids.groups.keys())
    keys = target_gdf[target_id].values
    chunks = []
    # for idx, (name, group) in enumerate(unique_geom_ids):
    for idx, key in enumerate(keys):
        with contextlib.suppress(Exception):
            weight_id_rows = unique_geom_ids.get_group(str(key))
            chunks.append(
                AggChunk(
                    mdata[
                        :,
                        np.array(weight_id_rows.i.values).astype(int),
                        np.array(weight_id_rows.j.values).astype(int),
                    ],
                    weight_id_rows.wght.values,
                    dfval,
                    idx,
                )
            )
    return chunks


def bag_generator(jobs: int, chunks: list[AggChunk]) -> Generator[list[AggChunk], None, None]:
    """Generate chunks of data for parallel processing.

    Args:
        jobs: The number of parallel jobs (and thus, chunks) to create.
        chunks: A list of `AggChunk` objects to be divided.

    Yields:
        A list of `AggChunk` objects representing one chunk of work.

    """
    chunk_size = len(chunks) // jobs + 1
    for i in range(0, len(chunks), chunk_size):
        yield chunks[i : i + chunk_size]


class DaskAgg(AggEngine):
    """A distributed engine for area-weighted aggregation using Dask.

    This engine is designed for very large datasets and can scale computations
    across a Dask cluster. It partitions data and computations to be executed
    in parallel on multiple workers.
    """

    def get_period_from_ds(self, data: AggData) -> list[str]:
        """Get start and end time strings from a subsetted Dataset.

        Args:
            data: The `AggData` object containing the xarray DataArray.

        Returns:
            A list containing the start and end time as strings. Returns an
            empty list if a time coordinate is not found.

        """
        try:
            tname = data.cat_cr.T_name
            tstrt = str(data.da.coords[tname].values[0])
            tend = str(data.da.coords[tname].values[-1])
            return [tstrt, tend]
        except IndexError:
            # Handle the error
            print(
                "IndexError: This error suggests that the source_time_period argument has not been properly specified."
            )
            # Return an appropriate value or re-raise the error
            # For example, return an empty list or specific error code/message
            return []

    def agg_w_weights(
        self,
    ) -> tuple[
        dict[str, AggData],
        gpd.GeoDataFrame,
        list[npt.NDArray[np.int_ | np.double]],
    ]:
        """Aggregate grid-to-polygon values using Dask.

        This method iterates through each variable specified in the user data,
        prepares the data for aggregation, performs the aggregation using Dask
        and the `calc_agg` method, and collects the results.

        Returns:
        A tuple containing:
                - A dictionary mapping variable names to `AggData` objects.
                - The dissolved GeoDataFrame of aggregated geometries.
                - A list of NumPy arrays with the aggregated values.

        """
        r_gdf = []
        r_vals = []
        r_agg_dict = {}
        avars = self.usr_data.get_vars()
        for index, key in enumerate(avars):
            print(f"Processing: {key}")
            tstrt = time.perf_counter()
            agg_data: AggData = self.usr_data.prep_agg_data(key=key)
            tend = time.perf_counter()
            print(f"    Data prepped for aggregation in {tend - tstrt:0.4f} seconds")
            tstrt = time.perf_counter()
            newgdf, nvals = self.calc_agg(key=key, data=agg_data)
            tend = time.perf_counter()
            print(f"    Data aggregated in {tend - tstrt:0.4f} seconds")
            if index == 0:
                # all new GeoDataFrames will be the same so save and return only one.
                r_gdf.append(newgdf)
            r_vals.append(nvals)
            r_agg_dict[key] = agg_data
        return r_agg_dict, r_gdf[0], r_vals

    def calc_agg(self: "DaskAgg", key: str, data: AggData) -> tuple[gpd.GeoDataFrame, npt.NDArray[np.int_ | np.double]]:
        """Perform the core aggregation calculation using Dask.

        This method leverages Dask to perform spatial and temporal aggregation
        of gridded data over a set of target geometries. It handles data
        loading, weight application, and distributed statistical calculation.

        Args:
            key: A reference key for the variable being aggregated.
            data: An `AggData` object containing the `DataArray`,
                `GeoDataFrame`, and metadata required for aggregation.

        Returns:
            A tuple containing:
                - The dissolved GeoDataFrame of target geometries.
                - A NumPy array of aggregated values with shape
                  (time_steps, n_geometries).

        Raises:
            ValueError: If the data is too large to load into memory, which
                can occur when accessing large remote datasets.

        """
        cp = data.cat_cr
        source_time_period = self.get_period_from_ds(data=data)
        gdf = data.target_gdf
        gdf = gdf.sort_values(self.target_id, axis=0).dissolve(self.target_id, as_index=False)
        geo_index = np.asarray(gdf.index, dtype=type(gdf.index.values[0]))
        # geo_index_chunk = np.array_split(geo_index, self._jobs)
        n_geo = len(geo_index)
        unique_geom_ids = self.wghts.groupby(self.target_id, sort=True)
        t_name = cp.T_name
        selection = {t_name: slice(source_time_period[0], source_time_period[1])}
        da = data.da.sel(**selection)  # type: ignore
        nts = len(da.coords[t_name].values)
        native_dtype = da.dtype
        # gdptools will handle floats and ints - catch if gridded type is different
        try:
            dfval = _get_default_val(native_dtype=native_dtype)
        except TypeError as e:
            print(e)

        val_interp = _get_interp_array(n_geo=n_geo, nts=nts, native_dtype=native_dtype, default_val=dfval)

        try:
            mdata = da.values  # type: ignore
        except Exception as e:
            raise ValueError(
                "This error likely arrises when the data requested to aggregate is too large to be retrieved from,"
                " a remote server."
                "Please try to reduce the time-period, or work on a smaller subset."
            ) from e

        chunks = get_weight_chunks(
            unique_geom_ids=unique_geom_ids,
            target_gdf=gdf,
            target_id=self.target_id,
            mdata=mdata,
            dfval=dfval,
        )

        worker_out = get_stats_dask(
            n_jobs=self._jobs,
            stat=self.stat,
            bag=bag_generator(jobs=self._jobs, chunks=chunks),
        )

        for index, val in worker_out[0]:
            val_interp[:, index] = val

        return gdf, val_interp


def get_stats_dask(
    n_jobs: int,
    stat: STAT_TYPES,
    bag: Generator[list[AggChunk], None, None],
) -> list[list[tuple[npt.NDArray[np.int_], npt.NDArray[np.int_ | np.double]]]]:
    """Calculate statistics for data chunks using a Dask graph.

    Args:
        n_jobs: The number of Dask workers to use. Not currently used.
        stat: The statistical method to apply to each chunk.
        bag: A generator that yields lists of `AggChunk` objects.

    Returns:
        A list of lists of tuples, where each inner tuple contains:
            - An array of indices corresponding to the processed geometries.
            - An array of calculated statistic values for each geometry in
              the chunk.
        The outer list structure is a result of the Dask compute operation.

    """
    worker_out = [dask.delayed(_stats)(chunk, method=stat) for chunk in bag]  # type: ignore
    return dask.compute(worker_out)  # type: ignore


class InterpEngine(ABC):
    """Abstract base class for grid-to-line interpolation engines.

    This class defines the common interface and workflow for all interpolation
    engines (serial, parallel, dask). It uses the template method pattern,
    where `run` orchestrates the interpolation process, and subclasses must
    implement the `interp` method to provide the specific computational logic.
    """

    def run(
        self,
        *,
        user_data: UserData,
        pt_spacing: float | int | None,
        stat: str,
        interp_method: str,
        calc_crs: int | str | CRS,
        mask_data: float | int | None,
        output_file: str | None = None,
        jobs: int = -1,
    ) -> tuple[pd.DataFrame, gpd.GeoDataFrame] | pd.DataFrame:
        """Run the interpolation engine.

        This is the main entry point for the interpolation engines. It sets up
        the necessary instance variables and calls the `interp` method, which
        is implemented by the concrete subclasses (e.g., SerialInterp).

        Args:
            user_data: The user data object with source grid and target polylines.
            pt_spacing: The distance between interpolated points along the line
                in meters. If 0, line vertices are used.
            stat: The statistic to calculate ('all', 'mean', 'median', 'min',
                'max', 'std').
            interp_method: The xarray interpolation method to use ('linear',
                'nearest', 'cubic', etc.).
            calc_crs: The CRS to use for distance calculations.
            mask_data: If True, mask nodata values during interpolation.
            output_file: Optional path to save statistics to a CSV file.
            jobs: The number of parallel jobs to use. Defaults to -1.

        Returns:
            A tuple containing a DataFrame of statistics and a GeoDataFrame of
            the interpolated points, or just the statistics DataFrame if
            `stat` is not 'all'.

        """
        self._user_data = user_data
        self._pt_spacing = pt_spacing
        self._stat = stat
        self._interp_method = interp_method
        self._calc_crs = calc_crs
        self._mask_data = mask_data
        self._output_file = output_file
        self._jobs = _resolve_jobs(jobs, half_default=True)
        logger.info(f"  ParallelWghtGenEngine using {self._jobs} jobs")

        return self.interp()

    @abstractmethod
    def interp(self) -> None:
        """Abstract method for performing the interpolation calculation.

        Concrete subclasses must implement this method to provide the specific
        logic for serial, parallel, or distributed computation.
        """
        pass

    def get_variables(self, key: str) -> dict:
        """Get a dictionary of parameters needed for interpolation.

        This method extracts and organizes all necessary metadata for processing
        a single variable, such as CRS, coordinate names, and target IDs, into
        a dictionary for easy access by the interpolation methods.

        Args:
            key: The variable name to process.

        Returns:
            A dictionary containing configuration parameters for the variable.

        """
        # Get crs and coord names for gridded data
        user_data_type = self._user_data.get_class_type()

        if user_data_type == "ClimRCatData":
            grid_proj = self._user_data.source_cat_dict[key]["crs"]
            x_coord = self._user_data.source_cat_dict[key]["X_name"]
            y_coord = self._user_data.source_cat_dict[key]["Y_name"]
            t_coord = self._user_data.source_cat_dict[key]["T_name"]
            varname = self._user_data.source_cat_dict[key]["varname"]
            target_id = self._user_data.target_id

        elif user_data_type in ["UserCatData", "NHGFStacData"]:
            grid_proj = self._user_data.source_crs
            x_coord = self._user_data.source_x_coord
            y_coord = self._user_data.source_y_coord
            t_coord = self._user_data.source_t_coord
            target_id = self._user_data.target_id
            varname = key

        elif user_data_type == "UserTiffData":
            grid_proj = self._user_data.source_crs
            x_coord = self._user_data.source_x_coord
            y_coord = self._user_data.source_y_coord
            t_coord = None
            target_id = self._user_data.target_id
            varname = key

        return {
            "key": key,
            "varname": varname,
            "spacing": self._pt_spacing,
            "grid_proj": grid_proj,
            "calc_crs": self._calc_crs,
            "x_coord": x_coord,
            "y_coord": y_coord,
            "t_coord": t_coord,
            "target_id": target_id,
            "class_type": user_data_type,
            "stat": self._stat,
            "mask_data": self._mask_data,
        }


class SerialInterp(InterpEngine):
    """A serial engine for grid-to-line interpolation.

    This engine processes each polyline and variable sequentially in a single
    thread. It is reliable and useful for smaller datasets or for debugging.
    """

    def get_period_from_ds(self, data: AggData) -> list[str]:
        """Get start and end time strings from a subsetted Dataset.

        Args:
            data: The `AggData` object containing the xarray DataArray.

        Returns:
            A list containing the start and end time as strings. Returns an
            empty list if a time coordinate is not found.

        """
        try:
            tname = data.cat_cr.T_name
            tstrt = str(data.da.coords[tname].values[0])
            tend = str(data.da.coords[tname].values[-1])
            return [tstrt, tend]
        except IndexError:
            # Handle the error
            print(
                "IndexError: This error suggests that the source_time_period argument has not been properly specified."
            )
            # Return an appropriate value or re-raise the error
            # For example, return an empty list or specific error code/message
            return []

    def interp(
        self,
    ) -> tuple[dict[str, AggData], pd.DataFrame, gpd.GeoDataFrame]:
        """Interpolate values along line geometries serially.

        This method iterates through each variable and each line geometry,
        calling `grid_to_line_intersection` to perform the interpolation and
        statistical calculation for each line.

        Returns:
            A tuple containing:
                - A dictionary mapping variable names to their corresponding
                  `AggData` objects.
                - A DataFrame containing the calculated statistics.
                - A GeoDataFrame containing the interpolated point geometries.

        """
        # Get each grid variable
        wvars = self._user_data.get_vars()

        stats_list = []
        points_list = []
        out_grid = {}

        # Loop thru each grid variable
        for _index, key in enumerate(wvars):
            logger.debug(f"Starting to process {key}")
            # loop thru each line geometry
            line_dict = {}
            for i in range(len(self._user_data.target_gdf)):
                logger.debug("Looping through lines")
                # Pull geometry ID from geodataframe
                line_id = self._user_data.target_gdf.loc[[i]][self._user_data.target_id][i]
                # Prep the input data
                interp_data: AggData = self._user_data.prep_interp_data(key=key, poly_id=line_id)
                logger.debug("Defined interp_data")
                line_dict[line_id] = interp_data
                # Calculate statistics
                statistics, pts = self.grid_to_line_intersection(interp_data, key=key)
                logger.debug("Calculated stats and pts")
                stats_list.append(statistics)
                points_list.append(pts)

            out_grid[key] = line_dict

        stats = pd.concat(stats_list).reset_index()
        points = pd.concat(points_list).reset_index()

        if self._output_file:
            stats.to_csv(self._output_file)

        # Project points back to original crs
        points = points.to_crs(self._user_data.get_target_crs())
        logger.debug("Finished running serial interp")

        return out_grid, stats, points

    def grid_to_line_intersection(
        self: "InterpEngine", interp_data: "AggData", key: str | None = None
    ) -> tuple[pd.DataFrame, gpd.GeoDataFrame]:
        """Extract grid values and calculate statistics for a single polyline.

        This is the core worker method for the serial engine. It interpolates
        points along a single line geometry, extracts grid values at these
        points using the specified interpolation method, and calculates
        summary statistics.

        Args:
            interp_data: An `AggData` object containing the data and metadata
                for a single line geometry and variable.
            key: The name of the variable in the xarray Dataset.

        Returns:
            A tuple containing:
                - A DataFrame of the calculated statistics for the line.
                - A GeoDataFrame of the interpolated point geometries.

        """
        data_array = interp_data.da
        varname = interp_data.cat_cr.varname
        spacing = self._pt_spacing
        user_data_type = self._user_data.get_class_type()

        # Get crs and coord names for gridded data
        if user_data_type in ["ClimRCatData"]:
            grid_proj = self._user_data.source_cat_dict[key]["crs"]
            x_coord = self._user_data.source_cat_dict[key]["X_name"]
            y_coord = self._user_data.source_cat_dict[key]["Y_name"]
        elif user_data_type in ["UserCatData", "NHGFStacData", "UserTiffData"]:
            grid_proj = self._user_data.source_crs
            x_coord = self._user_data.source_x_coord
            y_coord = self._user_data.source_y_coord

        # Reproject line to the grid's crs
        line = interp_data.target_gdf.copy()
        geom = line.geometry.to_crs(grid_proj)
        # Either find line vertices
        if spacing == 0:
            x, y, dist = _get_line_vertices(geom=geom, calc_crs=self._calc_crs, crs=grid_proj)
        # Or interpolate sample points
        else:
            x, y, dist = _interpolate_sample_points(geom=geom, spacing=spacing, calc_crs=self._calc_crs, crs=grid_proj)

        # Get the grid values from the interpolated points
        interp_coords = {x_coord: ("pt", x), y_coord: ("pt", y)}
        interp_dataset = data_array.interp(**interp_coords, method=self._interp_method)

        feature_id_array = np.full(len(dist), interp_data.target_gdf[self._user_data.target_id].values[0])
        # Add point spacing distance and line IDs
        # If interp_dataset is a DataArray, make sure it has a name
        if isinstance(interp_dataset, xr.DataArray) and interp_dataset.name is None:
            interp_dataset = interp_dataset.rename("tiff")
        interp_dataset = xr.merge(
            [
                interp_dataset,
                xr.DataArray(dist, dims=["pt"], name="dist"),
                xr.DataArray(feature_id_array, dims=["pt"], name=self._user_data.target_id),
            ]
        )
        # Convert to pandas dataframe, reset index to avoid multi-indexed columns: annoying
        interp_geo_df = _dataframe_to_geodataframe(
            interp_dataset.to_dataframe(), crs=grid_proj, x_coord=x_coord, y_coord=y_coord
        )
        interp_geo_df.rename(columns={varname: "values"}, inplace=True)
        target_id_array = np.full(len(interp_geo_df), varname)
        interp_geo_df["varname"] = target_id_array
        # prefer date, feature id and varname, up front of dataframe.
        t_coord = interp_data.cat_cr.T_name
        if self._user_data.get_class_type() != "UserTiffData":
            out_vals: dict[str, float] = {"date": interp_dataset[t_coord].values}
            out_vals[self._user_data.target_id] = np.full(
                out_vals[next(iter(out_vals.keys()))].shape[0],
                interp_data.target_gdf[self._user_data.target_id].values[0],
            )
        else:
            out_vals: dict[str, float] = {
                self._user_data.target_id: interp_data.target_gdf[self._user_data.target_id].values
            }

        out_vals["varname"] = np.full(
            out_vals[next(iter(out_vals.keys()))].shape[0],
            interp_data.cat_cr.varname,
        )
        out_vals |= _cal_point_stats(
            data=interp_dataset[interp_data.cat_cr.varname],
            userdata_type=self._user_data.get_class_type(),
            stat=self._stat,
            skipna=self._mask_data,
        )
        stats_df = pd.DataFrame().from_dict(out_vals)

        return stats_df, interp_geo_df


class ParallelInterp(InterpEngine):
    """A parallel engine for grid-to-line interpolation using joblib.

    This engine distributes the interpolation calculation for different polylines
    across multiple CPU cores. It is well-suited for medium-to-large datasets
    on a single machine to improve performance over serial processing.
    """

    def get_period_from_ds(self, data: AggData) -> list[str]:
        """Get starting and ending time strings from a subsetted Dataset.

        Args:
            data: The `AggData` object containing the xarray DataArray.

        Returns:
            A list containing the start and end time as strings. Returns an
            empty list if a time coordinate is not found.

        """
        try:
            tname = data.cat_cr.T_name
            tstrt = str(data.da.coords[tname].values[0])
            tend = str(data.da.coords[tname].values[-1])
            return [tstrt, tend]
        except IndexError:
            # Handle the error
            print(
                "IndexError: This error suggests that the source_time_period argument has not been properly specified."
            )
            # Return an appropriate value or re-raise the error
            # For example, return an empty list or specific error code/message
            return []

    def interp(
        self,
    ) -> tuple[dict[str, xr.DataArray], pd.DataFrame, gpd.GeoDataFrame]:
        """Interpolate values along line geometries in parallel using joblib.

        This method chunks the target polylines and distributes the
        interpolation and statistical calculations across multiple processes.

        Returns:
        A tuple containing:
                - A dictionary mapping variable names to their corresponding
                  xarray DataArrays.
                - A DataFrame containing the calculated statistics.
                - A GeoDataFrame containing the interpolated point geometries.

        """
        # Get each grid variable
        wvars = self._user_data.get_vars()

        stats_list = []
        points_list = []
        out_grid = {}

        # Loop thru each grid variable
        for _index, key in enumerate(wvars):
            # Chunk the geodataframe into equal parts
            gdf_list = _chunk_gdf(self._jobs, self._user_data.target_gdf)

            # Clip gridded data to 2d bounds of the input gdf
            data_array: xr.DataArray = self._user_data.get_source_subset(key)

            # Comb the user_data object for variables needed for the processing
            variables: dict = self.get_variables(key)
            variables["interp_method"] = self._interp_method

            with parallel_backend("loky", inner_max_num_threads=1):
                worker_out = Parallel(n_jobs=self._jobs)(
                    delayed(_grid_to_line_intersection)(chunk, data_array, variables) for chunk in gdf_list
                )

            key_stats: pd.DataFrame = pd.concat(list(zip(*worker_out))[0])  # noqa B905
            key_points: gpd.GeoDataFrame = pd.concat(list(zip(*worker_out))[1])  # noqa B905
            stats_list.append(key_stats)
            points_list.append(key_points)
            out_grid[key] = data_array
            del worker_out, key_stats, key_points

        stats = pd.concat(stats_list).reset_index()
        points = pd.concat(points_list).reset_index()

        if self._output_file:
            stats.to_csv(self._output_file)

        # Project points back to original crs
        points = points.to_crs(self._user_data.source_crs)

        return out_grid, stats, points


class DaskInterp(InterpEngine):
    """A distributed engine for grid-to-line interpolation using Dask.

    This engine is designed for very large datasets and can scale computations
    across a Dask cluster. It partitions data and computations to be executed
    in parallel on multiple workers.
    """

    def get_period_from_ds(self, data: AggData) -> list[str]:
        """Get starting and ending time strings from a subsetted Dataset.

        Args:
            data: The `AggData` object containing the xarray DataArray.

        Returns:
            A list containing the start and end time as strings. Returns an
            empty list if a time coordinate is not found.

        """
        try:
            tname = data.cat_cr.T_name
            tstrt = str(data.da.coords[tname].values[0])
            tend = str(data.da.coords[tname].values[-1])
            return [tstrt, tend]
        except IndexError:
            # Handle the error
            print(
                "IndexError: This error suggests that the source_time_period argument has not been properly specified."
            )
            # Return an appropriate value or re-raise the error
            # For example, return an empty list or specific error code/message
            return []

    def interp(
        self,
    ) -> tuple[dict[str, xr.DataArray], pd.DataFrame, gpd.GeoDataFrame]:
        """Interpolate values along line geometries using a Dask graph.

        This method creates a Dask Bag from the line geometries and maps the
        interpolation function (`g2l`) across the partitions for distributed
        computation.

        Returns:
            A tuple containing:
                - A dictionary mapping variable names to their corresponding
                  xarray DataArrays.
                - A DataFrame containing the calculated statistics.
                - A GeoDataFrame containing the interpolated point geometries.

        """
        import dask.bag as db

        # Get each grid variable, get line ids
        wvars = self._user_data.get_vars()
        line_ids_list = self._user_data.target_gdf.index.to_list()

        stats_list = []
        points_list = []
        out_grid = {}

        # Loop thru each grid variable
        for _index, key in enumerate(wvars):
            # Clip gridded data to 2d bounds of the gdf
            self.data_array: xr.DataArray = self._user_data.get_source_subset(key)
            # Comb the user_data object for variables needed for the processing
            self.variables: dict = self.get_variables(key)

            bag = db.from_sequence(line_ids_list).map(self.g2l)
            results = bag.compute()
            del bag

            key_stats: pd.DataFrame = pd.concat(list(zip(*results))[0])  # noqa B905
            key_points: gpd.GeoDataFrame = pd.concat(list(zip(*results))[1])  # noqa B905
            stats_list.append(key_stats)
            points_list.append(key_points)
            out_grid[key] = self.data_array
            del results, key_stats, key_points

        stats = pd.concat(stats_list).reset_index()
        points = pd.concat(points_list).reset_index()

        if self._output_file:
            stats.to_csv(self._output_file)

        # Project points back to original crs
        points = points.to_crs(self._user_data.target_crs)

        return out_grid, stats, points

    def g2l(self, id: int) -> tuple[pd.DataFrame, gpd.GeoDataFrame]:
        """Perform grid-to-line interpolation for a single geometry.

        This is the core worker function for the Dask engine. It is mapped
        over a Dask Bag to process each line geometry in parallel. It handles
        point generation, interpolation, and statistical calculation for one
        line.

        Args:
            id: The row index of the line geometry in the target GeoDataFrame.

        Returns:
            A tuple containing:
                - A DataFrame of the calculated statistics for the line.
                - A GeoDataFrame of the interpolated point geometries.

        """
        variables = self.variables
        variables["interp_method"] = self._interp_method

        line = self._user_data.target_gdf.loc[[id]]
        geom = line.geometry

        # Either find line vertices
        if variables["spacing"] == 0:
            x, y, dist = _get_line_vertices(geom=geom, calc_crs=variables["calc_crs"], crs=variables["grid_proj"])

        # Or interpolate sample points
        else:
            x, y, dist = _interpolate_sample_points(
                geom=geom,
                spacing=variables["spacing"],
                calc_crs=variables["calc_crs"],
                crs=variables["grid_proj"],
            )

        # Get the grid values from the interpolated points
        interp_coords = {variables["x_coord"]: ("pt", x), variables["y_coord"]: ("pt", y)}
        interp_dataset = self.data_array.interp(**interp_coords, method=variables["interp_method"])

        feature_id_array = np.full(len(dist), line[variables["target_id"]].values[0])
        # Add distsance and polygon IDs
        interp_dataset = xr.merge(
            [
                interp_dataset,
                xr.DataArray(dist, dims=["pt"], name="dist"),
                xr.DataArray(feature_id_array, dims=["pt"], name=variables["target_id"]),
            ]
        )

        interp_geo_df = _dataframe_to_geodataframe(
            interp_dataset.to_dataframe(),
            crs=variables["grid_proj"],
            x_coord=variables["x_coord"],
            y_coord=variables["y_coord"],
        )
        interp_geo_df.rename(columns={variables["varname"]: "values"}, inplace=True)
        target_id_array = np.full(len(interp_geo_df), variables["varname"])
        interp_geo_df["varname"] = target_id_array

        # prefer date, feature id and varname, up front of dataframe.
        if variables["t_coord"] is not None:
            out_vals: dict[str, float] = {"date": interp_dataset[variables["t_coord"]].values}
            out_vals[variables["target_id"]] = np.full(
                out_vals[next(iter(out_vals.keys()))].shape[0],
                line[variables["target_id"]].values[0],
            )
        else:
            out_vals: dict[str, float] = {variables["target_id"]: line[variables["target_id"]].values}

        out_vals["varname"] = np.full(
            out_vals[next(iter(out_vals.keys()))].shape[0],
            variables["varname"],
        )
        out_vals |= _cal_point_stats(
            data=interp_dataset[variables["varname"]],
            userdata_type=variables["class_type"],
            stat=variables["stat"],
            skipna=variables["mask_data"],
        )

        stats = pd.DataFrame().from_dict(out_vals)

        return stats, interp_geo_df


def _chunk_gdf(processes: int, target_gdf: gpd.GeoDataFrame) -> list[gpd.GeoDataFrame]:
    """Divide a GeoDataFrame into chunks for parallel processing.

    Args:
        processes: The number of chunks to create (should match the number
            of parallel jobs).
        target_gdf: The GeoDataFrame to divide.

    Returns:
        A list of GeoDataFrames, where each item is a chunk of the original.

    """
    from math import ceil

    gdf_list = []
    num_feat = len(target_gdf)
    batch_size = ceil(num_feat / processes)
    bottom_row = batch_size
    top_row = 0
    while top_row < num_feat:
        gdf_list.append(target_gdf[top_row:bottom_row])
        top_row += batch_size
        bottom_row += batch_size
        bottom_row = min(bottom_row, num_feat)
    return gdf_list


def _grid_to_line_intersection(
    chunk: gpd.GeoDataFrame, data_array: xr.DataArray, variables: dict
) -> tuple[pd.DataFrame, gpd.GeoDataFrame]:
    """Worker function to interpolate gridded data along line geometries.

    This function processes a chunk of line geometries. For each line, it
    generates points, extracts gridded data values at these points, and
    calculates summary statistics.

    Args:
        chunk: A GeoDataFrame containing one or more line geometries to process.
        data_array: The xarray DataArray containing the source gridded data.
        variables: A dictionary containing configuration parameters for the
            interpolation process (e.g., CRS, coordinate names, method).

    Returns:
        A tuple containing:
            - A DataFrame of calculated statistics for the lines in the chunk.
            - A GeoDataFrame of the interpolated point geometries.

    """
    stats_list = []
    interp_geo_list = []

    for i in range(len(chunk)):
        line: gpd.GeoDataFrame = chunk.reset_index().loc[[i]]
        geom: gpd.GeoSeries = line.geometry.to_crs(variables["grid_proj"])

        # Either find line vertices
        if variables["spacing"] == 0:
            x, y, dist = _get_line_vertices(geom=geom, calc_crs=variables["calc_crs"], crs=variables["grid_proj"])

        # Or interpolate sample points
        else:
            x, y, dist = _interpolate_sample_points(
                geom=geom,
                spacing=variables["spacing"],
                calc_crs=variables["calc_crs"],
                crs=variables["grid_proj"],
            )
        # Get the grid values from the interpolated points
        interp_coords = {variables["x_coord"]: ("pt", x), variables["y_coord"]: ("pt", y)}
        interp_dataset = data_array.interp(**interp_coords, method=variables["interp_method"])

        feature_id_array = np.full(len(dist), line[variables["target_id"]].values[0])
        # Add distsance and polygon ids
        interp_dataset = xr.merge(
            [
                interp_dataset,
                xr.DataArray(dist, dims=["pt"], name="dist"),
                xr.DataArray(feature_id_array, dims=["pt"], name=variables["target_id"]),
            ]
        )

        interp_geo_df = _dataframe_to_geodataframe(
            interp_dataset.to_dataframe(),
            crs=variables["grid_proj"],
            x_coord=variables["x_coord"],
            y_coord=variables["y_coord"],
        )
        interp_geo_df.rename(columns={variables["varname"]: "values"}, inplace=True)
        target_id_array = np.full(len(interp_geo_df), variables["varname"])
        interp_geo_df["varname"] = target_id_array
        interp_geo_list.append(interp_geo_df)

        # prefer date, feature id and varname, up front of dataframe.
        if variables["t_coord"] is not None:
            out_vals: dict[str, float] = {"date": interp_dataset[variables["t_coord"]].values}
            out_vals[variables["target_id"]] = np.full(
                out_vals[next(iter(out_vals.keys()))].shape[0],
                line[variables["target_id"]].values[0],
            )
        else:
            out_vals: dict[str, float] = {variables["target_id"]: line[variables["target_id"]].values}

        out_vals["varname"] = np.full(
            out_vals[next(iter(out_vals.keys()))].shape[0],
            variables["varname"],
        )
        out_vals |= _cal_point_stats(
            data=interp_dataset[variables["varname"]],
            userdata_type=variables["class_type"],
            stat=variables["stat"],
            skipna=variables["mask_data"],
        )
        stats_list.append(pd.DataFrame().from_dict(out_vals))

    interp_geo_df: gpd.GeoDataFrame = pd.concat(interp_geo_list)
    stats_df: pd.DataFrame = pd.concat(stats_list)

    return stats_df, interp_geo_df
