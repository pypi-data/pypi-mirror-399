"""Aggregation methods for grid-to-polygon and polyline statistics.

This module provides classes for performing area-weighted statistics on gridded
data aggregated over polygon geometries (AggGen) and along polyline geometries
(InterpGen).

Classes:
    AggGen: Performs grid-to-polygon aggregation using area-weighted statistics.
    InterpGen: Calculates grid statistics along a polyline geometry.

Examples:
    Basic polygon aggregation:
        >>> from gdptools.agg_gen import AggGen
        >>> agg = AggGen(
        ...     user_data=my_data,
        ...     stat_method="mean",
        ...     agg_engine="serial",
        ...     agg_writer="csv",
        ...     weights=weights_df
        ... )
        >>> gdf, ds = agg.calculate_agg()

    Line interpolation:
        >>> from gdptools.agg_gen import InterpGen
        >>> interp = InterpGen(
        ...     user_data=my_data,
        ...     pt_spacing=100,
        ...     stat="mean"
        ... )
        >>> stats, points = interp.calc_interp()

"""

from datetime import datetime
from typing import Literal, Union

import geopandas as gpd
import netCDF4
import numpy as np
import numpy.typing as npt
import pandas as pd
import xarray as xr
from pyproj import CRS

from gdptools.agg.agg_data_writers import CSVWriter, JSONWriter, NetCDFWriter, ParquetWriter
from gdptools.agg.agg_engines import DaskAgg, DaskInterp, ParallelAgg, ParallelInterp, SerialAgg, SerialInterp
from gdptools.agg.stats_methods import (
    Count,
    MACount,
    MAMax,
    MAMin,
    MASum,
    MAWeightedMean,
    MAWeightedMedian,
    MAWeightedStd,
    Max,
    Min,
    Sum,
    WeightedMean,
    WeightedMedian,
    WeightedStd,
)
from gdptools.data.agg_gen_data import AggData
from gdptools.data.user_data import UserData

STATSMETHODS = Literal[
    "masked_mean",
    "mean",
    "masked_std",
    "std",
    "masked_median",
    "median",
    "masked_count",
    "count",
    "masked_sum",
    "sum",
    "masked_min",
    "min",
    "masked_max",
    "max",
]
"""Available aggregation methods.

Options:
    masked_mean: Masked mean of the data.
    mean: Mean of the data.
    masked_std: Masked standard deviation of the data.
    std: Standard deviation of the data.
    masked_median: Masked median of the data.
    median: Median of the data.
    masked_count: Masked count of the data.
    count: Count of the data.
    masked_sum: Masked sum of the data.
    sum: Sum of the data.
    masked_min: Masked minimum of the data.
    min: Minimum of the data.
    masked_max: Masked maximum of the data.
    max: Maximum of the data.
"""

AGGENGINES = Literal["serial", "parallel", "dask"]
"""Available aggregation engines.

Options:
    serial: Perform area-weighted aggregation sequentially.
    parallel: Perform area-weighted aggregation in parallel.
    dask: Perform area-weighted aggregation with Dask.
"""

AGGWRITERS = Literal["none", "csv", "parquet", "netcdf", "json"]
"""Available output writers.

Options:
    none: Do not write output to file.
    csv: Write output in CSV format.
    parquet: Write output in Parquet format.
    netcdf: Write output in NetCDF format.
    json: Write output in JSON format.
"""

WRITER_TYPES = Union[
    None.__class__,
    type[CSVWriter],
    type[ParquetWriter],
    type[NetCDFWriter],
    type[JSONWriter],
]

AGG_ENGINE_TYPES = Union[type[SerialAgg], type[ParallelAgg], type[DaskAgg]]

LINEITERPENGINES = Literal["serial", "parallel", "dask"]
"""Available line interpolation engines.

Options:
    serial: Perform interpolation sequentially.
    parallel: Perform interpolation in parallel.
    dask: Perform interpolation with Dask.
"""


