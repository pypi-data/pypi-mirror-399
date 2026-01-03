"""Tests for exactextract zonal engine output format matching serial engine for categorical data."""

from pathlib import Path

import geopandas as gpd
import numpy as np
import pytest
import rioxarray as rxr
from gdptools import ZonalGen
from gdptools.data.user_data import UserTiffData


@pytest.fixture
def text_data():
    """Load TEXT_PRMS categorical raster and Oahu shapefile."""
    test_dir = Path(__file__).parent
    raster_path = test_dir / "data" / "rasters" / "TEXT_PRMS" / "TEXT_PRMS.tif"
    shp_path = test_dir / "data" / "Oahu.shp"

    rds = rxr.open_rasterio(raster_path)
    gdf = gpd.read_file(shp_path)

    return rds, gdf


def test_exactextract_categorical_output_format_matches_serial(text_data, tmp_path):
    """Test that exactextract engine produces output with same format as serial for categorical data.

    This test verifies that the exactextract engine output has:
    - Same columns as serial engine (category values + count)
    - Same number of rows (one per polygon)
    - Reasonable values (fractions sum to ~1 for each polygon)

    Note: Exact numerical equality is not expected because:
    - Serial engine counts whole pixels contained in polygons
    - ExactExtract computes fractional coverage with subpixel precision
    These are fundamentally different algorithms with different tradeoffs.
    """
    rds, gdf = text_data
    id_feature = "fid"
    crs = 26904
    tx_name = "x"
    ty_name = "y"
    band = 1
    bname = "band"
    varname = "TEXT"

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
        file_prefix="serial_cat",
    )
    stats_serial = zonal_serial.calculate_zonal(categorical=True)

    # ExactExtract engine
    zonal_exact = ZonalGen(
        user_data=data,
        zonal_engine="exactextract",
        zonal_writer="csv",
        out_path=str(tmp_path),
        file_prefix="exactextract_cat",
    )
    stats_exact = zonal_exact.calculate_zonal(categorical=True)

    # --- Format validation ---

    # Both DataFrames should have the same shape
    assert stats_serial.shape == stats_exact.shape, (
        f"Shape mismatch: serial={stats_serial.shape}, exact={stats_exact.shape}"
    )

    # Both should have the same columns (convert to strings for comparison)
    serial_cols = sorted([str(c) for c in stats_serial.columns])
    exact_cols = sorted([str(c) for c in stats_exact.columns])
    assert serial_cols == exact_cols, (
        f"Column mismatch: serial={serial_cols}, exact={exact_cols}"
    )

    # Verify 'count' column is present
    assert "count" in stats_serial.columns, "Serial missing 'count' column"
    assert "count" in stats_exact.columns, "ExactExtract missing 'count' column"

    # --- Reasonableness validation ---

    # Sort both by the index for consistent comparison
    stats_serial = stats_serial.sort_index()
    stats_exact = stats_exact.sort_index()

    # Identify category columns (not 'count')
    cat_cols = [c for c in stats_serial.columns if c != "count"]

    # Verify fractions sum to approximately 1 for each polygon (both engines)
    serial_row_sums = stats_serial[cat_cols].sum(axis=1)
    exact_row_sums = stats_exact[cat_cols].sum(axis=1)

    # Most rows should sum to 1.0 (within tolerance)
    np.testing.assert_allclose(
        serial_row_sums.values,
        np.ones(len(serial_row_sums)),
        rtol=0.01,
        atol=0.01,
        err_msg="Serial fractions don't sum to 1",
    )
    np.testing.assert_allclose(
        exact_row_sums.values,
        np.ones(len(exact_row_sums)),
        rtol=0.01,
        atol=0.01,
        err_msg="ExactExtract fractions don't sum to 1",
    )

    # Verify count values are correlated (different algorithms may have different counts
    # for small polygons, especially at edges)
    serial_counts = stats_serial["count"].values
    exact_counts = stats_exact["count"].values
    count_corr = np.corrcoef(serial_counts, exact_counts)[0, 1]
    assert count_corr > 0.90, f"Count correlation too low: {count_corr:.4f}"

    # Verify dominant category matches for most polygons
    # Get the dominant category for each polygon (column with max value)
    serial_dominant = stats_serial[cat_cols].idxmax(axis=1)
    exact_dominant = stats_exact[cat_cols].idxmax(axis=1)
    match_rate = (serial_dominant == exact_dominant).mean()
    assert match_rate >= 0.85, (
        f"Dominant category match rate too low: {match_rate:.2%}"
    )
