"""Helper functions for data subsetting and validation.

This module provides utility functions that support the core functionality of
gdptools by providing:
- Spatial and temporal subsetting for xarray Datasets and DataArrays.
- Validation checks for gridded data dimensions.

"""

from __future__ import annotations

import logging
from collections.abc import Mapping
from typing import Any

import numpy as np
import numpy.typing as npt
import pystac
import xarray as xr

logger = logging.getLogger(__name__)

# NHGF STAC catalog URL
NHGF_STAC_CATALOG_URL = "https://api.water.usgs.gov/gdp/pygeoapi/stac/stac-collection/"


class GDPToolsError(Exception):
    """Base exception for gdptools library errors."""


class STACCatalogError(GDPToolsError):
    """Exception raised when STAC catalog operations fail."""

pd_offset_conv: dict[str, str] = {
    "years": "Y",
    "months": "M",
    "days": "D",
    "hours": "H",
}


def build_subset(
    bounds: npt.NDArray[np.double],
    xname: str,
    yname: str,
    tname: str,
    toptobottom: bool,
    date_min: str | None = None,
    date_max: str | None = None,
) -> dict[str, object]:
    """Create a dictionary to use with xarray .sel() method to subset by time and space.

    Constructs a selection dictionary for xarray subsetting operations that handles
    both spatial (x, y) and temporal (time) dimensions. Automatically adjusts for
    coordinate system orientation and provides flexible time range selection.

    Args:
        bounds: Spatial bounds array in format [minx, miny, maxx, maxy].
        xname: Name of the x-dimension in the dataset.
        yname: Name of the y-dimension in the dataset.
        tname: Name of the time dimension in the dataset.
        toptobottom: If True, y-coordinates increase from north to south. If False,
            y-coordinates increase from south to north.
        date_min: Start date for temporal subset (ISO format string). If None,
            no temporal subsetting is applied.
        date_max: End date for temporal subset (ISO format string). If None and
            date_min is provided, only the exact date_min is selected.

    Returns:
        Dictionary containing slice objects for xarray .sel() method with keys
        corresponding to dimension names and values as slice objects or exact values.

    Examples:
        >>> bounds = np.array([-180, -90, 180, 90])
        >>> subset_dict = build_subset(
        ...     bounds, 'longitude', 'latitude', 'time', False,
        ...     '2020-01-01', '2020-12-31'
        ... )
        >>> data_subset = dataset.sel(subset_dict)

    """
    minx = bounds[0]
    maxx = bounds[2]
    miny = bounds[1]
    maxy = bounds[3]
    if not toptobottom:
        if date_max is None and date_min is None:
            return {
                xname: slice(minx, maxx),
                yname: slice(maxy, miny),
            }
        elif date_max is None:
            return {
                xname: slice(minx, maxx),
                yname: slice(maxy, miny),
                tname: date_min,
            }
        else:
            return {
                xname: slice(minx, maxx),
                yname: slice(maxy, miny),
                tname: slice(date_min, date_max),
            }

    elif date_max is None and date_min is None:
        return {
            xname: slice(minx, maxx),
            yname: slice(miny, maxy),
        }

    elif date_max is None:
        return {
            xname: slice(minx, maxx),
            yname: slice(miny, maxy),
            tname: date_min,
        }

    else:
        return {
            xname: slice(minx, maxx),
            yname: slice(miny, maxy),
            tname: slice(date_min, date_max),
        }


def build_subset_tiff(
    bounds: npt.NDArray[np.double],
    xname: str,
    yname: str,
    toptobottom: bool,
    bname: str,
    band: int,
) -> Mapping[Any, Any]:
    """Create a dictionary to use with xarray .sel() method to subset TIFF data by space and band.

    Constructs a selection dictionary for xarray subsetting operations specifically
    for TIFF/raster data that handles spatial (x, y) dimensions and band selection.
    Automatically adjusts for coordinate system orientation.

    Args:
        bounds: Spatial bounds array in format [minx, miny, maxx, maxy].
        xname: Name of the x-dimension in the dataset.
        yname: Name of the y-dimension in the dataset.
        toptobottom: If True, y-coordinates increase from north to south. If False,
            y-coordinates increase from south to north.
        bname: Name of the band dimension in the dataset.
        band: Specific band number to select.

    Returns:
        Dictionary containing slice objects for xarray .sel() method with keys
        corresponding to dimension names and values as slice objects or exact values.

    Examples:
        >>> bounds = np.array([-180, -90, 180, 90])
        >>> subset_dict = build_subset_tiff(
        ...     bounds, 'x', 'y', True, 'band', 1
        ... )
        >>> raster_subset = raster_data.sel(subset_dict)

    """
    minx = bounds[0]
    maxx = bounds[2]
    miny = bounds[1]
    maxy = bounds[3]

    return (
        {
            xname: slice(minx, maxx),
            yname: slice(miny, maxy),
            bname: band,
        }
        if toptobottom
        else {
            xname: slice(minx, maxx),
            yname: slice(maxy, miny),
            bname: band,
        }
    )


