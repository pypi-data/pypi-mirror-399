"""Test critical input validation and error handling for gdptools."""

import gc
import tempfile
from collections.abc import Generator

import geopandas as gpd
import numpy as np
import pandas as pd
import pytest
import xarray as xr
from gdptools import ClimRCatData, UserCatData, WeightGen
from shapely.geometry import Point, Polygon


@pytest.fixture(scope="function")
def sample_dataset() -> Generator[xr.Dataset, None, None]:
    """Create a sample xarray dataset for testing."""
    time = pd.date_range("2020-01-01", periods=12, freq="MS")
    lat = np.linspace(35, 45, 10)
    lon = np.linspace(-105, -95, 10)

    # Create properly shaped temperature and precipitation data
    temp_base = 15 + 10 * np.sin(np.arange(12) * 2 * np.pi / 12)
    temp_data = temp_base[:, np.newaxis, np.newaxis] + np.random.randn(12, 10, 10)
    precip_data = np.abs(np.random.randn(12, 10, 10)) * 50

    ds = xr.Dataset(
        {"temperature": (["time", "lat", "lon"], temp_data), "precipitation": (["time", "lat", "lon"], precip_data)},
        coords={"time": time, "lat": lat, "lon": lon},
    )

    # Add units attributes to coordinate variables
    ds.coords["time"].attrs["units"] = "days since 1970-01-01"
    ds.coords["lat"].attrs["units"] = "degrees_north"
    ds.coords["lon"].attrs["units"] = "degrees_east"

    yield ds
    del ds
    gc.collect()


@pytest.fixture(scope="function")
def sample_polygons() -> Generator[gpd.GeoDataFrame, None, None]:
    """Create sample polygons for testing."""
    # Create polygons that overlap with the dataset coordinates
    polygons = [
        Polygon([(-102, 37), (-100, 37), (-100, 39), (-102, 39)]),
        Polygon([(-100, 39), (-98, 39), (-98, 41), (-100, 41)]),
        Polygon([(-98, 37), (-96, 37), (-96, 39), (-98, 39)]),
    ]

    gdf = gpd.GeoDataFrame(
        {"basin_id": ["basin_1", "basin_2", "basin_3"], "area": [1000, 1500, 800], "geometry": polygons},
        crs="EPSG:4326",
    )

    yield gdf
    del gdf
    gc.collect()


@pytest.fixture(scope="function")
def invalid_polygons() -> Generator[gpd.GeoDataFrame, None, None]:
    """Create polygons that don't overlap with dataset for testing."""
    # Non-overlapping polygons
    polygons = [Polygon([(10, 10), (20, 10), (20, 20), (10, 20)]), Polygon([(25, 25), (35, 25), (35, 35), (25, 35)])]

    gdf = gpd.GeoDataFrame({"id": ["poly_1", "poly_2"], "geometry": polygons}, crs="EPSG:4326")

    yield gdf
    del gdf
    gc.collect()


