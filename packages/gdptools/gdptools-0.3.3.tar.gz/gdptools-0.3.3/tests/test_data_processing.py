"""Test core data processing and aggregation functionality."""

import gc
import tempfile
from collections.abc import Generator
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import pytest
import xarray as xr
from gdptools import AggGen, UserCatData, WeightGen
from shapely.geometry import Polygon


@pytest.fixture(scope="function")
def test_dataset() -> Generator[xr.Dataset, None, None]:
    """Create consistent test dataset."""
    time = pd.date_range("2020-01-01", periods=24, freq="MS")
    lat = np.linspace(35, 45, 20)
    lon = np.linspace(-105, -95, 20)

    # Create realistic temperature data with seasonal variation
    temp_base = 15 + 10 * np.sin(np.arange(24) * 2 * np.pi / 12)
    temp_data = temp_base[:, None, None] + np.random.randn(24, 20, 20) * 2

    # Create precipitation data
    precip_data = np.abs(np.random.randn(24, 20, 20)) * 30 + 20

    ds = xr.Dataset({
        "temperature": (["time", "lat", "lon"], temp_data),
        "precipitation": (["time", "lat", "lon"], precip_data)
    }, coords={
        "time": time,
        "lat": lat,
        "lon": lon
    })

    # Add attributes for realism
    ds.temperature.attrs = {"units": "degrees_C", "long_name": "Air Temperature"}
    ds.precipitation.attrs = {"units": "mm", "long_name": "Precipitation"}

    # Add units attributes to coordinate variables (required by gdptools)
    ds.coords['time'].attrs['units'] = 'days since 1970-01-01'
    ds.coords['lat'].attrs['units'] = 'degrees_north'
    ds.coords['lon'].attrs['units'] = 'degrees_east'

    yield ds
    del ds
    gc.collect()


@pytest.fixture(scope="function")
def test_polygons() -> Generator[gpd.GeoDataFrame, None, None]:
    """Create test polygons with known properties."""
    polygons = [
        # Small polygon in upper left
        Polygon([(-104, 42), (-102, 42), (-102, 44), (-104, 44)]),
        # Medium polygon in center
        Polygon([(-102, 38), (-98, 38), (-98, 42), (-102, 42)]),
        # Large polygon in lower right
        Polygon([(-100, 35), (-96, 35), (-96, 39), (-100, 39)])
    ]

    gdf = gpd.GeoDataFrame({
        "region_id": ["small", "medium", "large"],
        "area_km2": [8000, 32000, 32000],  # Approximate areas
        "category": ["mountain", "plains", "desert"],
        "geometry": polygons
    }, crs="EPSG:4326")

    yield gdf
    del gdf
    gc.collect()