class AggGen:
    """Performs grid-to-polygon aggregation using area-weighted statistics.

    This class provides functionality to aggregate gridded data over polygon
    geometries using various statistical methods and processing engines.

    Args:
        user_data: Input data for aggregation (e.g., UserCatData).
        stat_method: Statistical method to apply for aggregation.
        agg_engine: Aggregation engine to use for processing.
        agg_writer: Output writer format for results.
        weights: Path to CSV file or DataFrame containing area weights.
        out_path: Directory path for output files. Required if `agg_writer`
            is not 'none'.
        file_prefix: Prefix for output file names. Required if `agg_writer`
            is not 'none'.
        append_date: Whether to append current date to output file names.
        precision: Number of decimal places for output data rounding.
        jobs: Number of processors for parallel or dask engines. -1 uses all available.

    Attributes:
        agg_data: Dictionary mapping variable names to AggData instances after processing.

    Raises:
        ValueError: If agg_writer is not 'none' but out_path or file_prefix is missing.
        TypeError: If stat_method, agg_engine, or agg_writer is invalid.

    Examples:
        Basic aggregation with CSV output:
            >>> agg = AggGen(
            ...     user_data=my_data,
            ...     stat_method="mean",
            ...     agg_engine="serial",
            ...     agg_writer="csv",
            ...     weights="weights.csv",
            ...     out_path="/output",
            ...     file_prefix="results"
            ... )
            >>> gdf, dataset = agg.calculate_agg()

        Parallel processing with NetCDF output:
            >>> agg = AggGen(
            ...     user_data=my_data,
            ...     stat_method="masked_mean",
            ...     agg_engine="parallel",
            ...     agg_writer="netcdf",
            ...     weights=weights_df,
            ...     out_path="/output",
            ...     file_prefix="climate_data",
            ...     jobs=4
            ... )
            >>> gdf, dataset = agg.calculate_agg()

    """

    def __init__(
        self,
        user_data: UserData,
        stat_method: STATSMETHODS,
        agg_engine: AGGENGINES,
        agg_writer: AGGWRITERS,
        weights: Union[str, pd.DataFrame],
        out_path: str | None = None,
        file_prefix: str | None = None,
        append_date: bool = False,
        precision: int | None = None,
        jobs: int | None = -1,
    ) -> None:
        """Initialize the AggGen class with configuration parameters.

        Sets up the aggregation system by configuring the statistical method,
        processing engine, and output writer based on the provided parameters.

        Args:
            user_data: Input data container with source data and target geometries.
            stat_method: Statistical method for aggregation (e.g., 'mean', 'masked_mean').
            agg_engine: Processing engine ('serial', 'parallel', or 'dask').
            agg_writer: Output format ('none', 'csv', 'parquet', 'netcdf', 'json').
            weights: Path to weights CSV file or DataFrame with precomputed weights.
            out_path: Output directory path. Required if `agg_writer` is not 'none'.
            file_prefix: Prefix for output file names. Required if `agg_writer` is not 'none'.
            append_date: If True, append current date to output filenames.
            precision: Number of decimal places for rounding output values.
            jobs: Number of processors for parallel processing. -1 uses all available.

        Raises:
            ValueError: If `agg_writer` is not 'none' but `out_path` or `file_prefix` is missing.
            TypeError: If `stat_method`, `agg_engine`, or `agg_writer` is invalid.

        """
        self._user_data = user_data
        self._stat_method = stat_method
        self._agg_engine = agg_engine
        self._agg_writer = agg_writer
        self._weights = weights
        self._out_path = out_path
        self._file_prefix = file_prefix
        self._append_date = append_date
        self._precision = precision
        self._jobs: int = jobs or -1
        self._agg_data: dict[str, AggData]

        self._set_stats_method()
        self._set_agg_engine()
        self._set_writer()

    def _set_writer(self) -> None:
        """Configure the output writer class based on agg_writer parameter.

        Validates that required parameters are provided when writing is enabled
        and sets up the appropriate writer class for the specified output format.

        Raises:
            ValueError: If `agg_writer` is not 'none' but `out_path` or `file_prefix` is missing.
            TypeError: If `agg_writer` value is not supported.

        """
        if self._agg_writer != "none" and not (self._out_path and self._file_prefix):
            raise ValueError("If `agg_writer` is not 'none', both `out_path` and `file_prefix` must be set.")
        if self._agg_writer == "none":
            self.__writer: WRITER_TYPES = None  # type: ignore[assignment]
        else:
            writers = {
                "csv": CSVWriter,
                "parquet": ParquetWriter,
                "netcdf": NetCDFWriter,
                "json": JSONWriter,
            }
            try:
                self.__writer = writers[self._agg_writer]
            except KeyError as exc:
                raise TypeError(f"Invalid agg_writer: {self._agg_writer}") from exc

    def _set_agg_engine(self) -> None:
        """Configure the aggregation engine class based on agg_engine parameter.

        Sets up the appropriate processing engine (serial, parallel, or dask)
        for performing the aggregation calculations.

        Raises:
            TypeError: If `agg_engine` value is not supported.

        """
        engines = {"serial": SerialAgg, "parallel": ParallelAgg, "dask": DaskAgg}
        try:
            self.agg: AGG_ENGINE_TYPES = engines[self._agg_engine]
        except KeyError as exc:
            raise TypeError(f"Invalid agg_engine: {self._agg_engine}") from exc

    def _set_stats_method(self) -> None:
        """Configure the statistical method class based on stat_method parameter.

        Sets up the appropriate statistical calculation method for aggregation,
        supporting both masked and unmasked variants of common statistics.

        Raises:
            TypeError: If `stat_method` value is not supported.

        """
        methods = {
            "masked_mean": MAWeightedMean,
            "masked_std": MAWeightedStd,
            "masked_median": MAWeightedMedian,
            "masked_count": MACount,
            "masked_sum": MASum,
            "masked_min": MAMin,
            "masked_max": MAMax,
            "mean": WeightedMean,
            "std": WeightedStd,
            "median": WeightedMedian,
            "count": Count,
            "sum": Sum,
            "min": Min,
            "max": Max,
        }
        self._stat = methods.get(self._stat_method)
        if self._stat is None:
            raise TypeError(f"Invalid stat_method: {self._stat_method}")

    def calculate_agg(self) -> tuple[gpd.GeoDataFrame, xr.Dataset]:
        """Calculate area-weighted aggregations for target polygons.

        Performs the complete aggregation workflow: interpolates source gridded
        data to target polygons, computes the specified statistic, and optionally
        writes results to the specified output format.

        Returns:
            A tuple containing:
            - A GeoDataFrame with target polygons and computed statistics.
            - An xarray Dataset with aggregated values in CF-compliant format.

        Raises:
            TypeError: If writer or engine configuration is invalid.
            ValueError: If output path or file prefix is missing when writing is enabled.

        Examples:
            >>> agg = AggGen(user_data, "mean", "serial", "csv", weights_df)
            >>> gdf, dataset = agg.calculate_agg()
            >>> print(f"Processed {len(gdf)} polygons")

        """
        self._agg_data, new_gdf, agg_vals = self.agg().calc_agg_from_dictmeta(
            user_data=self._user_data,
            weights=self._weights,
            stat=self._stat,
            jobs=self._jobs,
        )
        if self._agg_writer != "none":
            self.__writer().save_file(
                agg_data=self._agg_data,
                target_gdf=new_gdf,
                vals=agg_vals,
                p_out=self._out_path,
                file_prefix=self._file_prefix,
                append_date=self._append_date,
                precision=self._precision,
            )

        return new_gdf, self._gen_xarray_return(target_gdf=new_gdf, vals=agg_vals)

    @property
    def agg_data(self) -> dict[str, AggData]:
        """Get the aggregation data collected during processing.

        Returns:
            dict[str, AggData]: A mapping from variable name to the corresponding
            ``AggData`` instance, which contains metadata and processed data for
            each variable.

        Notes:
            This property is populated only after calling ``calculate_agg()``.

        """
        return self._agg_data

    def _gen_xarray_return(
        self,
        target_gdf: gpd.GeoDataFrame,
        vals: list[npt.NDArray[np.int_ | np.double]],
    ) -> xr.Dataset:
        """Generate an xarray Dataset from aggregation results.

        Creates a CF-compliant xarray Dataset containing the aggregated values
        with appropriate coordinates, attributes, and metadata.

        Args:
            target_gdf: DataFrame of target polygons with feature identifiers.
            vals: List of aggregated value arrays for each variable.

        Returns:
            A CF-compliant xarray Dataset with variables, coordinates, and metadata.

        Notes:
            The returned Dataset includes proper encoding settings for NetCDF output
            and follows CF conventions for time series data.

        """
        datasets = []
        for idx, (_key, value) in enumerate(self._agg_data.items()):
            gdf = target_gdf
            idx_field = value.target_id
            param = value.cat_cr
            time_coord = param.T_name
            varname = param.varname

            data = np.round(vals[idx], self._precision) if self._precision is not None else vals[idx]
            dsn = xr.Dataset(
                data_vars={
                    varname: (
                        ["time", idx_field],
                        data,
                        {
                            "units": param.units,
                            "long_name": param.long_name,
                            "coordinates": "time",
                            "grid_mapping": "crs",
                        },
                    ),
                },
                coords={
                    "time": value.da.coords[time_coord].values,
                    idx_field: (
                        [idx_field],
                        gdf[idx_field].values,
                        {"feature_id": idx_field},
                    ),
                },
            )
            dtype = vals[idx].dtype.str
            if dtype == "<f8":
                dsn[varname].encoding["_FillValue"] = netCDF4.default_fillvals["f8"]
            elif dtype == "<i8":
                dsn[varname].encoding["_FillValue"] = netCDF4.default_fillvals["i8"]

            datasets.append(dsn)

        ds = xr.merge(datasets) if len(datasets) > 1 else datasets[0]
        ds.encoding["time"] = {"unlimited": True}
        timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        ds.attrs = {
            "Conventions": "CF-1.8",
            "featureType": "timeSeries",
            "history": (
                f"{timestamp} Original file created by gdptools: https://code.usgs.gov/wma/nhgf/toolsteam/gdptools\n"
            ),
        }
        return ds


