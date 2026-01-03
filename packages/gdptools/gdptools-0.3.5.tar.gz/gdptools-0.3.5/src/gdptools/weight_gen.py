"""Weight generation for grid-to-polygon spatial intersections.

This module provides classes for calculating area-weighted intersection weights
between gridded datasets and vector polygon geometries. These weights are essential
for performing accurate area-weighted aggregations in climate and environmental
data analysis.

Classes:
    WeightGen: Calculates grid-to-polygon intersection weights using various engines.

Examples:
    Basic weight calculation:
        >>> from gdptools.weight_gen import WeightGen
        >>> weight_gen = WeightGen(
        ...     user_data=my_data,
        ...     method="serial",
        ...     weight_gen_crs=6931
        ... )
        >>> weights = weight_gen.calculate_weights()

    Parallel processing with output file:
        >>> weight_gen = WeightGen(
        ...     user_data=my_data,
        ...     method="parallel",
        ...     weight_gen_crs=6931,
        ...     output_file="weights.csv",
        ...     jobs=4
        ... )
        >>> weights = weight_gen.calculate_weights()

"""

import time
import warnings
from typing import Literal

import geopandas as gpd
import pandas as pd
from pyproj import CRS

from gdptools.data.user_data import UserData
from gdptools.data.weight_gen_data import WeightData
from gdptools.weights.calc_weight_engines import DaskWghtGenEngine, ParallelWghtGenEngine, SerialWghtGenEngine

LARGE_TARGET_POLY_WARNING_THRESHOLD = 50_000
"""Polygon count above which we suggest switching to Dask/explicit chunking."""

WEIGHT_GEN_METHODS = Literal["serial", "parallel", "dask"]
"""Available weight generation processing methods.

Options:
    serial: Sequential processing through polygons one by one.
        Best for small datasets or debugging.
    parallel: Multi-core processing with polygon chunks distributed across CPUs.
        Optimal for moderate datasets with many polygons.
    dask: Distributed computing using Dask framework.
        Ideal for large datasets or cluster environments.

Note:
    Choose the method based on your computational resources and dataset size.
    Serial is most reliable, parallel offers good speedup for many polygons,
    and dask excels with very large datasets or when a Dask client is available.

Examples:
    >>> method = "serial"  # For smaller datasets
    >>> method = "parallel"  # For larger datasets
    >>> method = "dask"  # For very large or distributed datasets

"""