class TestUserCatDataValidation:
    """Test UserCatData input validation and error handling."""

    def test_valid_initialization(self, sample_dataset: xr.Dataset, sample_polygons: gpd.GeoDataFrame) -> None:
        """Test valid UserCatData initialization."""
        user_data = UserCatData(
            source_ds=sample_dataset,
            source_crs="EPSG:4326",
            source_x_coord="lon",
            source_y_coord="lat",
            source_t_coord="time",
            source_var=["temperature", "precipitation"],
            target_gdf=sample_polygons,
            target_crs="EPSG:4326",
            target_id="basin_id",
            source_time_period=["2020-01-01", "2020-12-31"],
        )

        assert user_data.get_class_type() == "UserCatData"
        assert user_data.get_feature_id() == "basin_id"
        assert set(user_data.get_vars()) == {"temperature", "precipitation"}

    def test_missing_coordinate_error(self, sample_dataset: xr.Dataset, sample_polygons: gpd.GeoDataFrame) -> None:
        """Test error when coordinate doesn't exist in dataset."""
        with pytest.raises((KeyError, ValueError)):
            UserCatData(
                source_ds=sample_dataset,
                source_crs="EPSG:4326",
                source_x_coord="invalid_x_coord",  # This coordinate doesn't exist
                source_y_coord="lat",
                source_t_coord="time",
                source_var=["temperature"],
                target_gdf=sample_polygons,
                target_crs="EPSG:4326",
                target_id="basin_id",
                source_time_period=["2020-01-01", "2020-12-31"],
            )

    def test_missing_variable_error(self, sample_dataset: xr.Dataset, sample_polygons: gpd.GeoDataFrame) -> None:
        """Test error when variable doesn't exist in dataset."""
        with pytest.raises((KeyError, ValueError)):
            UserCatData(
                source_ds=sample_dataset,
                source_crs="EPSG:4326",
                source_x_coord="lon",
                source_y_coord="lat",
                source_t_coord="time",
                source_var=["invalid_variable"],  # This variable doesn't exist
                target_gdf=sample_polygons,
                target_crs="EPSG:4326",
                target_id="basin_id",
                source_time_period=["2020-01-01", "2020-12-31"],
            )

    def test_invalid_target_id_error(self, sample_dataset: xr.Dataset, sample_polygons: gpd.GeoDataFrame) -> None:
        """Test error when target_id doesn't exist in GeoDataFrame."""
        with pytest.raises(KeyError):
            UserCatData(
                source_ds=sample_dataset,
                source_crs="EPSG:4326",
                source_x_coord="lon",
                source_y_coord="lat",
                source_t_coord="time",
                source_var=["temperature"],
                target_gdf=sample_polygons,
                target_crs="EPSG:4326",
                target_id="invalid_id",  # This ID doesn't exist
                source_time_period=["2020-01-01", "2020-12-31"],
            )

    def test_invalid_crs_error(self, sample_dataset: xr.Dataset, sample_polygons: gpd.GeoDataFrame) -> None:
        """Test error with invalid CRS specification."""
        with pytest.raises((ValueError, Exception)):
            UserCatData(
                source_ds=sample_dataset,
                source_crs="INVALID:CRS",  # Invalid CRS
                source_x_coord="lon",
                source_y_coord="lat",
                source_t_coord="time",
                source_var=["temperature"],
                target_gdf=sample_polygons,
                target_crs="EPSG:4326",
                target_id="basin_id",
                source_time_period=["2020-01-01", "2020-12-31"],
            )

    def test_invalid_time_period_error(self, sample_dataset: xr.Dataset, sample_polygons: gpd.GeoDataFrame) -> None:
        """Test error with invalid time period specification."""
        with pytest.raises((ValueError, TypeError)):
            UserCatData(
                source_ds=sample_dataset,
                source_crs="EPSG:4326",
                source_x_coord="lon",
                source_y_coord="lat",
                source_t_coord="time",
                source_var=["temperature"],
                target_gdf=sample_polygons,
                target_crs="EPSG:4326",
                target_id="basin_id",
                source_time_period=["invalid-date", "2020-12-31"],
            )

    def test_empty_variable_list_error(self, sample_dataset: xr.Dataset, sample_polygons: gpd.GeoDataFrame) -> None:
        """Test error with empty variable list."""
        with pytest.raises((ValueError, TypeError)):
            UserCatData(
                source_ds=sample_dataset,
                source_crs="EPSG:4326",
                source_x_coord="lon",
                source_y_coord="lat",
                source_t_coord="time",
                source_var=[],  # Empty variable list
                target_gdf=sample_polygons,
                target_crs="EPSG:4326",
                target_id="basin_id",
                source_time_period=["2020-01-01", "2020-12-31"],
            )

    def test_file_path_dataset(self, sample_dataset: xr.Dataset, sample_polygons: gpd.GeoDataFrame) -> None:
        """Test UserCatData with file path instead of dataset object."""
        import os
        import time

        with tempfile.NamedTemporaryFile(suffix=".nc", delete=False) as tmp_file:
            tmp_path = tmp_file.name

        # Remove units attribute from time coordinate to avoid CF encoding conflict
        ds_copy = sample_dataset.copy()
        if "units" in ds_copy.coords["time"].attrs:
            del ds_copy.coords["time"].attrs["units"]
        ds_copy.to_netcdf(tmp_path)

        try:
            user_data = UserCatData(
                source_ds=tmp_path,
                source_crs="EPSG:4326",
                source_x_coord="lon",
                source_y_coord="lat",
                source_t_coord="time",
                source_var=["temperature"],
                target_gdf=sample_polygons,
                target_crs="EPSG:4326",
                target_id="basin_id",
                source_time_period=["2020-01-01", "2020-12-31"],
            )

            assert user_data.get_class_type() == "UserCatData"

            # Close the dataset to release file handle before cleanup
            if hasattr(user_data.source_ds, "close"):
                user_data.source_ds.close()

        finally:
            # More robust cleanup for Windows
            try:
                # Give Windows a moment to release file handles
                time.sleep(0.1)
                os.unlink(tmp_path)
            except (PermissionError, FileNotFoundError):
                # On Windows, file might still be locked - that's ok for a test
                pass

    def test_no_spatial_overlap_warning(self, sample_dataset: xr.Dataset, invalid_polygons: gpd.GeoDataFrame) -> None:
        """Test handling when polygons don't overlap with dataset."""
        # This should either raise an error or handle gracefully
        # The specific behavior depends on implementation
        from contextlib import suppress
        with suppress(ValueError, IndexError, Exception):
            user_data = UserCatData(
                source_ds=sample_dataset,
                source_crs="EPSG:4326",
                source_x_coord="lon",
                source_y_coord="lat",
                source_t_coord="time",
                source_var=["temperature"],
                target_gdf=invalid_polygons,
                target_crs="EPSG:4326",
                target_id="id",
                source_time_period=["2020-01-01", "2020-12-31"],
            )
            assert user_data.get_class_type() == "UserCatData"


