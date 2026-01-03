"""Calculate zonal statistics for raster data.

This module provides classes for computing zonal statistics on raster data,
including both standard and weighted zonal statistics calculations. It supports
various computational engines (serial, parallel, and Dask) and output formats.

Classes:
    ZonalGen: Calculate standard zonal statistics for raster data.
    WeightedZonalGen: Calculate area-weighted zonal statistics for raster data.

Notes:
    This module requires that the user data has been properly preprocessed
    using the appropriate data preparation tools in the gdptools package.

"""

import time
from datetime import datetime
from pathlib import Path
from typing import Literal

import pandas as pd
from pyproj import CRS

from gdptools.agg.zonal_engines import ZonalEngineDask, ZonalEngineParallel, ZonalEngineSerial
from gdptools.data.user_data import UserData

ZONAL_ENGINES = Literal["serial", "parallel", "dask"]
"""Literal type alias for the zonal computation engines.

Options:
    serial: Perform zonal calculations in a serial manner.
    parallel: Perform zonal calculations in parallel using multiple processes.
    dask: Perform zonal calculations using Dask for distributed computing.
"""

ZONAL_WRITERS = Literal["csv"]
"""Literal type alias for the zonal statistics output formats.

Options:
    csv: Write zonal statistics to a CSV file.
"""


class ZonalGen:
    """Calculate standard zonal statistics for raster data.

    This class provides functionality to compute zonal statistics (mean, sum, count,
    etc.) for raster data within defined zones. It supports multiple computational
    engines for flexibility and performance optimization.

    The class handles the entire workflow from data preparation to result output,
    including options for different computational backends and output formats.

    Examples:
        Basic usage with serial computation:

        >>> from gdptools.zonal_gen import ZonalGen
        >>> from gdptools.data.user_data import UserData
        >>>
        >>> # Create zonal statistics generator
        >>> zonal_gen = ZonalGen(
        ...     user_data=user_data,
        ...     zonal_engine="serial",
        ...     zonal_writer="csv",
        ...     out_path="/path/to/output",
        ...     file_prefix="zonal_stats"
        ... )
        >>>
        >>> # Calculate zonal statistics
        >>> stats = zonal_gen.calculate_zonal()

        Parallel computation with date-stamped output:

        >>> zonal_gen = ZonalGen(
        ...     user_data=user_data,
        ...     zonal_engine="parallel",
        ...     zonal_writer="csv",
        ...     out_path="/path/to/output",
        ...     file_prefix="zonal_stats",
        ...     append_date=True,
        ...     jobs=4
        ... )
        >>> stats = zonal_gen.calculate_zonal()

    Attributes:
        agg: The zonal engine instance used for calculations.
        precision: Number of decimal places for output statistics.

    """

    def __init__(
        self,
        user_data: UserData,
        zonal_engine: ZONAL_ENGINES,
        zonal_writer: ZONAL_WRITERS,
        out_path: str | None = None,
        file_prefix: str | None = None,
        append_date: bool = False,
        precision: int | None = None,
        jobs: int = 1,
    ) -> None:
        """Initialize ZonalGen for calculating zonal statistics.

        Args:
            user_data: An instance of UserData containing the preprocessed raster
                and vector data for zonal analysis.
            zonal_engine: The computational engine to use for zonal calculations.
                Options: "serial", "parallel", or "dask".
            zonal_writer: The output format for zonal statistics. Currently
                supports "csv".
            out_path: Directory path where output files will be saved. If None,
                output will not be written to disk.
            file_prefix: Prefix for the output filename. If None, no prefix
                will be used.
            append_date: Whether to append current timestamp to the filename.
                Creates filenames like "2024_01_15_14_30_00_prefix.csv".
            precision: Number of decimal places for output statistics. If None,
                no rounding is applied.
            jobs: Number of parallel jobs for computation. Only used with
                "parallel" or "dask" engines.

        Raises:
            FileNotFoundError: If the specified output path does not exist.
            TypeError: If an invalid zonal engine is specified.

        Notes:
            The user_data should contain properly aligned raster and vector data
            with matching coordinate reference systems.

        """
        self._user_data = user_data
        self._zonal_engine = zonal_engine
        self._zonal_writer = zonal_writer
        self._jobs = jobs
        self._out_path = Path(out_path)
        if not self._out_path.exists():
            raise FileNotFoundError(f"Path: {self._out_path} does not exist")
        self._file_prefix = file_prefix
        self._append_date = append_date
        if self._append_date:
            self._fdate = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
            self._fname = f"{self._fdate}_{self._file_prefix}"
        else:
            self._fname = f"{self._file_prefix}"
        self.precision = precision
        self.agg: ZonalEngineSerial | ZonalEngineParallel | ZonalEngineDask
        if self._zonal_engine == "serial":
            self.agg = ZonalEngineSerial()
        elif self._zonal_engine == "parallel":
            self.agg = ZonalEngineParallel()
        elif self._zonal_engine == "dask":
            self.agg = ZonalEngineDask()
        else:
            raise TypeError(f"agg_engine: {self._zonal_engine} not in {ZONAL_ENGINES}")

    def calculate_zonal(self, categorical: bool = False) -> pd.DataFrame:
        """Calculate zonal statistics for raster data.

        Computes zonal statistics (mean, sum, count, etc.) for raster data within
        defined zones using the specified computational engine. Results are
        automatically saved to the configured output path if specified.

        Args:
            categorical: Whether to calculate categorical statistics (mode, unique
                counts) or continuous statistics (mean, sum, std, etc.). For
                categorical data like land cover classifications, set to True.

        Returns:
            pandas.DataFrame: Calculated zonal statistics with zones as rows and
            statistics as columns. The exact columns depend on the data type and
            whether `categorical=True`.

        Notes:
            The method automatically rounds results to the specified precision if set
            during initialization. Execution time is printed to stdout for performance
            monitoring.

        Examples:
        Calculate continuous zonal statistics:

            >>> stats = zonal_gen.calculate_zonal(categorical=False)
            >>> print(stats.columns) # doctest: +SKIP
            Index(['zone_id', 'mean', 'sum', 'count', 'std', 'min', 'max'])

            Calculate categorical zonal statistics:

            >>> stats = zonal_gen.calculate_zonal(categorical=True)
            >>> print(stats.columns) # doctest: +SKIP
            Index(['zone_id', 'mode', 'unique_count', 'majority_percent'])

        """
        tstrt = time.perf_counter()
        stats = self.agg.calc_zonal_from_aggdata(user_data=self._user_data, categorical=categorical, jobs=self._jobs)
        if self.precision is not None:
            stats = stats.round(self.precision)
        if self._zonal_writer == "csv":
            fullpath = self._out_path / f"{self._fname}.csv"
            stats.to_csv(fullpath, sep=",")
        tend = time.perf_counter()
        print(f"Total time for serial zonal stats calculation {tend - tstrt:0.4f} seconds")
        return stats
        # elif self._zonal_writer == "feather":
        #     fullpath = self._out_path / f"{self._fname}"
        #     stats.to_feather(path=fullpath, )