class WeightGen:
    """Calculates grid-to-polygon intersection weights for area-weighted aggregation.

    This class computes spatial intersection weights between gridded datasets and
    vector polygon geometries. The weights represent the proportional area of overlap
    and are essential for accurate area-weighted statistical aggregations.

    Args:
        user_data: Input data container with source grid and target polygons.
        method: Processing method for weight calculation.
        weight_gen_crs: Coordinate reference system for weight calculations.
            Accepts EPSG codes, WKT strings, or pyproj CRS objects.
        output_file: Path to save weights CSV file. If None, weights are not saved.
        jobs: Number of processors for parallel or dask methods. -1 uses all available.
        verbose: Whether to print detailed processing information.

    Attributes:
        grid_cells: GeoDataFrame of source grid cells after processing.
        intersections: GeoDataFrame of polygon intersections (if calculated).

    Raises:
        TypeError: If method is not one of the supported processing methods.

    Examples:
        Basic serial weight calculation:
            >>> weight_gen = WeightGen(
            ...     user_data=my_data,
            ...     method="serial",
            ...     weight_gen_crs=6931
            ... )
            >>> weights = weight_gen.calculate_weights()

        Parallel processing with file output:
            >>> weight_gen = WeightGen(
            ...     user_data=my_data,
            ...     method="parallel",
            ...     weight_gen_crs=6931,
            ...     output_file="weights.csv",
            ...     jobs=4,
            ...     verbose=True
            ... )
            >>> weights = weight_gen.calculate_weights()

    """

    def __init__(
        self,
        *,
        user_data: UserData,
        method: str,
        weight_gen_crs: str | int | CRS,
        output_file: str | None | None = None,
        jobs: int | None = -1,
        verbose: bool | None = False,
    ) -> None:
        """Initialize the WeightGen class with configuration parameters.

        Sets up the weight generation system by configuring the processing method,
        coordinate reference system, and output options.

        Args:
            user_data: Input data container with source grid and target polygons.
                Must be an instance of UserData subclass (UserCatData, NHGFStacData, etc.).
            method: Processing method for weight calculation ('serial', 'parallel', 'dask').
            weight_gen_crs: Coordinate reference system for calculations.
                Accepts EPSG codes, WKT strings, or pyproj CRS objects.
            output_file: Path to save weights as CSV file. If None, no file is saved.
            jobs: Number of processors for parallel/dask methods. -1 uses all available.
            verbose: If True, prints detailed processing information during execution.

        Raises:
            TypeError: If method is not one of the supported processing methods.

        """
        self.user_data = user_data
        self.method = method
        self.output_file = "" if output_file is None else output_file
        self.weight_gen_crs = weight_gen_crs
        self.jobs = jobs
        self.verbose = verbose
        self._intersections: gpd.GeoDataFrame
        self.__calc_method: SerialWghtGenEngine | ParallelWghtGenEngine | DaskWghtGenEngine
        if self.method == "serial":
            self.__calc_method = SerialWghtGenEngine()
            print("Using serial engine")
        elif self.method == "parallel":
            self.__calc_method = ParallelWghtGenEngine()
            print("Using parallel engine")
        elif self.method == "dask":
            self.__calc_method = DaskWghtGenEngine()
        else:
            raise TypeError(f"method: {self.method} not in [serial, parallel]")

    def calculate_weights(self, intersections: bool = False) -> pd.DataFrame:
        """Calculate spatial intersection weights between grid and polygons.

        Computes area-weighted intersection weights for each target polygon
        with source grid cells. The weights represent the proportional area
        of overlap and are used for accurate area-weighted aggregations.

        Args:
            intersections: If True, calculate and store detailed intersection
                geometries between target and source polygons. This provides
                additional spatial information but increases memory usage.

        Returns:
            pandas.DataFrame: The calculated weights with columns such as
                `target_id`, `i_index`, `j_index`, and `weight` (0.0-1.0).

        Notes:
            Processing time depends on the number of polygons and grid resolution.
            Use `intersections=True` only when detailed geometric information is needed.

        Examples:
            >>> weights = weight_gen.calculate_weights()
            >>> print(f"Calculated {len(weights)} weight entries")

            >>> # With intersection details
            >>> weights = weight_gen.calculate_weights(intersections=True)
            >>> intersections = weight_gen.intersections

        """
        tstrt = time.perf_counter()
        self._weight_data: WeightData = self.user_data.prep_wght_data()
        tend = time.perf_counter()
        print(f"Data preparation finished in {tend - tstrt:0.4f} seconds")
        target_count = len(self._weight_data.target_gdf)
        if self.method != "dask" and target_count > LARGE_TARGET_POLY_WARNING_THRESHOLD:
            warnings.warn(
                (
                    f"WeightGen detected {target_count:,} target polygons but method='{self.method}'. "
                    "Consider switching to method='dask' or chunking targets to avoid excessive memory usage."
                ),
                RuntimeWarning,
                stacklevel=2,
            )
        if self.method in {"parallel", "dask"} and (self.jobs is None or self.jobs == -1):
            warnings.warn(
                (
                    "jobs=-1 uses all available cores and duplicates the source dataset for each worker. "
                    "Set jobs to a smaller value if you experience memory pressure."
                ),
                RuntimeWarning,
                stacklevel=2,
            )
        if intersections:
            print("Saving intersections in weight generation.")
            weights, self._intersections = self.__calc_method.calc_weights(
                target_poly=self._weight_data.target_gdf,
                target_poly_idx=self._weight_data.target_id,
                source_poly=self._weight_data.grid_cells,
                source_poly_idx=["i_index", "j_index"],
                source_type="grid",
                wght_gen_crs=self.weight_gen_crs,
                filename=self.output_file,
                intersections=intersections,
                jobs=self.jobs,
                verbose=self.verbose,
            )
        else:
            weights = self.__calc_method.calc_weights(
                target_poly=self._weight_data.target_gdf,
                target_poly_idx=self._weight_data.target_id,
                source_poly=self._weight_data.grid_cells,
                source_poly_idx=["i_index", "j_index"],
                source_type="grid",
                wght_gen_crs=self.weight_gen_crs,
                filename=self.output_file,
                intersections=intersections,
                jobs=self.jobs,
                verbose=self.verbose,
            )
        return weights

    @property
    def grid_cells(self) -> gpd.GeoDataFrame:
        """Get the source grid cells as a GeoDataFrame.

        Returns the grid cells used in weight calculations. These represent
        the source grid geometry after processing and CRS transformation.

        Returns:
            geopandas.GeoDataFrame: Source grid cells with spatial geometry and
            grid indices (`i_index`, `j_index`).

        Notes:
            This property is only populated after calling `calculate_weights()`.
            If accessed before weight calculation, a message will be printed.

        """
        if self._weight_data.grid_cells is None:
            print("grid_cells not calculated yet. Run calculate_weights().")
        return self._weight_data.grid_cells

    @property
    def intersections(self) -> gpd.GeoDataFrame:
        """Get the polygon intersection geometries as a GeoDataFrame.

        Returns the detailed intersection geometries between target polygons
        and source grid cells. This provides the actual spatial overlap areas
        used in weight calculations.

        Returns:
            geopandas.GeoDataFrame: Intersection geometries with target/source
            identifiers and calculated areas.

        Notes:
            This property is only populated after calling
            `calculate_weights(intersections=True)`. If accessed otherwise, a
            message will be printed.

        """
        if self._intersections is None:
            print("intersections not calculated. Run calculate_weights(intersections=True)")
        return self._intersections