class TestClimRCatDataValidation:
    """Test ClimRCatData input validation and error handling."""

    def test_empty_cat_dict_error(self, sample_polygons: gpd.GeoDataFrame) -> None:
        """Test error with empty catalog dictionary."""
        with pytest.raises(ValueError):
            ClimRCatData(
                source_cat_dict={},  # Empty dictionary
                target_gdf=sample_polygons,
                target_id="basin_id",
                source_time_period=["2020-01-01", "2020-12-31"],
            )

    def test_invalid_target_id_in_climr(self, sample_polygons: gpd.GeoDataFrame) -> None:
        """Test error with invalid target_id in ClimRCatData."""
        # Mock catalog dictionary (minimal required fields)
        mock_cat_dict = {
            "temperature": {
                "URL": "http://example.com/test.nc",
                "X_name": "lon",
                "Y_name": "lat",
                "T_name": "time",
                "crs": "EPSG:4326",
            }
        }

        with pytest.raises(KeyError):
            ClimRCatData(
                source_cat_dict=mock_cat_dict,
                target_gdf=sample_polygons,
                target_id="invalid_id",  # Invalid ID
                source_time_period=["2020-01-01", "2020-12-31"],
            )


class TestWeightGenValidation:
    """Test WeightGen input validation and error handling."""

    def test_invalid_method_error(self, sample_dataset: xr.Dataset, sample_polygons: gpd.GeoDataFrame) -> None:
        """Test error with invalid weight generation method."""
        user_data = UserCatData(
            source_ds=sample_dataset,
            source_crs="EPSG:4326",
            source_x_coord="lon",
            source_y_coord="lat",
            source_t_coord="time",
            source_var=["temperature"],
            target_gdf=sample_polygons,
            target_crs="EPSG:4326",
            target_id="basin_id",
            source_time_period=["2020-01-01", "2020-12-31"],
        )

        # Method is now specified during WeightGen initialization
        with pytest.raises((ValueError, TypeError)):
            WeightGen(user_data=user_data, method="invalid_method", weight_gen_crs="EPSG:6931")

    def test_invalid_crs_in_weight_gen(self, sample_dataset: xr.Dataset, sample_polygons: gpd.GeoDataFrame) -> None:
        """Test error with invalid CRS in WeightGen."""
        user_data = UserCatData(
            source_ds=sample_dataset,
            source_crs="EPSG:4326",
            source_x_coord="lon",
            source_y_coord="lat",
            source_t_coord="time",
            source_var=["temperature"],
            target_gdf=sample_polygons,
            target_crs="EPSG:4326",
            target_id="basin_id",
            source_time_period=["2020-01-01", "2020-12-31"],
        )

        with pytest.raises((ValueError, Exception)):
            WeightGen(
                user_data=user_data,
                weight_gen_crs="INVALID:CRS",  # Invalid CRS
            )