class WeightedZonalGen:
    """Calculate area-weighted zonal statistics for raster data.

    This class extends standard zonal statistics by incorporating area weights
    based on the intersection of raster cells with zone boundaries. This is
    particularly important when working with data in geographic coordinate
    systems or when raster cells are partially covered by zones.

    The weighting is based on the specified CRS and accounts for the actual
    area of intersection between raster cells and zone polygons, providing
    more accurate statistics for geographic analyses.

    Examples:
        Basic weighted zonal statistics:

        >>> from gdptools.zonal_gen import WeightedZonalGen
        >>> from pyproj import CRS
        >>>
        >>> # Create weighted zonal statistics generator
        >>> weighted_gen = WeightedZonalGen(
        ...     user_data=user_data,
        ...     weight_gen_crs=CRS.from_epsg(4326),
        ...     zonal_engine="parallel",
        ...     zonal_writer="csv",
        ...     out_path="/path/to/output",
        ...     file_prefix="weighted_stats",
        ...     jobs=4
        ... )
        >>>
        >>> # Calculate weighted zonal statistics
        >>> stats = weighted_gen.calculate_weighted_zonal()

        Using with equal-area projection for accurate area calculations:

        >>> # Use an equal-area projection for more accurate area weighting
        >>> albers_crs = CRS.from_proj4(
        ...     "+proj=aea +lat_1=29.5 +lat_2=45.5 +lat_0=37.5 +lon_0=-96"
        ... )
        >>> weighted_gen = WeightedZonalGen(
        ...     user_data=user_data,
        ...     weight_gen_crs=albers_crs,
        ...     zonal_engine="dask",
        ...     zonal_writer="csv",
        ...     out_path="/path/to/output",
        ...     precision=3
        ... )
        >>> stats = weighted_gen.calculate_weighted_zonal()

    Attributes:
        agg: The zonal engine instance used for calculations.
        precision: Number of decimal places for output statistics.

    """

    def __init__(
        self,
        user_data: UserData,
        weight_gen_crs: str | int | CRS,
        zonal_engine: ZONAL_ENGINES,
        zonal_writer: ZONAL_WRITERS,
        out_path: str | None = None,
        file_prefix: str | None = None,
        append_date: bool = False,
        precision: int | None = None,
        jobs: int = 1,
    ) -> None:
        """Initialize WeightedZonalGen for calculating area-weighted zonal statistics.

        Args:
            user_data: An instance of UserData containing the preprocessed raster
                and vector data for zonal analysis.
            weight_gen_crs: The coordinate reference system for area weight
                calculations. Can be an EPSG code (int), proj4 string (str),
                or pyproj CRS object. Should be an appropriate equal-area
                projection for accurate area calculations.
            zonal_engine: The computational engine to use for zonal calculations.
                Options: "serial", "parallel", or "dask".
            zonal_writer: The output format for zonal statistics. Currently
                supports "csv".
            out_path: Directory path where output files will be saved. If None,
                output will not be written to disk.
            file_prefix: Prefix for the output filename. If None, no prefix
                will be used.
            append_date: Whether to append current timestamp to the filename.
                Creates filenames like "2024_01_15_14_30_00_prefix.csv".
            precision: Number of decimal places for output statistics. If None,
                no rounding is applied.
            jobs: Number of parallel jobs for computation. Only used with
                "parallel" or "dask" engines.

        Raises:
            FileNotFoundError: If the specified output path does not exist.
            TypeError: If an invalid zonal engine is specified.

        Notes:
            For most accurate area-weighted calculations, use an equal-area
            projection appropriate for your study region. Geographic coordinate
            systems (like EPSG:4326) can introduce area distortions.

        """
        self._user_data = user_data
        self._weight_gen_crs = weight_gen_crs
        self._zonal_engine = zonal_engine
        self._zonal_writer = zonal_writer
        self._jobs = jobs
        self._out_path = Path(out_path)
        if not self._out_path.exists():
            raise FileNotFoundError(f"Path: {self._out_path} does not exist")
        self._file_prefix = file_prefix
        self._append_date = append_date
        if self._append_date:
            self._fdate = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
            self._fname = f"{self._fdate}_{self._file_prefix}"
        else:
            self._fname = f"{self._file_prefix}"
        self.precision = precision
        self.agg: ZonalEngineSerial | ZonalEngineParallel | ZonalEngineDask
        if self._zonal_engine == "serial":
            self.agg = ZonalEngineSerial()
        elif self._zonal_engine == "parallel":
            self.agg = ZonalEngineParallel()
        elif self._zonal_engine == "dask":
            self.agg = ZonalEngineDask()
        else:
            raise TypeError(f"agg_engine: {self._zonal_engine} not in {ZONAL_ENGINES}")

    def calculate_weighted_zonal(self, categorical: bool = False) -> pd.DataFrame:
        """Calculate area-weighted zonal statistics for raster data.

        Computes zonal statistics weighted by the actual area of intersection
        between raster cells and zone boundaries. This provides more accurate
        statistics when raster cells are partially covered by zones or when
        working with geographic coordinate systems.

        Args:
            categorical: Whether to calculate categorical statistics (mode, unique
                counts) or continuous statistics (mean, sum, std, etc.). For
                categorical data like land cover classifications, set to True.

        Returns:
            A DataFrame containing the calculated area-weighted zonal statistics
            with zones as rows and statistics as columns. The exact columns
            depend on the data type and whether categorical=True.

        Notes:
            The method automatically rounds results to the specified precision
            if set during initialization. Execution time is printed to stdout
            for performance monitoring.

        Examples:
            Calculate weighted continuous statistics:

            >>> stats = weighted_gen.calculate_weighted_zonal(categorical=False)
            >>> print(stats.columns) # doctest: +SKIP
            Index(['zone_id', 'weighted_mean', 'weighted_sum', 'total_area'])

            Calculate weighted categorical statistics:

            >>> stats = weighted_gen.calculate_weighted_zonal(categorical=True)
            >>> print(stats.columns) # doctest: +SKIP
            Index(['zone_id', 'weighted_mode', 'area_weighted_majority'])

        """
        tstrt = time.perf_counter()
        stats = self.agg.calc_weights_zonal_from_aggdata(
            user_data=self._user_data, crs=self._weight_gen_crs, categorical=categorical, jobs=self._jobs
        )
        if self.precision is not None:
            stats = stats.round(self.precision)
        if self._zonal_writer == "csv":
            fullpath = self._out_path / f"{self._fname}.csv"
            stats.to_csv(fullpath, sep=",")
        tend = time.perf_counter()
        print(f"Total time for serial zonal stats calculation {tend - tstrt:0.4f} seconds")
        return stats
        # elif self._zonal_writer == "feather":
        #     fullpath = self._out_path / f"{self._fname}"
        #     stats.to_feather(path=fullpath, )