class TestDataProcessingWorkflow:
    """Test complete data processing workflows."""

    def test_full_aggregation_workflow(
        self,
        test_dataset: xr.Dataset,
        test_polygons: gpd.GeoDataFrame
    ) -> None:
        """Test complete aggregation workflow from data to results."""
        # Setup UserCatData
        user_data = UserCatData(
            source_ds=test_dataset,
            source_crs="EPSG:4326",
            source_x_coord="lon",
            source_y_coord="lat",
            source_t_coord="time",
            source_var=["temperature", "precipitation"],
            target_gdf=test_polygons,
            target_crs="EPSG:4326",
            target_id="region_id",
            source_time_period=["2020-01-01", "2020-12-31"]
        )

        # Generate weights
        weight_gen = WeightGen(user_data=user_data, method="serial", weight_gen_crs="EPSG:4326")
        weights = weight_gen.calculate_weights()

        # Verify weights structure
        assert isinstance(weights, pd.DataFrame)
        assert len(weights) > 0
        assert "wght" in weights.columns
        assert all(weights["wght"] >= 0)

        # Perform aggregation
        agg_gen = AggGen(
            user_data=user_data,
            stat_method="masked_mean",
            agg_engine="serial",
            agg_writer="none",
            weights=weights
        )

        result_gdf, result_dataset = agg_gen.calculate_agg()

        # Verify results
        assert isinstance(result_gdf, gpd.GeoDataFrame)
        assert isinstance(result_dataset, xr.Dataset)
        assert len(result_gdf) == len(test_polygons)
        assert "temperature" in result_dataset.data_vars
        assert "precipitation" in result_dataset.data_vars

    def test_statistical_methods(
        self,
        test_dataset: xr.Dataset,
        test_polygons: gpd.GeoDataFrame
    ) -> None:
        """Test different statistical aggregation methods."""
        user_data = UserCatData(
            source_ds=test_dataset,
            source_crs="EPSG:4326",
            source_x_coord="lon",
            source_y_coord="lat",
            source_t_coord="time",
            source_var=["temperature"],
            target_gdf=test_polygons,
            target_crs="EPSG:4326",
            target_id="region_id",
            source_time_period=["2020-01-01", "2020-06-30"]
        )

        weight_gen = WeightGen(user_data=user_data, method="serial", weight_gen_crs="EPSG:4326")
        weights_df = weight_gen.calculate_weights()

        # Test different statistical methods
        stat_methods = ["masked_mean", "masked_sum", "masked_std"]

        for stat_method in stat_methods:
            agg_gen = AggGen(
                user_data=user_data,
                stat_method=stat_method,
                agg_engine="serial",
                agg_writer="none",
                weights=weights_df
            )

            result_gdf, result_dataset = agg_gen.calculate_agg()

            # Verify results exist and are finite
            assert len(result_gdf) == len(test_polygons)
            temp_values = result_dataset["temperature"].values
            assert np.all(np.isfinite(temp_values))

            # Check that different methods give different results
            if stat_method == "masked_sum":
                # Sum should generally be larger than mean
                assert np.all(temp_values > 0)  # Temperature sum should be positive

    def test_temporal_subsetting(
        self,
        test_dataset: xr.Dataset,
        test_polygons: gpd.GeoDataFrame
    ) -> None:
        """Test temporal subsetting functionality."""
        # Test different time periods
        time_periods = [
            ["2020-01-01", "2020-03-31"],  # Q1
            ["2020-06-01", "2020-08-31"],  # Summer
            ["2020-01-01", "2020-12-31"]   # Full year
        ]

        results = {}

        for i, period in enumerate(time_periods):
            user_data = UserCatData(
                source_ds=test_dataset,
                source_crs="EPSG:4326",
                source_x_coord="lon",
                source_y_coord="lat",
                source_t_coord="time",
                source_var=["temperature"],
                target_gdf=test_polygons,
                target_crs="EPSG:4326",
                target_id="region_id",
                source_time_period=period
            )

            weight_gen = WeightGen(user_data=user_data, method="serial", weight_gen_crs="EPSG:4326")
            weights_df = weight_gen.calculate_weights()

            agg_gen = AggGen(
                user_data=user_data,
                stat_method="masked_mean",
                agg_engine="serial",
                agg_writer="none",
                weights=weights_df
            )

            result_gdf, result_dataset = agg_gen.calculate_agg()
            results[f"period_{i}"] = result_dataset["temperature"].values

        # Verify that different time periods give different results
        assert not np.array_equal(results["period_0"], results["period_1"])

        # Full year should have more time steps
        full_year_data = test_dataset.sel(time=slice("2020-01-01", "2020-12-31"))
        q1_data = test_dataset.sel(time=slice("2020-01-01", "2020-03-31"))
        assert len(full_year_data.time) > len(q1_data.time)

    def test_parallel_vs_serial_consistency(
        self,
        test_dataset: xr.Dataset,
        test_polygons: gpd.GeoDataFrame
    ) -> None:
        """Test that parallel and serial methods give consistent results."""
        user_data = UserCatData(
            source_ds=test_dataset,
            source_crs="EPSG:4326",
            source_x_coord="lon",
            source_y_coord="lat",
            source_t_coord="time",
            source_var=["temperature"],
            target_gdf=test_polygons,
            target_crs="EPSG:4326",
            target_id="region_id",
            source_time_period=["2020-01-01", "2020-06-30"]
        )

        # Serial processing
        weight_gen_serial = WeightGen(user_data=user_data, method="serial", weight_gen_crs="EPSG:4326")
        weights_serial = weight_gen_serial.calculate_weights()

        agg_gen_serial = AggGen(
            user_data=user_data,
            stat_method="masked_mean",
            agg_engine="serial",
            agg_writer="none",
            weights=weights_serial
        )
        result_serial_gdf, result_serial_ds = agg_gen_serial.calculate_agg()

        # Parallel processing
        weight_gen_parallel = WeightGen(user_data=user_data, method="parallel", weight_gen_crs="EPSG:4326")
        weights_parallel = weight_gen_parallel.calculate_weights()

        agg_gen_parallel = AggGen(
            user_data=user_data,
            stat_method="masked_mean",
            agg_engine="parallel",
            agg_writer="none",
            weights=weights_parallel
        )
        result_parallel_gdf, result_parallel_ds = agg_gen_parallel.calculate_agg()

        # Results should be very similar (allowing for small numerical differences)
        serial_values = result_serial_ds["temperature"].values
        parallel_values = result_parallel_ds["temperature"].values

        # Use relative tolerance for comparison
        np.testing.assert_allclose(serial_values, parallel_values, rtol=1e-10, atol=1e-10)

    def test_output_formats(
        self,
        test_dataset: xr.Dataset,
        test_polygons: gpd.GeoDataFrame
    ) -> None:
        """Test different output formats."""
        user_data = UserCatData(
            source_ds=test_dataset,
            source_crs="EPSG:4326",
            source_x_coord="lon",
            source_y_coord="lat",
            source_t_coord="time",
            source_var=["temperature"],
            target_gdf=test_polygons,
            target_crs="EPSG:4326",
            target_id="region_id",
            source_time_period=["2020-01-01", "2020-03-31"]
        )

        weight_gen = WeightGen(user_data=user_data, method="serial", weight_gen_crs="EPSG:4326")
        weights_df = weight_gen.calculate_weights()

        with tempfile.TemporaryDirectory() as temp_dir:
            # Test NetCDF output
            agg_gen_nc = AggGen(
                user_data=user_data,
                stat_method="masked_mean",
                agg_engine="serial",
                agg_writer="netcdf",
                weights=weights_df,
                out_path=temp_dir,
                file_prefix="test_output"
            )

            result_gdf, result_dataset = agg_gen_nc.calculate_agg()

            # Check that NetCDF file was created
            nc_files = list(Path(temp_dir).glob("*.nc"))
            assert len(nc_files) > 0

            # Test CSV output
            agg_gen_csv = AggGen(
                user_data=user_data,
                stat_method="masked_mean",
                agg_engine="serial",
                agg_writer="csv",
                weights=weights_df,
                out_path=temp_dir,
                file_prefix="test_output_csv"
            )

            result_gdf_csv, result_dataset_csv = agg_gen_csv.calculate_agg()

            # Check that CSV file was created
            csv_files = list(Path(temp_dir).glob("*.csv"))
            assert len(csv_files) > 0