class InterpGen:
    """Calculates grid statistics along polyline geometries.

    This class provides functionality to interpolate gridded data along polyline
    geometries at specified point intervals and compute statistics.

    Args:
        user_data: Input data container with source data and target polylines.
        pt_spacing: Spacing between interpolation points in meters. If ``None``,
            uses default spacing based on line geometry.
        stat: Statistic to calculate ("all", "mean", "median", "min", "max", "std").
        interp_method: xarray interpolation method ("linear", "nearest", "cubic").
        mask_data: Whether to mask nodata values during interpolation.
        output_file: Path to CSV file for saving results. If ``None``, no file is written.
        calc_crs: Coordinate reference system for interpolation calculations.
            Can be EPSG code, WKT string, or ``pyproj.CRS`` object.
        method: Interpolation engine to use for processing.
        jobs: Number of processors for parallel or dask engines. ``-1`` uses all available.

    Raises:
        ValueError: If the specified interpolation method is not supported.

    Examples:
        Basic line interpolation:
            >>> interp = InterpGen(
            ...     user_data=my_data,
            ...     pt_spacing=100,
            ...     stat="mean",
            ...     interp_method="linear"
            ... )
            >>> stats, points = interp.calc_interp()

        Parallel processing with custom CRS:
            >>> interp = InterpGen(
            ...     user_data=my_data,
            ...     pt_spacing=50,
            ...     stat="all",
            ...     calc_crs=3857,
            ...     method="parallel",
            ...     jobs=4
            ... )
            >>> stats, points = interp.calc_interp()

    """

    def __init__(
        self,
        user_data: UserData,
        *,
        pt_spacing: Union[float, int, None] = 50,
        stat: str = "all",
        interp_method: str = "linear",
        mask_data: bool = False,
        output_file: str | None = None,
        calc_crs: Union[str, int, CRS] = 6931,
        method: LINEITERPENGINES = "serial",
        jobs: int | None = -1,
    ) -> None:
        """Initialize the InterpGen class with configuration parameters.

        Sets up the interpolation system for calculating statistics along polyline
        geometries using the specified interpolation method and processing engine.

        Args:
            user_data: Input data container with source gridded data and target polylines.
            pt_spacing: Distance between interpolation points in meters. Default is 50m.
            stat: Statistical method to apply ("all", "mean", "median", "min", "max", "std").
            interp_method: xarray interpolation method ("linear", "nearest", "cubic").
            mask_data: If ``True``, mask nodata values during interpolation.
            output_file: Path to CSV file for saving results. If ``None``, no file is written.
            calc_crs: Coordinate reference system for calculations. Default is EPSG:6931.
            method: Processing engine ("serial", "parallel", "dask").
            jobs: Number of processors for parallel processing. ``-1`` uses all available.

        """
        self._user_data = user_data
        self._line = user_data.target_gdf
        self._pt_spacing = pt_spacing
        self._stat = stat
        self._interp_method = interp_method
        self._mask_data = mask_data
        self._output_file = output_file
        self._calc_crs = calc_crs
        self._method = method
        self._jobs = jobs or -1

    def calc_interp(self) -> Union[tuple[pd.DataFrame, gpd.GeoDataFrame], pd.DataFrame]:
        """Run interpolation and statistical calculations along polylines.

        Performs the complete interpolation workflow: generates points along
        polylines at specified intervals, interpolates gridded data to these
        points, and computes the requested statistics.

        Returns:
            Statistical results and interpolated points. Return type depends on
            the `stat` parameter:
            - If `stat` is 'all': tuple of (statistics DataFrame, points GeoDataFrame)
            - Otherwise: statistics DataFrame only

        Raises:
            ValueError: If the specified interpolation method is not supported.

        Examples:
            >>> interp = InterpGen(user_data, pt_spacing=100, stat="mean")
            >>> stats = interp.calc_interp()
            >>> print(f"Mean values: {stats['mean'].values}")

            >>> interp = InterpGen(user_data, pt_spacing=50, stat="all")
            >>> stats, points = interp.calc_interp()
            >>> print(f"Generated {len(points)} interpolation points")

        """
        engines = {
            "serial": SerialInterp,
            "parallel": ParallelInterp,
            "dask": DaskInterp,
        }
        key = self._method.lower()
        if key not in engines:
            raise ValueError(f"Invalid method: {self._method}. Available methods are: {', '.join(engines)}")

        self._interp_data, stats, pts = engines[key]().run(
            user_data=self._user_data,
            pt_spacing=self._pt_spacing,
            stat=self._stat,
            interp_method=self._interp_method,
            calc_crs=self._calc_crs,
            mask_data=self._mask_data,
            output_file=self._output_file,
        )
        return stats, pts
