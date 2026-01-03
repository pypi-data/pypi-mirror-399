"""Tests for .helper functions."""

import gc
from collections.abc import Generator
from typing import Any

import geopandas as gpd
import numpy as np
import pandas as pd
import pystac
import pytest
import xarray as xr
from gdptools.helpers import (
    STACCatalogError,
    build_subset,
    check_gridded_data_for_dimensions,
)


@pytest.fixture(scope="function")
def get_var() -> str:
    """Get variable string."""
    return "aet"


@pytest.fixture(scope="function")
def climrcat() -> Generator[dict[str, dict[str, Any]], None, None]:
    """Return climr catalog json."""
    cat = "https://github.com/mikejohnson51/climateR-catalogs/releases/download/June-2024/catalog.parquet"
    climr: pd.DataFrame = pd.read_parquet(cat)
    _id = "terraclim"
    _varname = "aet"
    cat_d: dict[str, Any] = climr.query("id == @_id & varname == @_varname").to_dict("records")[0]
    data = dict(zip([_varname], [cat_d]))  # noqa
    yield data
    del data
    gc.collect()


@pytest.fixture(scope="function")
def get_gdf() -> gpd.GeoDataFrame:
    """Create GeoDataFrame."""
    return gpd.read_file("./tests/data/hru_1210_epsg5070.shp")  # type: ignore


@pytest.fixture(scope="function")
def get_begin_date() -> str:
    """Get begin date."""
    return "2005-01-01"


@pytest.fixture(scope="function")
def get_end_date() -> str:
    """Get end date."""
    return "2005-02-01"


@pytest.fixture(scope="function")
def get_toptobottom() -> str:
    """Get end date."""
    return "True"


@pytest.fixture(scope="function")
def get_xcoord() -> str:
    """Get end date."""
    return "lon"


@pytest.fixture(scope="function")
def get_ycoord() -> str:
    """Get end date."""
    return "lat"


@pytest.fixture(scope="function")
def get_tcoord() -> str:
    """Get end date."""
    return "day"


@pytest.fixture(scope="function")
def get_xarray(climrcat, get_var) -> Generator[xr.Dataset, None, None]:
    """Create xarray Dataset."""
    ds = xr.open_dataset(climrcat[get_var]["URL"])
    yield ds
    del ds
    gc.collect()


def test_check_gridded_data_for_dimensions(get_xarray, get_var) -> None:
    """Test function check_gridded_data_for_dimensions."""
    output = check_gridded_data_for_dimensions(get_xarray, [get_var])
    assert isinstance(output, type(None))


def test_build_subset(
    get_gdf,
    get_xcoord,
    get_ycoord,
    get_tcoord,
    get_toptobottom,
    get_begin_date,
    get_end_date,
) -> None:
    """Test function build_subset."""
    subset = build_subset(
        bounds=np.asarray(get_gdf.bounds.loc[0]),
        xname=get_xcoord,
        yname=get_ycoord,
        tname=get_tcoord,
        toptobottom=get_toptobottom,
        date_min=get_begin_date,
        date_max=get_end_date,
    )

    real_subset = {
        "lon": slice(2054594.7771999985, 2127645.084399998, None),
        "lat": slice(2358794.8389, 2406615.137599999, None),
        "day": slice("2005-01-01", "2005-02-01", None),
    }

    assert subset == real_subset


# -----------------------------------------------------------------------------
# Tests for get_stac_collection
#
# These tests depend on an external STAC catalog that may be rate-limited or
# unavailable. We use xfail so network failures don't break CI, but tests
# actually run and pass when the catalog is accessible.
# -----------------------------------------------------------------------------

# Exceptions that can occur when STAC catalog is unavailable or rate-limited
_stac_network_errors = (STACCatalogError, pystac.STACError, Exception)

# Currently these are taking too long, and there are issues that need to be resolved on the server side so
# commenting them out for now.

# @pytest.mark.xfail(raises=_stac_network_errors, reason="STAC catalog may be unavailable or rate-limited")
# def test_get_stac_collection_valid_nested() -> None:
#     """Test fetching a valid nested data collection (conus404_daily)."""
#     collection = get_stac_collection("conus404_daily")

#     assert isinstance(collection, pystac.Collection)
#     assert collection.id == "conus404_daily"
#     # Data collections should have zarr assets
#     assert "zarr-s3-osn" in collection.assets


# @pytest.mark.xfail(raises=_stac_network_errors, reason="STAC catalog may be unavailable or rate-limited")
# def test_get_stac_collection_valid_toplevel() -> None:
#     """Test fetching a valid top-level collection."""
#     collection = get_stac_collection("conus404")

#     assert isinstance(collection, pystac.Collection)
#     assert collection.id == "conus404"


# @pytest.mark.xfail(raises=_stac_network_errors, reason="STAC catalog may be unavailable or rate-limited")
# def test_get_stac_collection_not_found() -> None:
#     """Test that a nonexistent collection raises STACCatalogError."""
#     with pytest.raises(STACCatalogError, match="not found in NHGF STAC catalog"):
#         get_stac_collection("nonexistent_collection_xyz")


# @pytest.mark.xfail(raises=_stac_network_errors, reason="STAC catalog may be unavailable or rate-limited")
# def test_get_stac_collection_has_expected_assets() -> None:
#     """Test that a data collection contains expected zarr asset structure."""
#     collection = get_stac_collection("conus404_daily")

#     asset = collection.assets.get("zarr-s3-osn")
#     assert asset is not None
#     assert hasattr(asset, "href")
#     assert "xarray:storage_options" in asset.extra_fields
