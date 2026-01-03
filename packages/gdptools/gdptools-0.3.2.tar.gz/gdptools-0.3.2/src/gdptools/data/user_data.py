"""User data classes for standardizing input data across different sources.

This module provides a comprehensive set of classes for handling various types of
geospatial data sources in the gdptools package. These classes serve as data
containers that standardize inputs from different sources (STAC catalogs, local
files, web services) and ensure all necessary metadata is available for processing.

The module implements an abstract base class pattern with specialized subclasses
for different data source types, providing a consistent interface for data
preparation, spatial subsetting, and aggregation operations.

Classes:
    UserData: Abstract base class defining the common interface for all data sources.
    ClimRCatData: Interface for Climate-R catalog datasets with automatic metadata handling.
    UserCatData: Handler for user-provided xarray datasets with custom configuration.
    NHGFStacData: Interface for NHGF STAC catalog datasets with spatiotemporal filtering.
    UserTiffData: Specialized handler for GeoTIFF and raster data processing.

Examples:
    Using Climate-R catalog data:

    .. code-block:: python

        from gdptools.data.user_data import ClimRCatData
        import pandas as pd

        # Load catalog and create data source
        cat_url = "https://github.com/mikejohnson51/climateR-catalogs/releases/download/June-2024/catalog.parquet"
        cat = pd.read_parquet(cat_url)
        cat_dict = {"temp": cat.query("id == 'gridmet' & variable == 'tmmn'").to_dict("records")[0]}

        data = ClimRCatData(
            source_cat_dict=cat_dict,
            target_gdf="watersheds.shp",
            target_id="huc12",
            source_time_period=["2020-01-01", "2020-12-31"]
        )

    Using custom xarray dataset:

    .. code-block:: python

        from gdptools.data.user_data import UserCatData
        import xarray as xr

        # Load custom dataset
        ds = xr.open_dataset("climate_data.nc")

        data = UserCatData(
            source_ds=ds,
            source_crs=4326,
            source_x_coord="longitude",
            source_y_coord="latitude",
            source_t_coord="time",
            source_var=["temperature", "precipitation"],
            target_gdf="regions.shp",
            target_crs=4326,
            target_id="region_id",
            source_time_period=["2020-01-01", "2020-12-31"]
        )

Notes:
    All classes automatically handle coordinate reference system validation,
    spatial intersection checking, and temporal subsetting to ensure data
    compatibility for downstream processing operations.

"""

import datetime
import logging
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Union

import geopandas as gpd
import numpy as np
import pandas as pd
import xarray as xr
from pyproj import CRS

from gdptools.data.agg_gen_data import AggData
from gdptools.data.odap_cat_data import CatClimRItem
from gdptools.data.weight_gen_data import WeightData
from gdptools.depreciation_utils import deprecate_kwargs
from gdptools.helpers import build_subset, build_subset_tiff
from gdptools.utils import (
    _check_for_intersection,
    _check_for_intersection_nc,
    _get_cells_poly,
    _get_data_via_catalog,
    _get_rxr_dataset,
    _get_shp_bounds_w_buffer,
    _get_shp_file,
    _get_top_to_bottom,
    _get_xr_dataset,
    _is_valid_crs,
    _process_period,
    _read_shp_file,
)

logger = logging.getLogger(__name__)


class UserData(ABC):
    """Abstract base class for standardizing geospatial data inputs.

    This class defines the common interface that all data source classes must
    implement. It ensures consistent data preparation, spatial subsetting, and
    aggregation capabilities across different data sources (catalogs, files, web
    services).

    The class enforces a standardized workflow for data handling:
    1. Data loading and validation
    2. Coordinate reference system handling
    3. Spatial and temporal subsetting
    4. Data preparation for weight generation and aggregation

    All subclasses must implement the abstract methods to provide source-specific
    functionality while maintaining interface consistency.

    Notes:
        This is an abstract base class and cannot be instantiated directly.
        Use one of the concrete subclasses (ClimRCatData, UserCatData,
        NHGFStacData, UserTiffData) instead.

    """

    @abstractmethod
    def __init__(self) -> None:
        """Initialize the data source.

        This method must be implemented by subclasses to handle source-specific
        initialization requirements.

        """
        pass

    @abstractmethod
    def get_target_crs(self) -> CRS:
        """Get the coordinate reference system of the target geometries.

        Returns:
            The coordinate reference system of the target vector data.

        """
        pass

    @abstractmethod
    def get_source_subset(self, key: str) -> xr.DataArray:
        """Get a spatially and temporally subset of the source data.

        Args:
            key (str): Variable name or identifier for the data to subset.

        Returns:
            A spatially and temporally subset DataArray for the specified variable.

        """
        pass

    @abstractmethod
    def prep_wght_data(self) -> WeightData:
        """Prepare data for weight generation calculations.

        Returns:
            A WeightData instance containing the necessary data for calculating
            spatial intersection weights between source and target geometries.

        """
        pass

    @abstractmethod
    def prep_interp_data(self, key: str, poly_id: Union[str, int]) -> AggData:
        """Prepare data for interpolation operations.

        Args:
            key (str): Variable name or identifier for the data to prepare.
            poly_id (Union[str, int]): Identifier for the target polygon geometry.

        Returns:
            An AggData instance configured for interpolation operations.

        """
        pass

    @abstractmethod
    def prep_agg_data(self, key: str) -> AggData:
        """Prepare data for aggregation operations.

        Args:
            key (str): Variable name or identifier for the data to prepare.

        Returns:
            An AggData instance configured for aggregation operations.

        """
        pass

    @abstractmethod
    def get_vars(self) -> list[str]:
        """Get the list of available variables in the data source.

        Returns:
            list[str]: List of variable names available for processing.

        """
        pass

    @abstractmethod
    def get_feature_id(self) -> str:
        """Get the identifier column name for target geometries.

        Returns:
            str: The column name used as the unique identifier for target geometries.

        """
        pass

    @abstractmethod
    def get_class_type(self) -> str:
        """Get the type identifier for this data source class.

        Returns:
            str: A string identifier for the data source type (e.g., "ClimRCatData").

        """
        pass