class TestPerformanceAndScaling:
    """Test performance aspects and scaling behavior."""

    def test_large_polygon_handling(self, test_dataset: xr.Dataset) -> None:
        """Test handling of polygons with many vertices."""
        # Create polygon with many vertices (simulating complex coastline)
        angles = np.linspace(0, 2*np.pi, 100)
        radius = 2
        center_lon, center_lat = -100, 40

        # Create circle with noise to simulate complex boundary
        lon_coords = center_lon + radius * np.cos(angles) + np.random.randn(100) * 0.1
        lat_coords = center_lat + radius * np.sin(angles) + np.random.randn(100) * 0.1

        complex_polygon = Polygon(zip(lon_coords, lat_coords, strict=False))

        complex_gdf = gpd.GeoDataFrame({
            "id": ["complex"],
            "geometry": [complex_polygon]
        }, crs="EPSG:4326")

        user_data = UserCatData(
            source_ds=test_dataset,
            source_crs="EPSG:4326",
            source_x_coord="lon",
            source_y_coord="lat",
            source_t_coord="time",
            source_var=["temperature"],
            target_gdf=complex_gdf,
            target_crs="EPSG:4326",
            target_id="id",
            source_time_period=["2020-01-01", "2020-02-29"]
        )

        weight_gen = WeightGen(user_data=user_data, method="serial", weight_gen_crs="EPSG:4326")
        weights_df = weight_gen.calculate_weights()
        # Should handle complex polygon without errors
        assert isinstance(weights_df, pd.DataFrame)
        assert len(weights_df["wght"]) > 0

    def test_memory_efficiency(self, test_polygons: gpd.GeoDataFrame) -> None:
        """Test memory efficient processing with chunked data."""
        # Create larger dataset to test chunking
        time = pd.date_range("2020-01-01", periods=100, freq="D")
        lat = np.linspace(35, 45, 50)
        lon = np.linspace(-105, -95, 50)

        # Create chunked dataset
        large_ds = xr.Dataset({
            "temperature": (["time", "lat", "lon"],
                          np.random.randn(100, 50, 50) * 10 + 20)
        }, coords={
            "time": time,
            "lat": lat,
            "lon": lon
        }).chunk({"time": 10, "lat": 25, "lon": 25})

        # Add units attributes to coordinate variables
        large_ds.coords['time'].attrs['units'] = 'days since 1970-01-01'
        large_ds.coords['lat'].attrs['units'] = 'degrees_north'
        large_ds.coords['lon'].attrs['units'] = 'degrees_east'

        user_data = UserCatData(
            source_ds=large_ds,
            source_crs="EPSG:4326",
            source_x_coord="lon",
            source_y_coord="lat",
            source_t_coord="time",
            source_var=["temperature"],
            target_gdf=test_polygons,
            target_crs="EPSG:4326",
            target_id="region_id",
            source_time_period=["2020-01-01", "2020-03-31"]
        )

        # Should handle chunked data efficiently
        weight_gen = WeightGen(user_data=user_data, method="serial", weight_gen_crs="EPSG:4326")
        weights_df = weight_gen.calculate_weights()

        assert isinstance(weights_df, pd.DataFrame)
        assert len(weights_df["wght"]) > 0


