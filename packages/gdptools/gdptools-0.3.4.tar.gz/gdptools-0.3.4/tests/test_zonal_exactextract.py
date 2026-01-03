"""Tests for exactextract zonal engine output format matching serial engine."""

from pathlib import Path

import geopandas as gpd
import numpy as np
import pytest
import rioxarray as rxr
from gdptools import ZonalGen
from gdptools.data.user_data import UserTiffData


@pytest.fixture
def slope_data():
    """Load slope raster and Oahu shapefile for continuous data tests."""
    test_dir = Path(__file__).parent
    raster_path = test_dir / "data" / "rasters" / "slope" / "slope.tif"
    shp_path = test_dir / "data" / "Oahu.shp"

    rds = rxr.open_rasterio(raster_path)
    gdf = gpd.read_file(shp_path)

    return rds, gdf


def test_exactextract_output_format_matches_serial(slope_data, tmp_path):
    """Test that exactextract engine produces output with same format as serial.

    This test verifies that the exactextract engine output has:
    - Same columns as serial engine
    - Same number of rows (one per polygon)
    - Reasonable values (means are correlated, counts are proportional)

    Note: Exact numerical equality is not expected because:
    - Serial engine counts whole pixels contained in polygons
    - ExactExtract computes fractional coverage with subpixel precision
    These are fundamentally different algorithms with different tradeoffs.
    """
    rds, gdf = slope_data
    id_feature = "fid"
    crs = 26904
    tx_name = "x"
    ty_name = "y"
    band = 1
    bname = "band"
    varname = "slope"

    # Prepare UserTiffData
    data = UserTiffData(
        source_var=varname,
        source_ds=rds,
        source_crs=crs,
        source_x_coord=tx_name,
        source_y_coord=ty_name,
        band=band,
        bname=bname,
        target_gdf=gdf,
        target_id=id_feature,
    )

    # Serial engine
    zonal_serial = ZonalGen(
        user_data=data,
        zonal_engine="serial",
        zonal_writer="csv",
        out_path=str(tmp_path),
        file_prefix="serial",
    )
    stats_serial = zonal_serial.calculate_zonal(categorical=False)

    # ExactExtract engine
    zonal_exact = ZonalGen(
        user_data=data,
        zonal_engine="exactextract",
        zonal_writer="csv",
        out_path=str(tmp_path),
        file_prefix="exactextract",
    )
    stats_exact = zonal_exact.calculate_zonal(categorical=False)

    # --- Format validation ---

    # Both DataFrames should have the same shape
    assert stats_serial.shape == stats_exact.shape, (
        f"Shape mismatch: serial={stats_serial.shape}, exact={stats_exact.shape}"
    )

    # Both should have the same columns
    serial_cols = sorted(stats_serial.columns.tolist())
    exact_cols = sorted(stats_exact.columns.tolist())
    assert serial_cols == exact_cols, (
        f"Column mismatch: serial={serial_cols}, exact={exact_cols}"
    )

    # Verify expected columns are present
    expected_cols = ["count", "mean", "std", "min", "25%", "50%", "75%", "max", "sum"]
    for col in expected_cols:
        assert col in stats_serial.columns, f"Serial missing column: {col}"
        assert col in stats_exact.columns, f"ExactExtract missing column: {col}"

    # --- Reasonableness validation ---

    # Reset index to make the id feature a column for comparison
    stats_serial = stats_serial.reset_index()
    stats_exact = stats_exact.reset_index()

    # Sort both by the id feature for consistent comparison
    stats_serial = stats_serial.sort_values(by=id_feature).reset_index(drop=True)
    stats_exact = stats_exact.sort_values(by=id_feature).reset_index(drop=True)

    # Verify mean values are highly correlated (R > 0.99)
    correlation = np.corrcoef(stats_serial["mean"].values, stats_exact["mean"].values)[0, 1]
    assert correlation > 0.99, f"Mean correlation too low: {correlation:.4f}"

    # Verify count values are highly correlated (different algorithms, same trend)
    count_corr = np.corrcoef(stats_serial["count"].values, stats_exact["count"].values)[0, 1]
    assert count_corr > 0.99, f"Count correlation too low: {count_corr:.4f}"

    # Verify the id column values match exactly
    np.testing.assert_array_equal(
        stats_serial[id_feature].values,
        stats_exact[id_feature].values,
        err_msg="ID values don't match",
    )