class ClimRCatData(UserData):
    """Interface for Climate-R catalog datasets with automatic metadata handling.

    This class provides seamless integration with the Climate-R catalog system,
    developed by Mike Johnson and available at https://github.com/mikejohnson51/climateR-catalogs.
    It automatically handles metadata extraction, coordinate system detection, and
    spatial/temporal subsetting for catalog-based datasets.

    The class accepts Climate-R catalog dictionaries and automatically configures
    data access parameters, coordinate names, and temporal ranges based on the
    catalog metadata.

    Attributes:
        source_cat_dict: Dictionary mapping variable names to Climate-R catalog metadata.
        target_gdf: GeoDataFrame containing target geometries for spatial operations.
        target_id: Column name for unique identifiers in target geometries.
        source_time_period: Processed time period for temporal subsetting.

    Examples:
        Basic usage with Climate-R catalog:

        .. code-block:: python

            import pandas as pd
            from gdptools.data.user_data import ClimRCatData

            # Load Climate-R catalog
            cat_url = "https://github.com/mikejohnson51/climateR-catalogs/releases/download/June-2024/catalog.parquet"
            cat = pd.read_parquet(cat_url)

            # Create catalog dictionary for TerraClimate variables
            cat_vars = ["aet", "pet", "PDSI"]
            cat_params = [
                cat.query("id == 'terraclim' & variable == @var").to_dict("records")[0]
                for var in cat_vars
            ]
            source_cat_dict = dict(zip(cat_vars, cat_params))

            # Initialize data source
            data = ClimRCatData(
                source_cat_dict=source_cat_dict,
                target_gdf="watersheds.shp",
                target_id="huc12",
                source_time_period=["2020-01-01", "2020-12-31"]
            )

            # Access data
            variables = data.get_vars()
            subset = data.get_source_subset("aet")

        Multiple variables from GridMET:

        .. code-block:: python

            # GridMET temperature and precipitation
            gm_vars = ["tmmn", "tmmx", "pr"]
            gm_params = [
                cat.query("id == 'gridmet' & variable == @var").to_dict("records")[0]
                for var in gm_vars
            ]
            source_cat_dict = dict(zip(gm_vars, gm_params))

            data = ClimRCatData(
                source_cat_dict=source_cat_dict,
                target_gdf=target_polygons,
                target_id="poly_id",
                source_time_period=["2019-01-01", "2021-12-31"]
            )

    """

    _deprecation_map = {  # noqa: RUF012
        "cat_dict": "source_cat_dict",
        "f_feature": "target_gdf",
        "id_feature": "target_id",
        "period": "source_time_period",
    }

    @deprecate_kwargs(_deprecation_map, removed_in="1.0.0")
    def __init__(  # noqa: D417
        self: "ClimRCatData",
        *,
        source_cat_dict: dict[str, dict[str, Any]],
        target_gdf: Union[str, Path, gpd.GeoDataFrame],
        target_id: str,
        source_time_period: list[Union[str, pd.Timestamp, datetime.datetime] | None],
        **kwargs,  # noqa: ANN003
    ) -> None:  # sourcery skip: simplify-len-comparison
        """Initialize ClimRCatData for Climate-R catalog integration.

        Sets up data access for Climate-R catalog datasets with automatic metadata
        handling, coordinate system detection, and spatial/temporal validation.

        Args:
            source_cat_dict: Dictionary mapping variable names to Climate-R catalog
                metadata dictionaries. Each entry should contain the complete catalog
                record for a variable, including URL, coordinate names, CRS, and
                temporal information.
            target_gdf: GeoDataFrame containing target geometries, or path to a
                shapefile/GeoPackage that can be read by geopandas.
            target_id: Column name in target_gdf to use as unique identifier for
                geometries in weight calculations and aggregations.
            source_time_period: Two-element list defining the temporal range for
                data subsetting. Format: ["YYYY-MM-DD", "YYYY-MM-DD"] or
                ["YYYY-MM-DD HH:MM:SS", "YYYY-MM-DD HH:MM:SS"].

        Raises:
            KeyError: If target_id is not found in target_gdf columns.
            ValueError: If source_cat_dict is empty or contains invalid entries.
            TypeError: If catalog entries are missing required metadata fields.

        Notes:
            The catalog dictionary structure should match the Climate-R catalog
            format with fields like 'URL', 'X_name', 'Y_name', 'T_name', 'crs',
            'toptobottom', etc. Invalid or incomplete entries will raise errors
            during initialization.

        Examples:
            Initialize with TerraClimate data:

            .. code-block:: python

                import pandas as pd

                cat_url = (
                    "https://github.com/mikejohnson51/climateR-catalogs/releases/download/June-2024/catalog.parquet"
                )
                cat = pd.read_parquet(cat_url)

                # Create catalog entry for actual evapotranspiration
                aet_params = (
                    cat.query("id == 'terraclim' & variable == 'aet'").to_dict("records")[0]
                )
                source_cat_dict = {"aet": aet_params}

                data = ClimRCatData(
                    source_cat_dict=source_cat_dict,
                    target_gdf="watersheds.shp",
                    target_id="huc12",
                    source_time_period=["2020-01-01", "2020-12-31"],
                )

        """
        logger.info("Initializing ClimRCatData")
        logger.info("  - loading data")
        self.source_cat_dict = source_cat_dict
        self.target_gdf = target_gdf
        self.target_id = target_id
        self.source_time_period = _process_period(source_time_period)
        self._check_input_dict()
        self._gdf = _read_shp_file(self.target_gdf)
        if self.target_id not in self._gdf.columns:
            # print(
            #     f"target_id {self.target_id} not in target_gdf columns: "
            #     f" {self._gdf.columns}"
            # )
            raise KeyError(f"target_id {self.target_id} not in target_gdf columns:  {self._gdf.columns}")
        self.target_crs = self._gdf.crs
        self._check_id_feature()
        self._keys = self.get_vars()
        cat_cr = self._create_climrcats(key=self._keys[0])

        logger.info("  - checking latitude bounds")
        is_intersect, is_degrees, is_0_360 = _check_for_intersection(
            cat_cr=cat_cr, gdf=self._gdf
        )  # Project the gdf to the crs of the gridded data
        self._gdf, self._gdf_bounds = _get_shp_file(shp_file=self._gdf, cat_cr=cat_cr, is_degrees=is_degrees)
        self._rotate_ds = bool((not is_intersect) & is_degrees & (is_0_360))

    def get_target_crs(self) -> CRS:
        """Get the coordinate reference system of the target geometries.

        Returns:
            CRS: The coordinate reference system of the target vector data.

        """
        return self.target_crs

    def get_source_subset(self, key: str) -> xr.DataArray:
        """Get a spatially and temporally subset of the source data.

        This method uses the metadata from the Climate-R catalog to retrieve
        and subset the data for a specific variable.

        Args:
            key (str): The variable name to subset from the catalog.

        Returns:
            xr.DataArray: A subsetted xarray DataArray.

        """
        cat_cr = self._create_climrcats(key=key)
        return _get_data_via_catalog(
            cat_cr=cat_cr,
            bounds=self._gdf_bounds,
            begin_date=self.source_time_period[0],
            end_date=self.source_time_period[1],
            rotate_lon=self._rotate_ds,
        )

    def prep_interp_data(self, key: str, poly_id: Union[str, int]) -> AggData:
        """Prep AggData from ClimRCatData.

        Args:
            key (str): Name of the xarray gridded data variable.
            poly_id (Union[str, int]): ID number of the geodataframe geometry to clip the
                gridded data to.

        Returns:
            AggData: An instance of the AggData class, ready for interpolation.

        """
        cat_cr = self._create_climrcats(key=key)

        # Select a feature and make sure it remains a geodataframe
        target_gdf = self._gdf[self._gdf[self.target_id] == poly_id]

        # Clip grid by x, y and time
        ds_ss = _get_data_via_catalog(
            cat_cr=cat_cr,
            bounds=self._gdf_bounds,
            begin_date=self.source_time_period[0],
            end_date=self.source_time_period[1],
            rotate_lon=self._rotate_ds,
        )

        return AggData(
            variable=key,
            cat_cr=cat_cr,
            da=ds_ss,
            target_gdf=target_gdf,
            target_id=self.target_id,
            source_time_period=self.source_time_period,
        )

    def prep_agg_data(self, key: str) -> AggData:
        """Prepare ClimRCatData data for aggregation methods.

        Args:
            key (str): The variable name to prepare for aggregation.

        Returns:
            AggData: An AggData instance ready for aggregation.

        """
        cat_cr = self._create_climrcats(key=key)

        target_gdf = self._gdf

        ds_ss = _get_data_via_catalog(
            cat_cr=cat_cr,
            bounds=self._gdf_bounds,
            begin_date=self.source_time_period[0],
            end_date=self.source_time_period[1],
            rotate_lon=self._rotate_ds,
        )

        return AggData(
            variable=key,
            cat_cr=cat_cr,
            da=ds_ss,
            target_gdf=target_gdf,
            target_id=self.target_id,
            source_time_period=self.source_time_period,
        )

    def prep_wght_data(self) -> WeightData:
        """Prepare data for weight generation calculations.

        Returns:
            WeightData: Data required for calculating spatial intersection
            weights between source and target geometries.

        """
        cat_cr = self._create_climrcats(key=self._keys[0])
        ds_ss = _get_data_via_catalog(
            cat_cr=cat_cr,
            bounds=self._gdf_bounds,
            begin_date=self.source_time_period[0],
            end_date=self.source_time_period[1],
            rotate_lon=self._rotate_ds,
        )
        tsrt = time.perf_counter()
        gdf_grid = _get_cells_poly(
            xr_a=ds_ss,
            x=cat_cr.X_name,
            y=cat_cr.Y_name,
            crs_in=cat_cr.crs,
        )
        tend = time.perf_counter()
        print(f"grid cells generated in {tend - tsrt:0.4f} seconds")

        return WeightData(target_gdf=self._gdf, target_id=self.target_id, grid_cells=gdf_grid)

    def get_feature_id(self) -> str:
        """Return target_id."""
        return self.target_id

    def get_vars(self) -> list[str]:
        """Return list of source_cat_dict keys, proxy for varnames."""
        return list(self.source_cat_dict.keys())

    def _check_input_dict(self: "ClimRCatData") -> None:
        """Check input source_cat_dict for content."""
        if len(self.source_cat_dict) < 1:
            raise ValueError("source_cat_dict should have at least 1 key,value pair")

    def _check_id_feature(self: "ClimRCatData") -> None:
        """Check if target_id is in the GeoDataFrame columns."""
        if self.target_id not in self._gdf.columns[:]:
            raise ValueError(f"shp_poly_idx: {self.target_id} not in gdf columns: {self._gdf.columns}")

    def get_class_type(self) -> str:
        """Get the type identifier for this data source class."""
        return "ClimRCatData"

    def _create_climrcats(self: "ClimRCatData", key: str) -> CatClimRItem:
        """Create a CatClimRItem instance from the catalog dictionary.

        Args:
            key (str): The variable key to look up in the source catalog dictionary.

        Returns:
            CatClimRItem: A dataclass instance containing the metadata for the variable.

        """
        return CatClimRItem(**self.source_cat_dict[key])