def build_subset_tiff_da(
    bounds: npt.NDArray[np.double],
    xname: str,
    yname: str,
    toptobottom: int | bool,
) -> Mapping[Any, Any]:
    """Create a dictionary to use with xarray .sel() method to subset TIFF DataArray by space.

    Constructs a selection dictionary for xarray subsetting operations specifically
    for TIFF/raster DataArray objects that handles spatial (x, y) dimensions.
    Automatically adjusts for coordinate system orientation.

    Args:
        bounds: Spatial bounds array in format [minx, miny, maxx, maxy].
        xname: Name of the x-dimension in the dataset.
        yname: Name of the y-dimension in the dataset.
        toptobottom: If True or 1, y-coordinates increase from north to south.
            If False or 0, y-coordinates increase from south to north.

    Returns:
        Dictionary containing slice objects for xarray .sel() method with keys
        corresponding to dimension names and values as slice objects.

    Examples:
        >>> bounds = np.array([-180, -90, 180, 90])
        >>> subset_dict = build_subset_tiff_da(
        ...     bounds, 'x', 'y', True
        ... )
        >>> raster_subset = raster_dataarray.sel(subset_dict)

    """
    minx = bounds[0]
    maxx = bounds[2]
    miny = bounds[1]
    maxy = bounds[3]

    return (
        {
            xname: slice(minx, maxx),
            yname: slice(miny, maxy),
        }
        if toptobottom
        else {
            xname: slice(minx, maxx),
            yname: slice(maxy, miny),
        }
    )


def check_gridded_data_for_dimensions(ds: xr.Dataset, vars: list[str]) -> None:
    """Check that gridded data has the required dimensions.

    Checks each specified DataArray in an xarray Dataset to confirm that it
    has three dimensions and that the first dimension is 'time'. This is a
    pre-requisite for many gdptools processing functions.

    Args:
        ds: The xarray Dataset to validate.
        vars: A list of variable names within the dataset to check.

    Raises:
        KeyError: If any of the specified variables do not have exactly
            three dimensions or if 'time' is not the first dimension.

    """
    bad_vars = []

    for var in vars:
        da = ds[var]
        if len(da.shape) == 3:
            if next(iter(da.indexes)) == "time":
                continue
        else:
            bad_vars.append(var)

    if bad_vars:
        raise KeyError(
            "Cannot process these DataArrays because their dimensions do not match the "
            f"requirements of GDPtools: {bad_vars}"
        )

def get_stac_collection(collection_id: str) -> pystac.Collection:
    """Fetch a collection from the NHGF STAC catalog.

    Searches recursively through the catalog tree to find nested collections
    (e.g., 'conus404_daily' is nested under 'conus404').

    Args:
        collection_id: The collection identifier.

    Returns:
        The pystac Collection object.

    Raises:
        ProcessorException: If the collection is not found.
    """
    try:
        catalog = pystac.Catalog.from_file(NHGF_STAC_CATALOG_URL)
    except Exception as e:
        raise STACCatalogError(f"Failed to load NHGF STAC catalog: {e}") from e

    # Search recursively for the collection
    def find_collection(
        parent: pystac.Catalog | pystac.Collection,
        target_id: str,
        depth: int = 0,
        max_depth: int = 5,
    ) -> pystac.Collection | None:
        """Recursively search for a collection by ID."""
        if depth > max_depth:
            return None
        for child in parent.get_children():
            if child.id == target_id:
                return child
            # Search nested children
            result = find_collection(child, target_id, depth + 1, max_depth)
            if result is not None:
                return result
        return None

    collection = find_collection(catalog, collection_id)
    if collection is not None:
        return collection

    # Collection not found - provide helpful error with available options
    available = [c.id for c in catalog.get_children()]
    raise STACCatalogError(
        f"Collection '{collection_id}' not found in NHGF STAC catalog. "
        f"Top-level collections: {available[:10]}... "
        f"(Note: some collections have sub-collections, e.g., 'conus404/conus404_daily')"
    )