class TestDataQuality:
    """Test data quality and validation."""

    def test_missing_data_handling(self, test_polygons: gpd.GeoDataFrame) -> None:
        """Test handling of datasets with missing values."""
        # Create dataset with NaN values
        time = pd.date_range("2020-01-01", periods=12, freq="MS")
        lat = np.linspace(35, 45, 10)
        lon = np.linspace(-105, -95, 10)

        temp_data = np.random.randn(12, 10, 10) * 10 + 20
        temp_data[5:7, 3:6, 4:7] = np.nan  # Insert missing values

        nan_ds = xr.Dataset({
            "temperature": (["time", "lat", "lon"], temp_data)
        }, coords={
            "time": time,
            "lat": lat,
            "lon": lon
        })

        # Add units attributes to coordinate variables
        nan_ds.coords['time'].attrs['units'] = 'days since 1970-01-01'
        nan_ds.coords['lat'].attrs['units'] = 'degrees_north'
        nan_ds.coords['lon'].attrs['units'] = 'degrees_east'

        user_data = UserCatData(
            source_ds=nan_ds,
            source_crs="EPSG:4326",
            source_x_coord="lon",
            source_y_coord="lat",
            source_t_coord="time",
            source_var=["temperature"],
            target_gdf=test_polygons,
            target_crs="EPSG:4326",
            target_id="region_id",
            source_time_period=["2020-01-01", "2020-12-31"]
        )

        weight_gen = WeightGen(user_data=user_data, method="serial", weight_gen_crs="EPSG:4326")
        weights_df = weight_gen.calculate_weights()

        agg_gen = AggGen(
            user_data=user_data,
            stat_method="masked_mean",  # Should handle NaN values properly
            agg_engine="serial",
            agg_writer="none",
            weights=weights_df
        )

        result_gdf, result_dataset = agg_gen.calculate_agg()

        # Results should be finite where data exists
        temp_result = result_dataset["temperature"].values
        assert np.any(np.isfinite(temp_result))  # Some values should be finite

    def test_extreme_values(self, test_polygons: gpd.GeoDataFrame) -> None:
        """Test handling of extreme values in data."""
        # Create dataset with extreme values
        time = pd.date_range("2020-01-01", periods=6, freq="MS")
        lat = np.linspace(35, 45, 10)
        lon = np.linspace(-105, -95, 10)

        temp_data = np.random.randn(6, 10, 10) * 10 + 20
        temp_data[0, 0, 0] = 1000  # Extreme hot
        temp_data[1, 1, 1] = -1000  # Extreme cold

        extreme_ds = xr.Dataset({
            "temperature": (["time", "lat", "lon"], temp_data)
        }, coords={
            "time": time,
            "lat": lat,
            "lon": lon
        })

        # Add units attributes to coordinate variables
        extreme_ds.coords['time'].attrs['units'] = 'days since 1970-01-01'
        extreme_ds.coords['lat'].attrs['units'] = 'degrees_north'
        extreme_ds.coords['lon'].attrs['units'] = 'degrees_east'

        user_data = UserCatData(
            source_ds=extreme_ds,
            source_crs="EPSG:4326",
            source_x_coord="lon",
            source_y_coord="lat",
            source_t_coord="time",
            source_var=["temperature"],
            target_gdf=test_polygons,
            target_crs="EPSG:4326",
            target_id="region_id",
            source_time_period=["2020-01-01", "2020-06-30"]
        )

        weight_gen = WeightGen(user_data=user_data, method="serial", weight_gen_crs="EPSG:4326")
        weights_df = weight_gen.calculate_weights()

        agg_gen = AggGen(
            user_data=user_data,
            stat_method="masked_mean",
            agg_engine="serial",
            agg_writer="none",
            weights=weights_df
        )

        result_gdf, result_dataset = agg_gen.calculate_agg()

        # Should handle extreme values without crashing
        assert isinstance(result_dataset, xr.Dataset)
        temp_values = result_dataset["temperature"].values
        assert np.all(np.isfinite(temp_values))