class UserCatData(UserData):
    """Handler for user-provided xarray datasets with custom configuration.

    This class provides a flexible interface for working with user-supplied gridded
    datasets that are not available through catalogs. It handles xarray datasets
    from local files, URLs, or in-memory objects, with full control over coordinate
    names, variable selection, and coordinate reference systems.

    The class performs comprehensive validation of input parameters and data
    compatibility, ensuring that coordinate names exist, variables are available,
    and coordinate reference systems are valid.

    Attributes:
        source_ds: The source xarray Dataset containing gridded data.
        target_gdf: GeoDataFrame containing target geometries.
        target_id: Column name for unique identifiers in target geometries.
        source_time_period: Processed time period for temporal subsetting.

    Examples:
        Basic usage with local NetCDF file:

        .. code-block:: python

            import xarray as xr
            from gdptools.data.user_data import UserCatData

            # Load custom dataset
            ds = xr.open_dataset("climate_data.nc")

            data = UserCatData(
                source_ds=ds,
                source_crs=4326,
                source_x_coord="longitude",
                source_y_coord="latitude",
                source_t_coord="time",
                source_var=["temperature", "precipitation"],
                target_gdf="watersheds.shp",
                target_crs=4326,
                target_id="huc12",
                source_time_period=["2020-01-01", "2020-12-31"]
            )

        Using URL data source:

        .. code-block:: python

            # Remote dataset
            data = UserCatData(
                source_ds="https://example.com/climate.nc",
                source_crs="EPSG:4326",
                source_x_coord="lon",
                source_y_coord="lat",
                source_t_coord="time",
                source_var="temperature",
                target_gdf=polygons_gdf,
                target_crs=3857,
                target_id="poly_id",
                source_time_period=["2019-01-01", "2021-12-31"]
            )

        Multiple variables with different CRS:

        .. code-block:: python

            # Projected dataset
            data = UserCatData(
                source_ds="projected_data.nc",
                source_crs=3857,  # Web Mercator
                source_x_coord="x",
                source_y_coord="y",
                source_t_coord="time",
                source_var=["var1", "var2", "var3"],
                target_gdf="regions.gpkg",
                target_crs=4326,
                target_id="region_id",
                source_time_period=["2020-06-01", "2020-08-31"]
            )

    """

    _deprecation_map = {  # noqa: RUF012
        "ds": "source_ds",
        "proj_ds": "source_crs",
        "x_coord": "source_x_coord",
        "y_coord": "source_y_coord",
        "t_coord": "source_t_coord",
        "var": "source_var",
        "f_feature": "target_gdf",
        "proj_feature": "target_crs",
        "id_feature": "target_id",
        "period": "source_time_period",
    }

    @deprecate_kwargs(_deprecation_map, removed_in="1.0.0")
    def __init__(
        self: "UserCatData",
        *,
        source_ds: Union[str, xr.Dataset],
        source_crs: str | int | CRS,
        source_x_coord: str,
        source_y_coord: str,
        source_t_coord: str,
        source_var: Union[str, list[str]],
        target_gdf: Union[str, Path, gpd.GeoDataFrame],
        target_crs: str | int | CRS,
        target_id: str,
        source_time_period: list[Union[str, pd.Timestamp, datetime.datetime] | None],
    ) -> None:
        """Initialize UserCatData for custom gridded datasets.

        Sets up data access for user-provided xarray datasets with comprehensive
        validation of coordinates, variables, and coordinate reference systems.

        Args:
            source_ds: Source dataset as xarray Dataset, file path, or URL.
                Can be any data source readable by xarray.open_dataset().
            source_crs: Coordinate reference system for the source dataset.
                Can be EPSG code, proj4 string, WKT, or pyproj CRS object.
            source_x_coord: Name of the x-coordinate dimension in source_ds.
                Must exist in dataset coordinates.
            source_y_coord: Name of the y-coordinate dimension in source_ds.
                Must exist in dataset coordinates.
            source_t_coord: Name of the time coordinate dimension in source_ds.
                Must exist in dataset coordinates.
            source_var: Variable name(s) to use for processing. Can be a single
                string or list of strings. All variables must exist in source_ds.
            target_gdf: Target geometries as GeoDataFrame or file path.
                Can be any format readable by geopandas.read_file().
            target_crs: Coordinate reference system for target geometries.
                Can be EPSG code, proj4 string, WKT, or pyproj CRS object.
            target_id: Column name in target_gdf to use as unique identifier.
                Must exist in target_gdf columns.
            source_time_period: Two-element list defining temporal range.
                Format: ["YYYY-MM-DD", "YYYY-MM-DD"] or with time stamps.

        Raises:
            KeyError: If target_id is not in target_gdf columns, or if coordinate
                names or variables are not found in the dataset.
            ValueError: If source_crs or target_crs are invalid CRS specifications.
            FileNotFoundError: If source_ds or target_gdf file paths don't exist.

        Note:
            This class performs extensive validation upon initialization, including
            checking for the existence of specified coordinates and variables,
            validating CRS definitions, and ensuring the target ID exists in the
            geometries.

        Examples:
            Initialize with local NetCDF file:

            .. code-block:: python

                import xarray as xr
                data = UserCatData(
                    source_ds="temperature_data.nc",
                    source_crs=4326,
                    source_x_coord="longitude",
                    source_y_coord="latitude",
                    source_t_coord="time",
                    source_var=["temperature"],
                    target_gdf="watersheds.shp",
                    target_crs=4326,
                    target_id="huc12",
                    source_time_period=["2020-01-01", "2020-12-31"]
                )

            Initialize with in-memory dataset:

            .. code-block:: python

                ds = xr.open_dataset("climate.nc")
                data = UserCatData(
                    source_ds=ds,
                    source_crs="EPSG:4326",
                    source_x_coord="lon",
                    source_y_coord="lat",
                    source_t_coord="time",
                    source_var=["temp", "precip"],
                    target_gdf=polygons_gdf,
                    target_crs=3857,
                    target_id="poly_id",
                    source_time_period=["2019-01-01", "2021-12-31"]
                )

        """
        logger.info("Initializing UserCatData")
        logger.info("  - loading data")
        self.source_ds = _get_xr_dataset(ds=source_ds)
        self.target_id = target_id
        self.target_gdf = _read_shp_file(shp_file=target_gdf)

        # Validate target_id exists in target_gdf
        if self.target_id not in self.target_gdf.columns:
            print(f"target_id {self.target_id} not in target_gdf columns: {self.target_gdf.columns}")
            raise KeyError(
                f"target_id '{self.target_id}' not found in target_gdf columns: {list(self.target_gdf.columns)}"
            )

        # Validate source CRS
        if not _is_valid_crs(source_crs):
            raise ValueError(
                f"Invalid CRS specification: {source_crs!r}. "
                "Please provide a valid CRS (e.g., EPSG code, proj string, WKT, or pyproj.CRS object)."
            )

        # Validate target CRS
        if not _is_valid_crs(target_crs):
            raise ValueError(
                f"Invalid target CRS specification: {target_crs!r}. "
                "Please provide a valid CRS (e.g., EPSG code, proj string, WKT, or pyproj.CRS object)."
            )

        # Validate coordinate names exist in dataset
        if source_x_coord not in self.source_ds.coords:
            raise KeyError(
                f"X coordinate '{source_x_coord}' not found in dataset coordinates: {list(self.source_ds.coords.keys())}"  # noqa: E501
            )

        if source_y_coord not in self.source_ds.coords:
            raise KeyError(
                f"Y coordinate '{source_y_coord}' not found in dataset coordinates: {list(self.source_ds.coords.keys())}"  # noqa: E501
            )

        if source_t_coord not in self.source_ds.coords:
            raise KeyError(
                f"Time coordinate '{source_t_coord}' not found in dataset coordinates: {list(self.source_ds.coords.keys())}"  # noqa: E501
            )

        # Validate and process source variables
        source_var_list = source_var if isinstance(source_var, list) else [source_var]

        # Check for empty variable list
        if not source_var_list:
            raise ValueError("source_var cannot be empty. Please provide at least one variable name.")

        # Validate each variable exists in dataset
        missing_vars = []
        if missing_vars := [var for var in source_var_list if var not in self.source_ds.data_vars]:
            raise KeyError(
                f"Variables {missing_vars} not found in dataset data variables: {list(self.source_ds.data_vars.keys())}"
            )

        self.source_var = source_var_list

        # Validate and process time period
        try:
            self.source_time_period = _process_period(source_time_period)
        except (ValueError, TypeError, pd.errors.ParserError) as e:
            raise ValueError(  # noqa: B904
                f"Invalid time period specification: {source_time_period}. "
                f"Please provide valid date strings (e.g., 'YYYY-MM-DD'). Error: {e}"
            )

        # Set remaining attributes
        self.source_crs = source_crs
        self.source_x_coord = source_x_coord
        self.source_y_coord = source_y_coord
        self.source_t_coord = source_t_coord
        self.target_crs = target_crs

        self._gdf_bounds = _get_shp_bounds_w_buffer(
            gdf=self.target_gdf,
            ds=self.source_ds,
            crs=self.source_crs,
            lon=self.source_x_coord,
            lat=self.source_y_coord,
        )
        logger.info("  - checking latitude bounds")
        is_intersect, is_degrees, is_0_360 = _check_for_intersection_nc(
            ds=self.source_ds,
            x_name=self.source_x_coord,
            y_name=self.source_y_coord,
            proj=self.source_crs,
            gdf=self.target_gdf,
        )

        if bool((not is_intersect) & is_degrees & (is_0_360)):  # rotate
            logger.info("  - rotating into -180 - 180")
            self.source_ds.coords[self.source_x_coord] = (self.source_ds.coords[self.source_x_coord] + 180) % 360 - 180
            self.source_ds = self.source_ds.sortby(self.source_ds[self.source_x_coord])

        # calculate toptobottom (order of latitude coords)
        self._ttb = _get_top_to_bottom(self.source_ds, self.source_y_coord)
        logger.info("  - getting gridded data subset")
        self._agg_subset_dict = build_subset(
            bounds=self._gdf_bounds,
            xname=self.source_x_coord,
            yname=self.source_y_coord,
            tname=self.source_t_coord,
            toptobottom=self._ttb,
            date_min=self.source_time_period[0],
            date_max=self.source_time_period[1],
        )

    @classmethod
    def __repr__(cls) -> str:
        """Print class name."""
        return f"Class is {cls.__name__}"

    def get_target_crs(self) -> str | int | CRS:
        """Return the coordinate reference system (CRS) for the source data.

        This method provides the CRS used by the target geometries.

        Returns:
            str | int | CRS: The CRS associated with the target geometries.

        """
        return self.target_crs

    def get_source_subset(self, key: str) -> xr.DataArray:
        """Get a spatially and temporally subset of the source dataset.

        This method applies the pre-calculated spatial and temporal subset
        dictionary to the source dataset for the given variable.

        Args:
            key (str): Name of the xarray gridded data variable.

        Returns:
            xr.DataArray: A subsetted xarray DataArray of the original source gridded data.

        """
        return self.source_ds[key].sel(**self._agg_subset_dict)

    def get_feature_id(self) -> str:
        """Return target_id."""
        return self.target_id

    def get_vars(self) -> list[str]:
        """Return list of vars in data."""
        return self.source_var

    def get_class_type(self) -> str:
        """Get the type identifier for this data source class."""
        return "UserCatData"

    def prep_interp_data(self, key: str, poly_id: Union[str, int]) -> AggData:
        """Prep AggData from UserCatData.

        Args:
            key (str): Name of the xarray gridded data variable.
            poly_id (Union[str, int]): ID number of the geodataframe geometry to clip the
                gridded data to.

        Returns:
            AggData: An instance of the AggData class, ready for interpolation.

        """
        # Open grid and clip to geodataframe and time window
        data_ss: xr.DataArray = self.source_ds[key].sel(**self._agg_subset_dict)  # type: ignore

        # Select a feature and make sure it remains a geodataframe
        target_gdf = self.target_gdf[self.target_gdf[self.target_id] == poly_id]

        # Reproject the feature to grid crs and get a buffered bounding box
        bounds = _get_shp_bounds_w_buffer(
            gdf=target_gdf,
            ds=self.source_ds,
            crs=self.source_crs,
            lon=self.source_x_coord,
            lat=self.source_y_coord,
        )

        # Clip grid to time window and line geometry bbox buffer
        ss_dict = build_subset(
            bounds=bounds,
            xname=self.source_x_coord,
            yname=self.source_y_coord,
            tname=self.source_t_coord,
            toptobottom=self._ttb,
            date_min=str(self.source_time_period[0]),
            date_max=str(self.source_time_period[1]),
        )

        ds_ss = data_ss.sel(**ss_dict)
        cat_cr = self._create_climrcats(key=key, da=ds_ss)

        return AggData(
            variable=key,
            cat_cr=cat_cr,
            da=ds_ss,
            target_gdf=target_gdf,
            target_id=self.target_id,
            source_time_period=self.source_time_period,
        )

    def prep_agg_data(self, key: str) -> AggData:
        """Prepare data for aggregation operations.

        This method subsets the source dataset based on the pre-calculated
        spatial and temporal bounds and prepares an AggData object.

        Args:
            key (str): The variable name to prepare for aggregation.

        Returns:
            An AggData instance ready for aggregation.

        """
        logger.info("Agg Data preparation - beginning")
        data_ss: xr.DataArray = self.source_ds[key].sel(**self._agg_subset_dict)  # type: ignore
        target_gdf = self.target_gdf
        cat_cr = self._create_climrcats(key=key, da=data_ss)

        logger.info("  - returning AggData")
        return AggData(
            variable=key,
            cat_cr=cat_cr,
            da=data_ss,
            target_gdf=target_gdf,
            target_id=self.target_id,
            source_time_period=self.source_time_period,
        )

    def _create_climrcats(self: "UserCatData", key: str, da: xr.DataArray) -> CatClimRItem:
        """Create a CatClimRItem instance from the user-provided metadata.

        Args:
            key (str): The variable name.
            da (xr.DataArray): The DataArray for the variable, used to extract metadata.

        Returns:
            CatClimRItem: A dataclass instance containing the metadata.

        """
        return CatClimRItem(
            # id=self.id,
            URL="",
            varname=key,
            long_name=str(self._get_ds_var_attrs(da, "long_name")),
            T_name=self.source_t_coord,
            units=str(self._get_ds_var_attrs(da, "units")),
            X_name=self.source_x_coord,
            Y_name=self.source_y_coord,
            proj=str(self.source_crs),
            resX=max(np.diff(da[self.source_x_coord].values)),
            resY=max(np.diff(da[self.source_y_coord].values)),
            toptobottom=str(_get_top_to_bottom(da, self.source_y_coord)),
        )

    def _get_ds_var_attrs(self, da: xr.DataArray, attr: str) -> Any:  # noqa: ANN401
        """Return source_var attributes.

        Args:
            da (xr.DataArray): The DataArray to inspect.
            attr (str): The attribute name to retrieve.

        Returns:
            Any: The value of the attribute, or "None" if not found.

        """
        try:
            return da.attrs.get(attr)
        except KeyError:
            return "None"

    def prep_wght_data(self) -> WeightData:
        """Prepare data for weight generation calculations.

        This method subsets the source dataset and generates grid cell polygons
        required for calculating spatial intersection weights.

        Returns:
            WeightData: Data required for weight generation.

        """
        logger.info("Weight Data preparation - beginning")
        try:
            data_ss_wght = self.source_ds.sel(**self._agg_subset_dict)  # type: ignore
        except KeyError as e:
            if self.source_t_coord in str(e):
                example_time = self.source_ds[self.source_t_coord].values[0]
                new_message = (
                    f"The source data time coordinate is formatted as {example_time}, you specified time as"
                    f"{self.source_time_period[0]}. For non-standard time formats, Use a string to specify a time source_time_period that"  # noqa: E501
                    "matches the time format in the source data"
                )
                raise KeyError(new_message) from e

        logger.info("  - calculating grid-cell polygons")
        start = time.perf_counter()
        grid_poly = _get_cells_poly(
            xr_a=data_ss_wght,
            x=self.source_x_coord,
            y=self.source_y_coord,
            crs_in=self.source_crs,
        )
        end = time.perf_counter()
        print(f"Generating grid-cell polygons finished in {round(end - start, 2)} second(s)")
        logger.info(f"Generating grid-cell polygons finished in {round(end - start, 2)} second(s)")
        return WeightData(target_gdf=self.target_gdf, target_id=self.target_id, grid_cells=grid_poly)