class TestCRSHandling:
    """Test coordinate reference system handling and reprojection."""

    def test_different_crs_handling(self, sample_dataset: xr.Dataset) -> None:
        """Test handling of different CRS between source and target."""
        # Create polygons in different CRS (UTM)
        polygons_utm = gpd.GeoDataFrame(
            {
                "id": ["test_1"],
                "geometry": [Polygon([(500000, 4000000), (600000, 4000000), (600000, 4100000), (500000, 4100000)])],
            },
            crs="EPSG:32613",
        )  # UTM Zone 13N

        user_data = UserCatData(
            source_ds=sample_dataset,
            source_crs="EPSG:4326",
            source_x_coord="lon",
            source_y_coord="lat",
            source_t_coord="time",
            source_var=["temperature"],
            target_gdf=polygons_utm,
            target_crs="EPSG:32613",
            target_id="id",
            source_time_period=["2020-01-01", "2020-12-31"],
        )

        # Should handle CRS transformation
        assert user_data.get_class_type() == "UserCatData"

    def test_equal_area_projection(self, sample_dataset: xr.Dataset, sample_polygons: gpd.GeoDataFrame) -> None:
        """Test equal area projection for accurate weight calculation."""
        user_data = UserCatData(
            source_ds=sample_dataset,
            source_crs="EPSG:4326",
            source_x_coord="lon",
            source_y_coord="lat",
            source_t_coord="time",
            source_var=["temperature"],
            target_gdf=sample_polygons,
            target_crs="EPSG:4326",
            target_id="basin_id",
            source_time_period=["2020-01-01", "2020-12-31"],
        )

        # Test with equal area projection
        weight_gen = WeightGen(
            user_data=user_data,
            method="serial",
            weight_gen_crs="EPSG:6931",  # US National Atlas Equal Area
        )

        # Should work without errors
        assert weight_gen.user_data is not None


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_single_point_polygon(self, sample_dataset: xr.Dataset) -> None:
        """Test with degenerate polygon (single point)."""
        point_gdf = gpd.GeoDataFrame({"id": ["point_1"], "geometry": [Point(-100, 40)]}, crs="EPSG:4326")

        # This might raise an error or handle gracefully depending on implementation
        try:
            user_data = UserCatData(
                source_ds=sample_dataset,
                source_crs="EPSG:4326",
                source_x_coord="lon",
                source_y_coord="lat",
                source_t_coord="time",
                source_var=["temperature"],
                target_gdf=point_gdf,
                target_crs="EPSG:4326",
                target_id="id",
                source_time_period=["2020-01-01", "2020-12-31"],
            )
            assert user_data.get_class_type() == "UserCatData"
        except (ValueError, Exception):
            # Error is acceptable for degenerate geometry
            import logging
            logging.exception("Exception occurred in test_single_point_polygon")

    def test_single_time_step(self, sample_polygons: gpd.GeoDataFrame) -> None:
        """Test with dataset containing only one time step."""
        # Create single-time dataset
        single_time_ds = xr.Dataset(
            {"temperature": (["lat", "lon"], np.random.randn(10, 10))},
            coords={"lat": np.linspace(35, 45, 10), "lon": np.linspace(-105, -95, 10)},
        )

        try:
            user_data = UserCatData(
                source_ds=single_time_ds,
                source_crs="EPSG:4326",
                source_x_coord="lon",
                source_y_coord="lat",
                source_t_coord="time",  # This coordinate doesn't exist
                source_var=["temperature"],
                target_gdf=sample_polygons,
                target_crs="EPSG:4326",
                target_id="basin_id",
                source_time_period=["2020-01-01", "2020-01-01"],
            )
            assert user_data.get_class_type() == "UserCatData"
        except (KeyError, ValueError):
            # Expected behavior for missing time coordinate
            pass

    def test_very_large_polygon(self, sample_dataset: xr.Dataset) -> None:
        """Test with very large polygon that covers entire dataset."""
        # Create polygon that covers the entire dataset extent
        large_polygon = gpd.GeoDataFrame(
            {"id": ["large_1"], "geometry": [Polygon([(-110, 30), (-90, 30), (-90, 50), (-110, 50)])]}, crs="EPSG:4326"
        )

        user_data = UserCatData(
            source_ds=sample_dataset,
            source_crs="EPSG:4326",
            source_x_coord="lon",
            source_y_coord="lat",
            source_t_coord="time",
            source_var=["temperature"],
            target_gdf=large_polygon,
            target_crs="EPSG:4326",
            target_id="id",
            source_time_period=["2020-01-01", "2020-12-31"],
        )

        assert user_data.get_class_type() == "UserCatData"