class NHGFStacData(UserData):
    """Interface for NHGF STAC catalog datasets with spatiotemporal filtering.

    This class provides access to datasets through the NHGF STAC (SpatioTemporal
    Asset Catalog) system, enabling federated data access with automatic
    spatiotemporal filtering and metadata handling.

    The class integrates with STAC-compliant data catalogs to provide seamless
    access to large-scale gridded datasets with built-in spatial and temporal
    subsetting capabilities.

    Attributes:
        source_collection: STAC collection identifier for the dataset.
        source_var: Variable name(s) to access from the collection.
        target_gdf: GeoDataFrame containing target geometries.
        target_id: Column name for unique identifiers in target geometries.
        source_time_period: Processed time period for temporal filtering.

    Examples:
        Basic STAC usage:

        .. code-block:: python

            from gdptools.data.user_data import NHGFStacData

            # Access CONUS404 dataset
            data = NHGFStacData(
                source_collection="conus404-hourly-cloud-optimized",
                source_var=["T2", "PRCP"],
                target_gdf="watersheds.shp",
                target_id="huc12",
                source_time_period=["2020-01-01", "2020-01-31"]
            )

            # Access variables
            variables = data.get_vars()
            subset = data.get_source_subset("T2")

        Single variable access:

        .. code-block:: python

            data = NHGFStacData(
                source_collection="daymet-daily-na",
                source_var="tmax",
                target_gdf=regions_gdf,
                target_id="region_id",
                source_time_period=["2019-01-01", "2019-12-31"]
            )

    Note:
        This class requires access to the NHGF STAC catalog endpoints and
        appropriate authentication for restricted datasets.

    """

    _deprecation_map = {  # noqa: RUF012
        "collection": "source_collection",
        "var": "source_var",
        "f_feature": "target_gdf",
        "id_feature": "target_id",
        "period": "source_time_period",
    }

    @deprecate_kwargs(_deprecation_map, removed_in="1.0.0")
    def __init__(
        self,
        *,
        source_collection,  # noqa: ANN001
        source_var: Union[str, list[str]],
        target_gdf: Union[str, Path, gpd.GeoDataFrame],
        target_id: str,
        source_time_period: list[Union[str, pd.Timestamp, datetime.datetime] | None],
    ) -> None:
        """Initialize NHGFStacData class.

        This class is meant to read in gridded datasets from the National Hydrologic Geospatail Fabric (NHGF)
        Spatio-Temporal Asset Catalog (STAC) available here:

        https://api.water.usgs.gov/gdp/pygeoapi/stac/stac-collection/

        The STAC is accessed and queried with the pystac Python package.

        Args:
            source_collection: STAC collection object for the dataset.
            source_var (Union[str, list[str]]): Variable name(s) to be used in aggregation.
            target_gdf (Union[str, Path, gpd.GeoDataFrame]): GeoDataFrame or path/URL readable by geopandas.
            target_id (str): Column name in target_gdf containing unique identifiers.
            source_time_period (list[str]): Two-element list defining start and end date
                ('YYYY-MM-DD' or with time), matching the dataset's time coordinate format.

        Raises:
            KeyError: If target_id is not in target_gdf columns.

        """
        logger.info("Initializing NHGFStacData")
        logger.info("  - loading data")
        self.id = source_collection.id
        self.asset = source_collection.assets["zarr-s3-osn"]
        # self.source_ds = xr.open_dataset(self.asset)
        self.source_ds = xr.open_zarr(
            self.asset.href,
            storage_options=self.asset.extra_fields["xarray:storage_options"],
        )
        self.target_id = target_id
        self.target_gdf = target_gdf
        self._gdf = _read_shp_file(self.target_gdf)
        if self.target_id not in self._gdf.columns:
            logger.error(f"target_id {self.target_id} not in target_gdf columns:  {self._gdf.columns}")
            raise KeyError(f"target_id {self.target_id} not in target_gdf columns:  {self._gdf.columns}")
        self.source_time_period = source_time_period
        self.source_var = source_var if isinstance(source_var, list) else [source_var]
        # Ensure gridded data has proper dimensions
        # check_gridded_data_for_dimensions(self.ds, self.source_var)
        self.target_crs = self._gdf.crs
        self.source_crs = self.source_ds.crs.attrs["crs_wkt"]
        if type(CRS.from_string(self.source_crs)) is not CRS:
            logger.error("Projection of the gridded dataset could not be identified")

        self.source_x_coord = "x"
        self.source_y_coord = "y"
        self.source_t_coord = "time"

        self._gdf_bounds = _get_shp_bounds_w_buffer(
            gdf=self._gdf,
            ds=self.source_ds,
            crs=self.source_crs,
            lon=self.source_x_coord,
            lat=self.source_y_coord,
        )
        logger.info("  - checking latitude bounds")
        is_intersect, is_degrees, is_0_360 = _check_for_intersection_nc(
            ds=self.source_ds,
            x_name=self.source_x_coord,
            y_name=self.source_y_coord,
            proj=self.source_crs,
            gdf=self._gdf,
        )

        if bool((not is_intersect) & is_degrees & (is_0_360)):  # rotate
            logger.info("  - rotating into -180 - 180")
            self.source_ds.coords[self.source_x_coord] = (self.source_ds.coords[self.source_x_coord] + 180) % 360 - 180
            self.source_ds = self.source_ds.sortby(self.source_ds[self.source_x_coord])

        # calculate toptobottom (order of latitude coords)
        self._ttb = _get_top_to_bottom(self.source_ds, self.source_y_coord)
        logger.info("  - getting gridded data subset")
        self._weight_subset_dict = build_subset(
            bounds=self._gdf_bounds,
            xname=self.source_x_coord,
            yname=self.source_y_coord,
            tname=self.source_t_coord,
            toptobottom=self._ttb,
            date_min=self.source_time_period[0],
        )
        self._agg_subset_dict = build_subset(
            bounds=self._gdf_bounds,
            xname=self.source_x_coord,
            yname=self.source_y_coord,
            tname=self.source_t_coord,
            toptobottom=self._ttb,
            date_min=self.source_time_period[0],
            date_max=self.source_time_period[1],
        )

    @classmethod
    def __repr__(cls) -> str:
        """Print class name."""
        return f"Class is {cls.__name__}"

    def get_target_crs(self) -> str | int | CRS:
        """Return the coordinate reference system (CRS) for the source data.

        This method provides the CRS used by the source dataset.

        Returns:
            str | int | CRS: The CRS associated with the source data.

        """
        return self.target_crs

    def get_source_subset(self, key: str) -> xr.DataArray:
        """Get a subset of the STAC data source for a specific variable.

        This method applies the pre-calculated spatial and temporal subset
        dictionary to the STAC dataset for the given variable.

        Args:
            key (str): Name of the variable to subset.

        Returns:
            xr.DataArray: Subsetted dataarray.

        """
        return self.source_ds[key].sel(**self._agg_subset_dict)

    def get_feature_id(self) -> str:
        """Return target_id."""
        return self.target_id

    def get_vars(self) -> list[str]:
        """Return list of vars in data."""
        return self.source_var

    def get_class_type(self) -> str:
        """Abstract method for returning the type of the data class."""
        return "NHGFStacData"

    def prep_interp_data(self, key: str, poly_id: Union[str, int]) -> AggData:
        """Prep AggData from NHGFStacData.

        Args:
            key (str): Name of the xarray gridded data variable.
            poly_id (Union[str, int]): ID number of the geodataframe geometry to clip the
                gridded data to.

        Returns:
            AggData: An instance of the AggData class, ready for interpolation.

        """
        # Open grid and clip to geodataframe and time window
        data_ss = self.get_source_subset(key)
        cat_cr = self._create_climrcats(key=key, da=data_ss)

        # Select a feature and make sure it remains a geodataframe
        target_gdf = self._gdf[self._gdf[self.target_id] == poly_id]

        return AggData(
            variable=key,
            cat_cr=cat_cr,
            da=data_ss,
            target_gdf=target_gdf,
            target_id=self.target_id,
            source_time_period=self.source_time_period,
        )

    def prep_agg_data(self, key: str) -> AggData:
        """Prep AggData from UserData."""
        logger.info("Agg Data preparation - beginning")
        data_ss: xr.DataArray = self.get_source_subset(key)
        cat_cr = self._create_climrcats(key=key, da=data_ss)
        target_gdf = self._gdf
        # If the time dimension has only one step:
        try:
            data_ss.coords.get(self.source_t_coord).all()
            source_time_period = self.source_time_period
        except Exception:
            source_time_period = ["None", "None"]

        logger.info("  - returning AggData")
        return AggData(
            variable=key,
            cat_cr=cat_cr,
            da=data_ss,
            target_gdf=target_gdf,
            target_id=self.target_id,
            source_time_period=source_time_period,
        )

    def _create_climrcats(self: "NHGFStacData", key: str, da: xr.DataArray) -> CatClimRItem:
        """Create a CatClimRItem instance from STAC metadata.

        Args:
            key (str): The variable name.
            da (xr.DataArray): The DataArray for the variable, used to extract metadata.

        Returns:
            CatClimRItem: A dataclass instance containing the metadata.

        """
        return CatClimRItem(
            # id=self.id,
            URL=self.asset.href,
            varname=key,
            long_name=str(self._get_ds_var_attrs(da, "description")),
            T_name=self.source_t_coord,
            units=str(self._get_ds_var_attrs(da, "units")),
            X_name=self.source_x_coord,
            Y_name=self.source_y_coord,
            proj=str(self.source_crs),
            resX=max(np.diff(da[self.source_x_coord].values)),
            resY=max(np.diff(da[self.source_y_coord].values)),
            toptobottom=str(_get_top_to_bottom(da, self.source_y_coord)),
        )

    def _get_ds_var_attrs(self, da: xr.DataArray, attr: str) -> Any:  # noqa: ANN401
        """Return source_var attributes.

        Args:
            da (xr.DataArray): Target DataArray to pull attributes from.
            attr (str): Name of the attribute to return.

        Returns:
            The value of the attribute, or "None" if not found.

        """
        try:
            return da.attrs.get(attr)
        except KeyError:
            return "None"

    def prep_wght_data(self) -> WeightData:
        """Prepare and return WeightData for weight generation."""
        logger.info("Weight Data preparation - beginning")
        data_ss_wght = self.source_ds.sel(**self._weight_subset_dict)  # type: ignore
        logger.info("  - calculating grid-cell polygons")
        start = time.perf_counter()
        grid_poly = _get_cells_poly(
            xr_a=data_ss_wght,
            x=self.source_x_coord,
            y=self.source_y_coord,
            crs_in=self.source_crs,
        )
        end = time.perf_counter()
        print(f"Generating grid-cell polygons finished in {round(end - start, 2)} second(s)")
        logger.info(f"Generating grid-cell polygons finished in {round(end - start, 2)} second(s)")
        return WeightData(target_gdf=self._gdf, target_id=self.target_id, grid_cells=grid_poly)


class UserTiffData(UserData):
    """Handler for GeoTIFF and other raster data sources.

    This class is optimized for working with raster data sources such as GeoTIFF
    files, providing specialized functionality for zonal statistics and spatial
    analysis operations. It handles single and multi-band rasters with automatic
    band selection and coordinate system validation.

    The class is particularly useful for processing elevation data, land cover
    classifications, and other raster datasets that require zonal statistics
    calculations over vector geometries.

    Attributes:
        source_ds: The source raster data as xarray DataArray or Dataset.
        target_gdf: GeoDataFrame containing target geometries for zonal operations.
        target_id: Column name for unique identifiers in target geometries.
        band: Selected band number for multi-band rasters.
        source_var: Variable name assigned to the raster data.

    Examples:
        Basic elevation processing:

        .. code-block:: python

            from gdptools.data.user_data import UserTiffData

            # Process elevation data
            data = UserTiffData(
                source_ds="elevation.tif",
                source_crs=4326,
                source_x_coord="x",
                source_y_coord="y",
                target_gdf="watersheds.shp",
                target_id="huc12"
            )

            # Prepare for zonal statistics
            weight_data = data.prep_wght_data()

        Multi-band raster processing:

        .. code-block:: python

            # Select specific band from multi-band raster
            data = UserTiffData(
                source_ds="landcover.tif",
                source_crs=3857,
                source_x_coord="x",
                source_y_coord="y",
                target_gdf=polygons_gdf,
                target_id="poly_id",
                band=3,  # Select band 3
                source_var="landcover_class"
            )

        In-memory raster data:

        .. code-block:: python

            import rioxarray as rxr
            raster = rxr.open_rasterio("slope.tif")
            data = UserTiffData(
                source_ds=raster,
                source_crs=raster.rio.crs,
                source_x_coord="x",
                source_y_coord="y",
                target_gdf="regions.gpkg",
                target_id="region_id"
            )

    Notes:
        This class automatically handles band selection and coordinate system
        validation for raster data. It's optimized for zonal statistics workflows
        and integrates seamlessly with the ZonalGen classes.

    """

    _deprecation_map = {  # noqa: RUF012
        "ds": "source_ds",
        "proj_ds": "source_crs",
        "x_coord": "source_x_coord",
        "y_coord": "source_y_coord",
        "t_coord": "source_t_coord",
        "var": "source_var",
        "f_feature": "target_gdf",
        "proj_feature": "target_crs",
        "id_feature": "target_id",
        "period": "source_time_period",
    }

    @deprecate_kwargs(_deprecation_map, removed_in="1.0.0")
    def __init__(
        self,
        source_ds: Union[str, xr.DataArray, xr.Dataset],
        source_crs: str | int | CRS,
        source_x_coord: str,
        source_y_coord: str,
        target_gdf: Union[str, Path, gpd.GeoDataFrame],
        target_id: str,
        bname: str = "band",
        band: int = 1,
        source_var: str = "tiff",
    ) -> None:
        """Initialize UserTiffData for raster data processing.

        Args:
            source_ds: Raster data source as a file path, xarray DataArray,
                or Dataset.
            source_crs: Coordinate reference system of the raster data.
            source_x_coord: Name of the x-coordinate dimension in the raster.
            source_y_coord: Name of the y-coordinate dimension in the raster.
            target_gdf: Target geometries as a GeoDataFrame or file path.
            target_id: Column name in `target_gdf` for unique identifiers.
            bname: Name of the band dimension in multi-band rasters.
                Defaults to "band".
            band: Band number to select from a multi-band raster (1-indexed).
                Defaults to 1.
            source_var: A name to assign to the raster data variable.
                Defaults to "tiff".

        Raises:
            FileNotFoundError: If `source_ds` file path does not exist.
            KeyError: If `target_id` is not found in `target_gdf` columns.
            ValueError: If `source_crs` is invalid or the band number is
                out of range.

        """
        self.varname = source_var  # Need in zonal_engines to convert xarray dataarray to dataset
        self.source_x_coord = source_x_coord
        self.source_y_coord = source_y_coord
        self.bname = bname
        self.band = band
        self.source_ds = _get_rxr_dataset(source_ds)
        if not _is_valid_crs(source_crs):
            raise ValueError(
                f"Invalid CRS specification: {source_crs!r}. "
                "Please provide a valid CRS (e.g., EPSG code, proj string, WKT, or pyproj.CRS object)."
            )
        self.source_crs = source_crs
        self.target_gdf = _read_shp_file(shp_file=target_gdf)

        self.target_id = target_id
        self.target_gdf = self.target_gdf.sort_values(self.target_id).dissolve(by=self.target_id, as_index=False)
        self.target_gdf.reset_index()
        self.target_crs = self.target_gdf.crs.to_epsg()

        self._check_xname()
        self._check_yname()
        self._check_band()
        self._check_crs()
        self._toptobottom = _get_top_to_bottom(data=self.source_ds, y_coord=self.source_y_coord)

    def get_target_crs(self) -> CRS:
        """Get the coordinate reference system of the target geometries.

        Returns:
            CRS: The coordinate reference system of the target vector data.

        """
        return self.target_crs

    def get_source_subset(self, key: str) -> xr.DataArray:
        """Get a spatially subset of the source raster data.

        This method subsets the source raster based on the buffered bounding
        box of the target geometries. The `key` argument is not used for
        this class but is required for interface consistency.

        Args:
            key (str): A placeholder argument for interface consistency.

        Returns:
            xr.DataArray: A spatially subsetted xarray DataArray.

        """
        bb_feature = _get_shp_bounds_w_buffer(
            gdf=self.target_gdf,
            ds=self.source_ds,
            crs=self.source_crs,
            lon=self.source_x_coord,
            lat=self.source_y_coord,
        )

        subset_dict = build_subset_tiff(
            bounds=bb_feature,
            xname=self.source_x_coord,
            yname=self.source_y_coord,
            toptobottom=self._toptobottom,
            bname=self.bname,
            band=self.band,
        )

        return self.source_ds.sel(**subset_dict)  # type: ignore

    def get_vars(self) -> list[str]:
        """Get the list of available variables.

        For `UserTiffData`, this is typically a single variable name assigned
        during initialization.

        Returns:
            list[str]: A list containing the single variable name.

        """
        return [self.source_ds] if isinstance(self.source_ds, str) else [self.varname]

    def get_feature_id(self) -> str:
        """Get the identifier column name for target geometries."""
        return self.target_id

    def prep_wght_data(self) -> WeightData:
        """Prepare data for weight generation.

        Notes:
            This method is not yet implemented for `UserTiffData`. Zonal
            statistics for rasters are handled by `prep_agg_data`.

        """
        pass

    def get_class_type(self) -> str:
        """Get the type identifier for this data source class."""
        return "UserTiffData"

    def prep_interp_data(self, key: str, poly_id: int) -> AggData:
        """Prepare data for interpolation operations.

        This method subsets the source raster data to the bounding box of a
        specific target geometry and prepares an `AggData` object for
        interpolation.

        Args:
            key (str): The variable name to prepare for interpolation.
            poly_id (int): The identifier of the target geometry to use for
                subsetting.

        Returns:
            AggData: An instance ready for interpolation.

        """
        # Select a feature and make sure it remains a geodataframe
        target_gdf = self.target_gdf[self.target_gdf[self.target_id] == poly_id]

        bb_feature = _get_shp_bounds_w_buffer(
            gdf=target_gdf,
            ds=self.source_ds,
            crs=self.source_crs,
            lon=self.source_x_coord,
            lat=self.source_y_coord,
        )

        subset_dict = build_subset_tiff(
            bounds=bb_feature,
            xname=self.source_x_coord,
            yname=self.source_y_coord,
            toptobottom=self._toptobottom,
            bname=self.bname,
            band=self.band,
        )

        data_ss: xr.DataArray = self.source_ds.sel(**subset_dict)  # type: ignore
        cat_cr = self._create_climrcats(key=key, da=data_ss)

        return AggData(
            variable=key,
            cat_cr=cat_cr,
            da=data_ss,
            target_gdf=target_gdf,
            target_id=self.target_id,
            source_time_period=["None", "None"],
        )

    def prep_agg_data(self, key: str) -> AggData:
        """Prepare data for aggregation or zonal statistics.

        This method subsets the source raster data to the buffered bounding
        box of the target geometries and prepares an `AggData` object.

        Args:
            key (str): The variable name to prepare for aggregation.

        Returns:
            AggData: An instance ready for aggregation.

        Raises:
            ValueError: If subsetting the raster results in an empty dataset,
                which can indicate a CRS mismatch or no spatial overlap.

        """
        bb_feature = _get_shp_bounds_w_buffer(
            gdf=self.target_gdf,
            ds=self.source_ds,
            crs=self.source_crs,
            lon=self.source_x_coord,
            lat=self.source_y_coord,
        )

        subset_dict = build_subset_tiff(
            bounds=bb_feature,
            xname=self.source_x_coord,
            yname=self.source_y_coord,
            toptobottom=self._toptobottom,
            bname=self.bname,
            band=self.band,
        )

        data_ss: xr.DataArray = self.source_ds.sel(**subset_dict)  # type: ignore
        if data_ss.size == 0:
            raise ValueError(
                "Sub-setting the raster resulted in no values",
                f"check the specified source_crs value: {self.source_crs}",
                f" and target_crs value: {self.target_crs}",
            )

        cat_cr = self._create_climrcats(key=key, da=data_ss)

        return AggData(
            variable=key,
            cat_cr=cat_cr,
            da=data_ss,
            target_gdf=self.target_gdf.copy(),
            target_id=self.target_id,
            source_time_period=["None", "None"],
        )

    def _check_xname(self: "UserTiffData") -> None:
        """Validate that the x-coordinate name exists in the dataset."""
        if self.source_x_coord not in self.source_ds.coords:
            raise ValueError(f"xname:{self.source_x_coord} not in {self.source_ds.coords}")

    def _check_yname(self: "UserTiffData") -> None:
        """Validate that the y-coordinate name exists in the dataset."""
        if self.source_y_coord not in self.source_ds.coords:
            raise ValueError(f"yname:{self.source_y_coord} not in {self.source_ds.coords}")

    def _check_band(self: "UserTiffData") -> None:
        """Validate that the band coordinate name exists in the dataset."""
        if self.bname not in self.source_ds.coords:
            raise ValueError(f"band:{self.bname} not in {self.source_ds.coords} or {self.source_ds.data_vars}")

    def _check_crs(self: "UserTiffData") -> None:
        """Validate that the source and target CRS are valid."""
        crs = CRS.from_user_input(self.source_crs)
        if not isinstance(crs, CRS):
            raise ValueError(f"ds_proj:{self.source_crs} not in valid")
        crs2 = CRS.from_user_input(self.target_crs)
        if not isinstance(crs2, CRS):
            raise ValueError(f"ds_proj:{self.target_crs} not in valid")

    def _create_climrcats(self: "UserTiffData", key: str, da: xr.DataArray) -> CatClimRItem:
        """Create a CatClimRItem instance from the raster metadata.

        This helper method constructs a `CatClimRItem` object, which is used
        internally to standardize metadata for processing.

        Args:
            key (str): The variable name.
            da (xr.DataArray): The DataArray for the variable, used to extract metadata.

        Returns:
            A `CatClimRItem` instance containing the metadata.

        """
        return CatClimRItem(
            # id=self.id,
            URL="",
            varname=key,
            long_name=str(self._get_ds_var_attrs(da, "description")),
            units=str(self._get_ds_var_attrs(da, "units")),
            X_name=self.source_x_coord,
            Y_name=self.source_y_coord,
            proj=str(self.source_crs),
            resX=max(np.diff(da[self.source_x_coord].values)),
            resY=max(np.diff(da[self.source_y_coord].values)),
            toptobottom=str(_get_top_to_bottom(da, self.source_y_coord)),
        )

    def _get_ds_var_attrs(self: "UserTiffData", da: xr.DataArray, attr: str) -> str:
        """Get a specific attribute from a DataArray.

        Safely retrieves an attribute from the DataArray's `attrs` dictionary.

        Args:
            da (xr.DataArray): The DataArray to inspect.
            attr (str): The attribute name to retrieve.

        Returns:
            The attribute value as a string, or "None" if not found.

        """
        try:
            return str(da.attrs.get(attr))
        except KeyError:
            return "None"
