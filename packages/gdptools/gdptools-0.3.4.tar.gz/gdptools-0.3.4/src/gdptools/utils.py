"""Ancillary function to support core functions in helper.py."""

from __future__ import annotations

import datetime
import json
import logging
import math
import sys
import time
import warnings
from collections.abc import Iterator
from pathlib import Path
from typing import Any, Literal

import geopandas as gpd
import geopandas.sindex
import netCDF4
import numpy as np
import numpy.typing as npt
import pandas as pd
import rioxarray as rxr
import xarray as xr
from pyproj import CRS, Transformer
from pyproj.exceptions import ProjError
from shapely import centroid, get_coordinates
from shapely.geometry import LineString, Point, Polygon, box

from gdptools.data.odap_cat_data import CatClimRItem

logger = logging.getLogger(__name__)

SOURCE_ORIGIN = Literal["source", "target"]


def _is_valid_crs(crs_candidate: int | str | CRS) -> bool:
    """Check if the provided CRS candidate is valid."""
    try:
        CRS.from_user_input(crs_candidate)
        return True
    except Exception as e:
        # Optionally, print or log the error for debugging
        print(f"Invalid CRS: {e}")
        return False

class ReprojectionError(Exception):
    """Custom exception for errors during reprojection."""

    pass


def _check_empty_geometries(gdf: gpd.GeoDataFrame, source_type: SOURCE_ORIGIN) -> None:
    """Check for empty geometries in a GeoDataFrame after reprojection.

    Args:
        gdf (gpd.GeoDataFrame): The GeoDataFrame to check.
        source_type (SOURCE_ORIGIN): Indicates whether the GeoDataFrame
            represents the "source" or "target" geometries. Used for
            informative error messages.

    Raises:
        ReprojectionError: If any geometry in the GeoDataFrame is empty.

    """
    print(f"     - checking {source_type} for empty geometries")
    if gdf.is_empty.any():
        raise ReprojectionError(f"{source_type} GeoDataFrame contains empty geometries after reprojection.")


def _check_invalid_geometries(gdf: gpd.GeoDataFrame, source_type: SOURCE_ORIGIN) -> None:
    """Check and attempt to fix invalid geometries in a GeoDataFrame.

    This function checks for invalid geometries within the provided
    GeoDataFrame. If invalid geometries are found, it attempts to make them
    valid using the `_make_valid` function.

    Args:
        gdf (gpd.GeoDataFrame): The GeoDataFrame to check for invalid
            geometries. Modified in place if invalid geometries are found.
        source_type (SOURCE_ORIGIN): Indicates whether the GeoDataFrame
            represents the "source" or "target" geometries. Used for
            informative print statements.

    """
    print(f"     - checking the {source_type} geodataframe for invalid geometries")
    invalid_geoms = gdf[~gdf.is_valid]
    if not invalid_geoms.empty:
        print(f"     - validating reprojected {source_type} geometries")
        _make_valid(gdf)
        # raise ReprojectionError("GeoDataFrame contains invalid geometries after reprojection.")


def _check_grid_file_availability(
    source_crs: int | str | CRS, new_crs: int | str | CRS, source_type: SOURCE_ORIGIN
) -> None:
    """Check availability of grid files for transformation.

    Verifies if necessary grid files are accessible for the specified source
    and target CRS.  Attempts a sample transformation to detect potential
    issues.

    Args:
        source_crs (Union[int, str, CRS]): Source CRS.
        new_crs (Union[int, str, CRS]): Target CRS.
        source_type (SOURCE_ORIGIN): "source" or "target", used for error
            messages.

    Raises:
        ReprojectionError: If grid files are unavailable or a transformation
            error occurs.

    """
    error_message = (
        f"Reprojecting the {source_type} polygons failed because PROJ could not download the required "
        "grid shift files. If you run behind a firewall or in an offline environment, install the "
        "`proj-data` package (or copy the contents of a PROJ data directory) and set the following "
        "environment variables before running gdptools:\n"
        "  * PROJ_NETWORK=OFF\n"
        "  * PROJ_DATA=<path to your local proj/share> (or PROJ_LIB for older releases)\n"
        "  * PROJ_CURL_CA_BUNDLE=<path to your CA bundle> (optional when TLS interception occurs).\n"
        "See the PROJ docs <https://proj.org/usage/network.html> for more details."
    )
    try:
        source_crs = CRS.from_user_input(source_crs)
        target_crs = CRS.from_user_input(new_crs)
        transformer = Transformer.from_crs(source_crs, target_crs, always_xy=True)

        # Attempt a transformation on a sample coordinate
        x, y = transformer.transform(0, 0)
        if x == float("inf") or y == float("inf"):
            raise ReprojectionError(
                f"Required grid files are not available for accurate transformation: {error_message}"
            )
    except ProjError as e:
        error_message = (
            f"Projection error while reprojecting {source_type} polygons: {e}. "
            "Please check the CRS and ensure that the required grid files are available."
        )
        logger.error(error_message)
        raise ReprojectionError(error_message) from e


def _check_reprojection(
    gdf: gpd.GeoDataFrame, new_crs: int | str | CRS, source_crs: int | str | CRS, source_type: SOURCE_ORIGIN
) -> None:
    """Validate reprojection of a GeoDataFrame.

    Checks for grid file availability, invalid geometries, and empty
    geometries after reprojection.

    Args:
        gdf (gpd.GeoDataFrame): The reprojected GeoDataFrame.
        new_crs (Union[int, str, CRS]): Target CRS.
        source_crs (Union[int, str, CRS]): Source CRS.
        source_type (SOURCE_ORIGIN): "source" or "target", for error messages.

    Raises:
        RuntimeError: If reprojection issues are detected.

    """
    try:
        _check_grid_file_availability(source_crs, new_crs, source_type=source_type)
        _check_invalid_geometries(gdf, source_type=source_type)
        _check_empty_geometries(gdf, source_type=source_type)
    except Exception as e:
        error_message = (
            f"Error during reprojection of the {source_type} polygons."
            f"This can occur when the {source_type} polygons are invalid, or the reprojection failed."
        )
        logger.error(error_message)
        raise RuntimeError(error_message) from e


def _reproject_for_weight_calc(
    target_poly: gpd.GeoDataFrame,
    source_poly: gpd.GeoDataFrame,
    wght_gen_crs: int | str | CRS,
) -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]:
    """Reprojects source and target GeoDataFrames to a specified CRS and checks for reprojection errors.

    Args:
        target_poly (gpd.GeoDataFrame): The target GeoDataFrame to be reprojected.
        source_poly (gpd.GeoDataFrame): The source GeoDataFrame to be reprojected.
        wght_gen_crs (Union[int, str, CRS]): The CRS to reproject the GeoDataFrames to. This can be an EPSG code,
            string, or pyproj CRS object.

    Returns:
        tuple[gpd.GeoDataFrame, gpd.GeoDataFrame]: The reprojected target and source GeoDataFrames.

    Raises:
        ReprojectionError: If there are any reprojection errors or issues with the CRS.

    """
    start = time.perf_counter()
    try:
        source_poly_reprojected = _reproject_and_check(
            message="     - reprojecting and validating source polygons",
            geom=source_poly,
            wght_gen_crs=wght_gen_crs,
            source_type="source",
        )
    except ReprojectionError as e:
        logger.error(f"Failed to reproject source polygons: {e}")
        raise
    try:
        target_poly_reprojected = _reproject_and_check(
            message="     - reprojecting and validating target polygons",
            geom=target_poly,
            wght_gen_crs=wght_gen_crs,
            source_type="target",
        )
    except ReprojectionError as e:
        logger.error(f"Failed to reproject target polygons: {e}")
        raise
    end = time.perf_counter()
    print(f"Reprojecting to: {wght_gen_crs} and validating polygons finished in {round(end - start, 2)} seconds")
    return target_poly_reprojected, source_poly_reprojected


def _reproject_and_check(
    message: str, geom: gpd.GeoDataFrame, wght_gen_crs: str | int | CRS, source_type: SOURCE_ORIGIN
) -> gpd.GeoDataFrame:
    """Reprojects a GeoDataFrame to a specified CRS and checks for reprojection validity.

    This function prints a message, reprojects the provided geometry, and verifies the reprojection's integrity.
    If any issues arise during the reprojection check, an error is logged, and the exception is raised.

    Args:
        message (str): A message to be printed before the reprojection process.
        geom (gpd.GeoDataFrame): The GeoDataFrame containing the geometries to be reprojected.
        wght_gen_crs (Union[str, int, CRS]): The target CRS to which the geometries will be reprojected.
        source_type (SOURCE_ORIGIN): Indicates the origin of the data, either "source" or "target".

    Raises:
        Exception: If there is an error during the reprojection process or the validity check.

    Returns:
        gpd.GeoDataFrame: The reprojected GeoDataFrame.

    """
    print(message)
    # Reproject the source geometry
    result = geom.to_crs(wght_gen_crs)
    try:
        _check_reprojection(result, wght_gen_crs, geom.crs, source_type=source_type)
    except Exception as e:
        logger.error(f"Reprojection error: {e}")
        raise

    return result


def _get_grid_cell_sindex(grid_cells: gpd.GeoDataFrame) -> geopandas.sindex:
    """Build and return a spatial index for grid cells.

    Args:
        grid_cells (gpd.GeoDataFrame): GeoDataFrame containing grid cell geometries.

    Returns:
        geopandas.sindex: The spatial index built from `grid_cells`.

    """
    start = time.perf_counter()
    spatial_index = grid_cells.sindex
    # print(type(spatial_index))
    end = time.perf_counter()
    print(f"Spatial index generations finished in {round(end - start, 2)} second(s)")
    return spatial_index


def _check_grid_cell_crs(grid_cells: gpd.GeoDataFrame) -> None:
    if not grid_cells.crs:
        error_string = f"grid_cells don't contain a valid crs: {grid_cells.crs}"
        raise ValueError(error_string)


def _check_feature_crs(poly: gpd.GeoDataFrame) -> None:
    if not poly.crs:
        error_string = f"polygons don't contain a valid crs: {poly.crs}"
        raise ValueError(error_string)


def _check_target_poly_idx(poly: gpd.GeoDataFrame, poly_idx: str) -> None:
    if poly_idx not in poly.columns:
        error_string = f"Error: target_poly_idx ({poly_idx}) is not found in the poly ({poly.columns})"
        raise ValueError(error_string)


def _check_source_poly_idx(poly: gpd.GeoDataFrame, poly_idx: str | list[str]) -> None:
    if isinstance(poly_idx, str):
        poly_idx = [poly_idx]
    for id in poly_idx:
        if id not in poly.columns:
            error_string = f"Error: source_poly_idx ({id}) is not found in the poly ({poly.columns})"
            raise ValueError(error_string)


def _get_print_on(numrows: int) -> int:
    """Return an interval to print progress of run_weights() function.

    Args:
        numrows (int): Number of rows: as in number of polygons

    Returns:
        int: Reasonable interval to print progress statements. Prints at about 10%

    """
    if numrows <= 10:  # pragma: no cover
        print_on = 1
    elif numrows <= 100:
        print_on = 10
    elif numrows <= 1000:
        print_on = 100
    elif numrows <= 10000:
        print_on = 1000
    elif numrows <= 100000:
        print_on = 10000
    else:
        print_on = 50000
    return int(print_on)


def _get_crs(crs_in: str | int | CRS) -> CRS:
    """Return pyproj.CRS given integer or string.

    Args:
        crs_in (Union[str, int, CRS]): integer: epsg code or pyproj string

    Returns:
        CRS: pyproj.CRS

    """
    # if type(crs_in) == int:
    #     in_crs = CRS.from_epsg(crs_in)
    # elif type(crs_in) == str:
    #     in_crs = CRS.from_proj4(crs_in)
    return CRS.from_user_input(crs_in)


def _get_cells_poly(
    xr_a: xr.Dataset | xr.DataArray,
    x: str,
    y: str,
    crs_in: str | int | CRS,
    verbose: bool | None = False,
) -> gpd.GeoDataFrame:
    """Get cell polygons associated with "nodes" in xarray gridded data.

    Args:
        xr_a (Union[xr.Dataset, xr.DataArray]): Source xarray dataset or dataarray.
        x (str): Name of the x coordinate variable in the xarray object.
        y (str): Name of the y coordinate variable in the xarray object.
        crs_in (Union[str, int, CRS]): Projection of the xarray object. Can be an integer (EPSG code),
            string (proj4 string), or pyproj CRS object.
        verbose (Optional[bool], optional): Provide verbose response. Defaults to False.

    Returns:
        gpd.GeoDataFrame: A GeoDataFrame of grid-cell polygons calculated as follows:

        1) The polygons surrounding each node, where for each node at
           (i, j) the 4 surrounding polygons tpoly1a, tpoly2a, tpoly3a
           tpoly4a are calculated.

        (i-1, j+1)    (i, j+1)  (i+1, j+1)
            *...........*...........*
            .           .           .
            .           .           .
            . (tpoly3a) . (tpoly2a) .
            .           .           .
            .           .           .
        (i-1, j)      (i, j)    (i+1, j)
            *...........*...........*
            .           .           .
            .           .           .
            . (tpoly4a) . (tpoly1a) .
            .           .           .
            .           .           .
            *...........*...........*
        (i-1, j-1)    (i, j-1)  (i+1, j-1)

        2) The centroid is calculated for each of the 4 polygons
           in step 1, from with the bonding polygon of the node
           is determined.
            *..........*..........*
            .          .          .
            .          .          .
            .    p3----------p2   .
            .    |     .      |   .
            .    |     .      |   .
            *....|.....*......|...*
            .    |     .      |   .
            .    |     .      |   .
            .    p4----------p1   .
            .          .          .
            .          .          .
            *..........*..........*

    The grid-cell polygon surounding the node/vertex at (i, j) is
    [p1, p2, p3, p4, p1]

        This is to account for both rectangular and non-rectangular
        grid geometries.

    """
    tlon = xr_a[x]
    tlat = xr_a[y]
    in_crs = crs_in

    lon, lat = np.meshgrid(tlon, tlat)
    poly = []
    if verbose:
        logger.info("calculating surrounding cell vertices")
    start = time.perf_counter()

    tpoly1a = [
        Polygon(
            [
                [lon[i, j], lat[i, j]],
                [lon[i, j - 1], lat[i, j - 1]],
                [lon[i + 1, j - 1], lat[i + 1, j - 1]],
                [lon[i + 1, j], lat[i + 1, j]],
            ]
        )
        for i in range(1, lon.shape[0] - 1)
        for j in range(1, lon.shape[1] - 1)
    ]
    tpoly2a = [
        Polygon(
            [
                [lon[i, j], lat[i, j]],
                [lon[i + 1, j], lat[i + 1, j]],
                [lon[i + 1, j + 1], lat[i + 1, j + 1]],
                [lon[i, j + 1], lat[i, j + 1]],
            ]
        )
        for i in range(1, lon.shape[0] - 1)
        for j in range(1, lon.shape[1] - 1)
    ]
    tpoly3a = [
        Polygon(
            [
                [lon[i, j], lat[i, j]],
                [lon[i, j + 1], lat[i, j + 1]],
                [lon[i - 1, j + 1], lat[i - 1, j + 1]],
                [lon[i - 1, j], lat[i - 1, j]],
            ]
        )
        for i in range(1, lon.shape[0] - 1)
        for j in range(1, lon.shape[1] - 1)
    ]
    tpoly4a = [
        Polygon(
            [
                [lon[i, j], lat[i, j]],
                [lon[i - 1, j], lat[i - 1, j]],
                [lon[i - 1, j - 1], lat[i - 1, j - 1]],
                [lon[i, j - 1], lat[i, j - 1]],
            ]
        )
        for i in range(1, lon.shape[0] - 1)
        for j in range(1, lon.shape[1] - 1)
    ]
    end = time.perf_counter()
    if verbose:
        logger.info(f"finished calculating surrounding cell vertices in {round(end - start, 2)} second(s)")

    # print(len(lon_n), len(lat_n), type(lon_n), np.shape(lon_n))
    numcells = len(tpoly1a)
    index = np.array(range(numcells))
    i_index = np.empty(numcells)
    j_index = np.empty(numcells)
    count = 0
    for i in range(1, lon.shape[0] - 1):
        for j in range(1, lon.shape[1] - 1):
            i_index[count] = i
            j_index[count] = j
            count += 1

    if verbose:
        logger.info("calculating centroids")

    start = time.perf_counter()
    # tpoly1 = [Polygon(tpoly1a)]
    p1 = get_coordinates(centroid(tpoly1a))

    # tpoly2 = [Polygon(tpoly2a)]
    p2 = get_coordinates(centroid(tpoly2a))

    # tpoly3 = [Polygon(tpoly3a)]
    p3 = get_coordinates(centroid(tpoly3a))

    # tpoly4 = [Polygon(tpoly4a)]
    p4 = get_coordinates(centroid(tpoly4a))
    end = time.perf_counter()

    if verbose:
        logger.info(f"finished calculating surrounding cell vertices  in {round(end - start, 2)} second(s)")
    lon_point_list = [[p1[i][0], p2[i][0], p3[i][0], p4[i][0]] for i in range(numcells)]
    lat_point_list = [[p1[i][1], p2[i][1], p3[i][1], p4[i][1]] for i in range(numcells)]
    poly = [Polygon(zip(lon_point_list[i], lat_point_list[i])) for i in range(numcells)]  # noqa B905
    df = pd.DataFrame({"i_index": i_index, "j_index": j_index})
    return gpd.GeoDataFrame(df, index=index, geometry=poly, crs=in_crs)


def _build_subset_cat(
    cat_cr: CatClimRItem,
    bounds: tuple[np.double, np.double, np.double, np.double],
    date_min: str,
    date_max: str | None = None,
) -> dict[Any, Any]:
    """Create a dictionary to use with xarray .sel() method to subset by time and space.

    Args:
        cat_cr (CatClimRItem): CatClimRItem object containing metadata for the dataset.
        bounds (npt.NDArray[np.double]): Bounding box coordinates in the format (left, bottom, right, top).
        date_min (str): Date string in ISO format (YYYY-MM-DD) representing the minimum date for subsetting.
        date_max (str, optional): Date string in ISO format (YYYY-MM-DD) representing the maximum date for subsetting.
            Defaults to None.

    Returns:
        dict: A dictionary to use with xarray's .sel() method to subset by time and space.

    """
    xname = cat_cr.X_name
    yname = cat_cr.Y_name
    # print(type(xname), type(yname))
    tname = cat_cr.T_name
    minx = bounds[0]
    maxx = bounds[2]
    miny = bounds[1]
    maxy = bounds[3]
    gridorder = bool(cat_cr.toptobottom)
    if not gridorder:
        return (
            {
                xname: slice(minx, maxx),
                yname: slice(maxy, miny),
                tname: date_min,
            }
            if date_max is None
            else {
                xname: slice(minx, maxx),
                yname: slice(maxy, miny),
                tname: slice(date_min, date_max),
            }
        )

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


def _read_shp_file(shp_file: str | Path | gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Read shapefile.

    Args:
        shp_file (Union[str, gpd.GeoDataFrame]): Shapefile path or GeoDataFrame.

    Returns:
        gpd.GeoDataFrame: GeodataFrame containing the shapefile data.

    """
    if isinstance(shp_file, gpd.GeoDataFrame):
        return shp_file.reset_index()
    gdf = gpd.read_file(shp_file)
    return gdf.reset_index()


def _get_shp_file(
    shp_file: gpd.GeoDataFrame, cat_cr: CatClimRItem, is_degrees: bool
) -> tuple[gpd.GeoDataFrame, tuple[np.double, np.double, np.double, np.double]]:
    """Return GeoDataFrame and bounds of shapefile.

    Args:
        shp_file (gpd.GeoDataFrame): GeodataFrame containing the shapefile data.
        cat_cr (CatClimRItem): CatClimRItem object containing metadata for the dataset.
        is_degrees (bool): Boolean indicating if the coordinates are in degrees.

    Returns:
        tuple[gpd.GeoDataFrame, tuple[np.double, np.double, np.double, np.double]]: The GeoDataFrame and its bounds
        as (minx, miny, maxx, maxy).

    """
    # read shapefile, calculate total_bounds, and project to grid's projection
    gdf = shp_file.to_crs(cat_cr.proj)
    # buffer polygons bounding box by twice max resolution of grid
    bbox = box(*gdf.total_bounds)
    # if
    gdf_bounds = bbox.buffer(2.0 * max(cat_cr.resX, cat_cr.resY)).bounds  # type: ignore
    if is_degrees and (gdf_bounds[0] < -180.0) & (gdf_bounds[2] > 180.0):
        newxmax = 180.0 - (abs(gdf_bounds[0]) - 180.0)
        newxmin = -180.0 + (abs(gdf_bounds[2]) - 180.0)
        gdf_bounds = (newxmin, gdf_bounds[1], newxmax, gdf_bounds[3])
        print("Warning: The feature data crosses the anitmeridian.")

    return gdf, gdf_bounds


def _is_degrees_nc(ds: xr.Dataset, x_name: str, y_name: str) -> bool:
    """Test if "degree" or "degrees" is present in the units attribute of both X and Y coordinates.

    Args:
        ds (xr.Dataset): The dataset.
        x_name (str): The name of the X coordinate.
        y_name (str): The name of the Y coordinate.

    Returns:
        bool: True if "degree" or "degrees" is present in the units attribute of both X and Y coordinates,
            False otherwise.

    Raises:
        ValueError: If the units attribute is missing from either X or Y coordinate.

    """
    try:
        x_units = ds[x_name].attrs["units"]
        y_units = ds[y_name].attrs["units"]
        if "degree" in x_units.lower() or "degree" in y_units.lower():
            return True
        return False
    except KeyError as e:
        raise ValueError(
            f"Both {x_name} and {y_name} coordinates must have units attribute. Add units to coordinates of the dataset"
        ) from e


def _is_degrees(ds: xr.Dataset, cat_cr: CatClimRItem) -> bool:
    """Test if degrees in attributes on longitude.

    Args:
        ds (xr.Dataset): The xarray dataset.
        cat_cr (CatClimRItem): The CatClimRItem.

    Returns:
        bool: True if "degree" or "degrees" is in the units attribute of both X and Y coordinates, False otherwise.

    Raises:
        ValueError: If the "units" attribute is missing from either X or Y coordinate.

    """
    try:
        x_units = ds[cat_cr.X_name].attrs["units"]
        y_units = ds[cat_cr.Y_name].attrs["units"]
        if "degree" in x_units.lower() or "degree" in y_units.lower():
            return True
        return False
    except KeyError as e:
        raise ValueError(
            f"Both {ds[cat_cr.X_name]} and {ds[cat_cr.Y_name]} coordinates must have units attribute."
        ) from e


def _is_lon_0_360(vals: npt.NDArray[np.double]) -> bool:
    """Test if longitude spans 0-360.

    Args:
        vals (npt.NDArray[np.double]): Values to check.

    Returns:
        bool: Returns True if the longitude values span 0-360 degrees, False otherwise.

    """
    result = False
    if (vals[0] > 180.0) & (np.min(vals) > 0.0):
        result = True  # False
    elif (np.max(vals) > 180.0) & (np.min(vals) > 180.0):
        result = True  # False
    elif np.max(vals) > 180.0:
        result = True

    return result


def _get_shp_bounds_w_buffer(
    gdf: gpd.GeoDataFrame,
    ds: xr.DataArray | xr.Dataset,
    crs: int | str | CRS,
    lon: str,
    lat: str,
) -> npt.NDArray[np.double]:
    """Calculate buffered bounding box of a GeoDataFrame.

    Calculates the bounding box of the input GeoDataFrame after reprojecting
    it to the specified CRS. The bounding box is then buffered by twice the
    maximum resolution of the gridded dataset.

    Args:
        gdf (gpd.GeoDataFrame): The GeoDataFrame to calculate the bounds for.
        ds (Union[xr.DataArray, xr.Dataset]): The gridded dataset, used to
            determine the buffer size based on its resolution.
        crs (Union[int, str, CRS]): The target CRS for reprojection and bounds calculation.
        lon (str): Name of the longitude coordinate in `ds`.
        lat (str): Name of the latitude coordinate in `ds`.

    Returns:
        npt.NDArray[np.double]: The buffered bounding box as a NumPy array.

    Raises:
        ValueError: If the GeoDataFrame cannot be reprojected to the specified CRS.

    """
    bbox = box(*gdf.to_crs(crs).total_bounds)
    if bbox.area == np.nan:
        raise ValueError(f"unable to reproject target_gdf's projection {gdf.crs} to proj_ds{crs}")
    return np.asarray(
        bbox.buffer(2 * max(max(np.diff(ds[lat].values)), max(np.diff(ds[lon].values)))).bounds  # type: ignore
    )


def _check_for_intersection(cat_cr: CatClimRItem, gdf: gpd.GeoDataFrame) -> tuple[bool, bool, bool]:
    """Check for intersection between features and grid.

    This function checks if the geometries in the GeoDataFrame intersect with
    the bounding box of the gridded dataset described by the CatClimRItem. It
    also determines if the gridded dataset uses degrees as units and if its
    longitude spans 0-360 degrees.

    Args:
        cat_cr (CatClimRItem): Metadata describing the gridded dataset.
        gdf (gpd.GeoDataFrame): GeoDataFrame containing the geometries.

    Returns:
        tuple[bool, bool, bool]: A tuple containing three boolean values:
            - is_intersect (bool): True if the geometries intersect the
              grid's bounding box, False otherwise.
            - is_degrees (bool): True if the gridded dataset uses degrees as
              units, False otherwise.
            - is_0_360 (bool): True if the gridded dataset's longitude spans
              0-360 degrees, False otherwise.

    """
    is_degrees = False
    is_intersect = True
    is_0_360 = False
    ds_url = cat_cr.URL
    ds = xr.open_dataset(ds_url + "#fillmismatch", decode_coords=True)
    xvals = ds[cat_cr.X_name]
    yvals = ds[cat_cr.Y_name]
    minx = xvals.values.min()
    maxx = xvals.values.max()
    miny = yvals.values.min()
    maxy = yvals.values.max()
    ds_bbox = box(minx, miny, maxx, maxy)
    bounds = _get_shp_bounds_w_buffer(
        gdf,
        ds,
        cat_cr.crs,
        cat_cr.X_name,
        cat_cr.Y_name,
    )
    is_degrees = _is_degrees(ds=ds, cat_cr=cat_cr)
    if is_degrees & (not ds_bbox.intersects(box(*np.asarray(bounds).tolist()))):
        is_intersect = False
        is_0_360 = _is_lon_0_360(xvals.values)
        if is_0_360:
            warning_string = (
                "0-360 longitude crossing the international date line encountered.\n"
                "Longitude coordinates will be 0-360 in output."
            )
            warnings.warn(warning_string, stacklevel=2)

    ds.close()
    return is_intersect, is_degrees, is_0_360


def _check_for_intersection_nc(
    ds: xr.Dataset,
    x_name: str,
    y_name: str,
    proj: int | str | CRS,
    gdf: gpd.GeoDataFrame,
) -> tuple[bool, bool, bool]:
    """Check for intersection between features and grid.

    This function checks if the geometries in the GeoDataFrame intersect with
    the bounding box of the gridded dataset. It also determines if the gridded
    dataset uses degrees as units and if its longitude spans 0-360 degrees.

    Args:
        ds (xr.Dataset): The gridded dataset.
        x_name (str): Name of the x-coordinate.
        y_name (str): Name of the y-coordinate.
        proj (Union[int, str, CRS]): Projection of the dataset.
        gdf (gpd.GeoDataFrame): GeoDataFrame containing the geometries.

    Returns:
        tuple[bool, bool, bool]: A tuple containing:
            - is_intersect: True if geometries intersect grid's bounding box
            - is_degrees: True if dataset uses degrees as units
            - is_0_360: True if longitude spans 0-360 degrees

    """
    is_degrees = False
    is_intersect = True
    is_0_360 = False

    xvals = ds[x_name]
    yvals = ds[y_name]
    minx = xvals.values.min()
    maxx = xvals.values.max()
    miny = yvals.values.min()
    maxy = yvals.values.max()
    ds_bbox = box(minx, miny, maxx, maxy)
    bounds = _get_shp_bounds_w_buffer(
        gdf,
        ds,
        proj,
        x_name,
        y_name,
    )
    is_degrees = _is_degrees_nc(ds=ds, x_name=x_name, y_name=y_name)
    if is_degrees & (not ds_bbox.intersects(box(*np.asarray(bounds).tolist()))):
        is_intersect = False
        is_0_360 = _is_lon_0_360(xvals.values)
        if is_0_360:
            warning_string = (
                "0-360 longitude crossing the international date line encountered.\n"
                "Longitude coordinates will be 0-360 in output."
            )
            warnings.warn(warning_string, stacklevel=2)

    return is_intersect, is_degrees, is_0_360


def _get_data_via_catalog(
    cat_cr: CatClimRItem,
    bounds: tuple[np.double, np.double, np.double, np.double],
    begin_date: str,
    end_date: str | None = None,
    rotate_lon: bool | None = False,
) -> xr.DataArray:
    """Retrieve data from a catalog using specified parameters.

    This function opens a dataset from a URL, optionally rotates longitude coordinates,
    and selects a subset of the data based on provided bounds and dates.

    Args:
        cat_cr (CatClimRItem): Catalog item containing dataset metadata.
        bounds (Tuple[np.double, np.double, np.double, np.double]): Bounding box coordinates.
        begin_date (str): Start date for data selection.
        end_date (Optional[str], optional): End date for data selection. Defaults to None.
        rotate_lon (Optional[bool], optional): Whether to rotate longitude coordinates. Defaults to False.

    Returns:
        xr.DataArray: Selected data array from the dataset.

    """
    ds_url = cat_cr.URL
    with  xr.open_dataset(ds_url + "#fillmismatch", decode_coords=True) as ds:
        if rotate_lon:
            lon = cat_cr.X_name
            ds.coords[lon] = (ds.coords["lon"] + 180) % 360 - 180
            ds = ds.sortby(ds[lon])

        # get grid data subset to polygons buffered bounding box
        ss_dict = _build_subset_cat(cat_cr, bounds, begin_date, end_date)
        # gridMET requires the '#fillmismatch' see:
        # https://discourse.oceanobservatories.org/
        # t/
        # accessing-data-on-thredds-opendap-via-python-netcdf4-or-xarray
        # -dealing-with-fillvalue-type-mismatch-error/61

        varname = cat_cr.varname
        return ds[varname].sel(**ss_dict)


def _get_weight_df(wght_file: str | pd.DataFrame, poly_idx: str) -> pd.DataFrame:
    """Read weight file into a Pandas DataFrame.

    This function reads a weight file, which can be either a CSV file path (str)
    or a Pandas DataFrame. The file/DataFrame is expected to contain columns
    "i", "j", "wght", and a column specified by `poly_idx`. The data types
    of these columns are enforced.

    Args:
        wght_file (Union[str, pd.DataFrame]): Path to the weight file (CSV) or
            a Pandas DataFrame containing the weights.
        poly_idx (str): Name of the column containing polygon indices.

    Returns:
        pd.DataFrame: Pandas DataFrame containing the weights, with enforced
            data types for "i", "j", "wght", and `poly_idx` columns.

    Raises:
        SystemExit: If `wght_file` is neither a string nor a Pandas DataFrame.

    """
    if isinstance(wght_file, pd.DataFrame):
        # wghts = wght_file.copy()
        wghts = wght_file.astype({"i": int, "j": int, "wght": float, poly_idx: str})
    elif isinstance(wght_file, str):
        wghts = pd.read_csv(wght_file, dtype={"i": int, "j": int, "wght": float, poly_idx: str})
    else:
        sys.exit("wght_file must be one of string or pandas.DataFrame")
    return wghts


def _date_range(p_start: str, p_end: str, intv: int) -> Iterator[str]:
    """Generate a sequence of dates between two points.

    This function creates an iterator that yields evenly spaced dates between
    a start and end date. The number of intervals is specified by the `intv` parameter.

    Args:
        p_start (str): Start date in 'YYYY-MM-DD' format.
        p_end (str): End date in 'YYYY-MM-DD' format.
        intv (int): Number of intervals to divide the date range.

    Yields:
        str: Dates in 'YYYY-MM-DD' format at each interval, including start and end dates.

    """
    start = datetime.strptime(p_start, "%Y-%m-%d")
    end = datetime.strptime(p_end, "%Y-%m-%d")
    diff = (end - start) / intv
    for i in range(intv):
        yield (start + diff * i).strftime("%Y-%m-%d")
    yield end.strftime("%Y-%m-%d")


def _get_catalog_time_increment(param: dict) -> tuple[int, str]:
    """Extract time increment and units from a dictionary.

    This function extracts the time increment value and its units from a
    dictionary, typically representing metadata. It assumes the 'interval'
    key contains a string like "1 days" or "3 months".

    Args:
        param (dict): Dictionary containing time interval information.

    Returns:
        tuple[int, str]: A tuple containing the increment value (int) and its units (str).

    """
    interval = str(param.get("interval")).split(" ")
    return int(interval[0]), str(interval[1])


def _get_dataframe(object: str | pd.DataFrame) -> pd.DataFrame:
    """Convert input to a Pandas DataFrame.

    This function takes either a JSON string or a Pandas DataFrame and
    returns a Pandas DataFrame. If a JSON string is provided, it is parsed
    and converted to a DataFrame.

    Args:
        object (Union[str, pd.DataFrame]): Input to be converted to a DataFrame.
            Can be a JSON string or an existing Pandas DataFrame.

    Returns:
        pd.DataFrame: A Pandas DataFrame representing the input data.

    """
    if isinstance(object, str):
        return pd.DataFrame.from_dict(json.loads(object))
    else:
        return object


def _get_default_val(native_dtype: np.dtype) -> int | float:
    """Return the default NetCDF fill value for a given NumPy data type.

    Args:
        native_dtype (np.dtype): A NumPy data type instance (e.g., np.dtype('int32') or np.float64).

    Returns:
        int | float: The default fill value as defined in `netCDF4.default_fillvals`.

    Raises:
        TypeError: If the data type is not an integer or floating-point type.

    """
    if native_dtype.kind == "i":
        dfval = netCDF4.default_fillvals["i8"]
    elif native_dtype.kind == "f":
        dfval = netCDF4.default_fillvals["f8"]
    else:
        raise TypeError(f"gdptools currently only supports int and float types. The value type here is {native_dtype}")

    return dfval


def _get_interp_array(
    n_geo: int,
    nts: int,
    native_dtype: np.dtype[Any],
    default_val: int | float
) -> npt.NDArray[np.int_] | npt.NDArray[np.double]:
    """Create an interpolation array with default fill values.

    This function creates a 2D NumPy array for interpolation, with dimensions
    determined by the number of geometries and time steps. The array is filled
    with a default value based on the input data type.

    Args:
        n_geo (int): Number of geometries.
        nts (int): Number of time steps.
        native_dtype (np.dtype[Any]): The native data type of the array.
        default_val (Union[int, float]): The default fill value for the array.

    Returns:
        Union[npt.NDArray[np.int_], npt.NDArray[np.double]]: A 2D NumPy array
        filled with the default value, with integer or float type.

    Raises:
        TypeError: If the data type is not an integer or float.

    """
    if native_dtype.kind == "i":
        # val_interp = np.empty((nts, n_geo), dtype=np.dtype("int64"))
        val_interp = np.full((nts, n_geo), dtype=np.dtype("int64"), fill_value=default_val)
    elif native_dtype.kind == "f":
        # val_interp = np.empty((nts, n_geo), dtype=np.dtype("float64"))
        val_interp = np.full((nts, n_geo), dtype=np.dtype("float64"), fill_value=default_val)
    else:
        raise TypeError(f"gdptools currently only supports int and float types.The value type here is {native_dtype}")

    return val_interp


def _get_top_to_bottom(data: xr.Dataset | xr.DataArray, y_coord: str) -> bool:
    """Determine the orientation of the y-coordinate values.

    This function checks whether the y-coordinate values are in ascending or
    descending order. It helps determine the top-to-bottom orientation of
    gridded data.

    Args:
        data (Union[xr.Dataset, xr.DataArray]): The input xarray Dataset or DataArray.
        y_coord (str): The name of the y-coordinate in the dataset.

    Returns:
        bool: True if the y-coordinate values are in ascending order (top-to-bottom),
              False if they are in descending order.

    """
    yy = data.coords[y_coord].values
    return yy[0] <= yy[-1]


def _get_xr_dataset(ds: str | xr.Dataset | Path) -> xr.Dataset:
    """Open or validate an xarray Dataset.

    This function handles different input types for obtaining an xarray Dataset.
    It supports opening datasets from URLs, file paths, or directly passing an
    existing xarray Dataset.

    Args:
        ds (Union[str, xr.Dataset, Path]): Input dataset source. Can be a URL,
            file path, or an existing xarray Dataset.

    Returns:
        xr.Dataset: A validated xarray Dataset.

    Raises:
        TypeError: If the input is an xarray DataArray or an unsupported type.

    """
    if isinstance(ds, str):
        # Check if it's a local file path or a URL
        if ds.startswith(('http://', 'https://', 'ftp://')) or '://' in ds:
            # For URLs, use the fillmismatch workaround
            return xr.open_dataset(ds + "#fillmismatch", decode_coords=True)
        else:
            # For local file paths, open directly
            return xr.open_dataset(ds, decode_coords=True)
    if isinstance(ds, Path):
        return xr.open_dataset(ds, decode_coords=True)
    elif isinstance(ds, xr.Dataset):
        return ds
    elif isinstance(ds, xr.DataArray):
        raise TypeError("Expected xarray.Dataset, not xarray.DataArray")
    else:
        raise TypeError("Invalid xarray dataset, must be a URL or xarray Dataset")


def _get_rxr_dataset(ds: str | xr.DataArray | xr.Dataset) -> xr.DataArray | xr.Dataset | str:
    """Open or validate a raster dataset for rioxarray workflows.

    This helper accepts either a path/URL to a raster readable by rioxarray,
    or an existing ``xarray.DataArray``/``xarray.Dataset``. For error cases used by
    unit tests, it returns a human-readable string rather than raising to allow
    graceful handling in calling code.

    Args:
        ds (str | xr.DataArray | xr.Dataset): Either a file path/URL to a raster,
            an xarray DataArray, or an xarray Dataset.

    Returns:
        xr.DataArray | xr.Dataset | str: The opened raster as DataArray/Dataset or the
        original object if already such. If opening fails for a string path/URL, returns
        a message containing "Failed to open dataset". If an unsupported type is
        provided, returns a message containing "Unsupported type for ds".

    """
    if isinstance(ds, xr.Dataset | xr.DataArray):
        return ds
    if isinstance(ds, str):
        try:
            return rxr.open_rasterio(ds)
        except Exception as e:
            # Match tests that assert substring "Failed to open dataset"
            return f"Failed to open dataset from '{ds}': {e}"
    # Match tests that assert substring "Unsupported type for ds"
    return f"Unsupported type for ds: {type(ds)}. Expected str, xr.DataArray, or xr.Dataset."


def _interpolate_sample_points(
    geom: gpd.GeoSeries, spacing: float | int, calc_crs: str | int | CRS, crs: str | int | CRS
) -> tuple[npt.NDArray[np.double], npt.NDArray[np.double], npt.NDArray[np.double]]:
    """Interpolated points at equal distances along a line.

    Return the interpolated points and their distances from the initial point.

    Args:
        geom (gpd.GeoSeries): Line geometry to pull sample points from.
        spacing (Union[float, int]): The distance in meters between the sample points.
        calc_crs (Union[str, int, CRS]): Coordinate system to calculate interpolated points and distance.
        crs (Union[str, int, CRS]): Coordinate system to return the points in. EPSG code or Proj 4 string.

    Returns:
        Tuple[npt.NDArray[np.double], npt.NDArray[np.double], npt.NDArray[np.double]]:
        x (npt.NDArray[np.double]): Array of x coordinates of the sample points.
        y (npt.NDArray[np.double]): Array of y coordinates of the sample points.
        dist (npt.NDArray[np.double]): Array of distances from the first point to each of the sample points.

    Raises:
        Exception: For any other errors encountered during reprojection.

    """
    # Reproject twice prevents inf values
    # rp_geom: gpd.GeoSeries = geom.to_crs(calc_crs)
    rp_geom: gpd.GeoSeries = geom.to_crs(calc_crs)
    try:
        _check_reprojection(rp_geom, calc_crs, geom.crs, source_type="source")
    except Exception as e:
        logger.error(f"Reprojection error: {e}")
        raise
    # Get line length
    length = rp_geom.length.values[0]
    # Calculate the number of sample points
    num_points = int(length / spacing) + 1
    # Create empty numpy arrays for x,y coords
    x = np.zeros(num_points, dtype=np.double)
    y = np.zeros(num_points, dtype=np.double)
    dist = np.zeros(num_points, dtype=np.double)
    # Find sample points on line  # from nldi_xstools.PathGen
    d = 0.0
    index = 0
    while d < length:
        point = rp_geom.interpolate(d)
        # Project to grid crs
        point = point.to_crs(crs)
        # x[index] = point.x
        # y[index] = point.y
        # fix for FutureWarning
        x[index] = float(point.iloc[0].x)
        y[index] = float(point.iloc[0].y)
        dist[index] = d
        d += spacing
        index += 1

    return x, y, dist


def _get_line_vertices(
    geom: gpd.GeoDataFrame, calc_crs: str | int | CRS, crs: str | int | CRS
) -> tuple[list[float], list[float], list[float]]:
    """Return the vertices and the distance inbetween of a line in a GeoDataFrame.

    Args:
        geom (GeoDataFrame): A GeoDataFrame with a single line geometry
        calc_crs(Union[str, int, CRS]): Coordinate system to calculate vertex distance.
        crs (Union[str, int, CRS]): Coordinate system to return the points in. EPSG code or Proj 4 string.

    Returns:
        Tuple[list[float], list[float], list[float]]: Three list containing the x coords,
            y coords and distance in meters from the first vertex to each vertex

    Raises:
        Exception: For any other errors encountered during reprojection.

    """
    # project to equidistant crs to calculate distance between vertices
    rp_geom: gpd.GeoSeries = geom.to_crs(calc_crs).reset_index()
    try:
        _check_reprojection(rp_geom, calc_crs, geom.crs, "source")
    except Exception as e:
        logger.error(f"Reprojection error: {e}")
        raise
    if type(rp_geom.geometry[0]) is LineString:
        x, y = rp_geom.geometry[0].coords.xy
    else:  # If it is a multilinestring:
        x, y = rp_geom.geometry[0].geoms[0].coords.xy
    x = list(x)
    y = list(y)

    # cal distance between the first vertex and each vertex
    for i in range(len(x)):
        if i == 0:
            dist = [0.0]
        else:
            d = dist[i - 1] + math.dist([x[i - 1], y[i - 1]], [x[i], y[i]])
            dist.append(d)

    # Project line to grid crs and export vertex coords
    rp_geom: gpd.GeoSeries = geom.to_crs(crs).reset_index()
    if type(rp_geom.geometry[0]) is LineString:
        x, y = rp_geom.geometry[0].coords.xy
    else:  # If it is a multilinestring:
        x, y = rp_geom.geometry[0].geoms[0].coords.xy
    x = list(x)
    y = list(y)

    return x, y, dist


def _cal_point_stats(
    data: xr.DataArray | xr.Dataset,
    stat: str,
    userdata_type: str,
    skipna: bool | None = None,
) -> dict[Any]:
    """Calculate the specified stats from a DataSet of points.

    Args:
        data: (Union[xr.DataArray, xr.Dataset]): Xarray DataArray or Dataset of values pulled from
            a gridded dataset at interpolated points
        stat (str): A string indicating which statistics to calculated.
            Options: all, mean, median, std, min, max
        userdata_type (str): A string indicating the type of the User Data Class. Options
            are 'UserCatData', 'ClimRCatData', 'UserTiffData', 'NHGFStacData'.
        skipna (bool or None): Optional; If True, skip nodata values in the gridded
            data for the calculations of statistics. By default, only skips missing
            values for float dtypes.

    Returns:
        dict: A dictionary of statistical values

    """
    out_vals: dict[Any] = {}

    # Calculate the stats
    if userdata_type != "UserTiffData":
        options = {
            "mean": data.mean(dim=["pt"], skipna=skipna),
            "median": data.median(dim=["pt"], skipna=skipna),
            "std": data.std(dim=["pt"], skipna=skipna),
            "min": data.min(dim=["pt"], skipna=skipna),
            "max": data.max(dim=["pt"], skipna=skipna),
        }
    else:
        options = {
            "mean": data.mean(dim=["pt"], skipna=skipna).values,
            "median": data.median(dim=["pt"], skipna=skipna).values,
            "std": data.std(dim=["pt"], skipna=skipna).values,
            "min": data.min(dim=["pt"], skipna=skipna).values,
            "max": data.max(dim=["pt"], skipna=skipna).values,
        }

    stat = ["mean", "median", "std", "min", "max"] if stat == "all" else [stat]

    for i in stat:
        out_vals[i] = options[i]

    return out_vals


def _buffer_line(
    geometry: gpd.GeoSeries,
    buffer: float | int,
    proj_feature: int | str | CRS,
    calc_crs: int | str | CRS,
) -> gpd.GeoSeries:
    """Buffer a line segment.

    The line gets reprojected to an AEA projection, so that the buffer can be
    submitted in meters. Then the buffered geometry it reprojected back to
    a user specified crs.

    Args:
        geometry (GeoSeries): Geometry of the query line
        buffer (float): Value in meters of the diameter of the buffer
        proj_feature (Union[int, str, CRS]): Coordinate system of the returned buffer geometry
        calc_crs: (Union[int, str, CRS]) Coordinate system in which to perform the statistical calculations

    Returns:
        new_geometry (GeoSeries): Geometry of the buffer

    """
    return geometry.to_crs(calc_crs).buffer(buffer).to_crs(proj_feature)


def _dataframe_to_geodataframe(
        df: pd.DataFrame,
        crs: str | int | CRS,
        x_coord: str | None = None,
        y_coord: str | None = None,
    ) -> gpd.GeoDataFrame:
    """Convert a Pandas DataFrame to a GeoDataFrame.

    This function converts a Pandas DataFrame with 'x' and 'y' columns
    representing point coordinates into a GeoDataFrame. It assigns Point
    geometries to each row based on these coordinates and sets the specified
    CRS.

    Args:
        df (pd.DataFrame): The input DataFrame with 'x' and 'y' columns.
        crs (Union[str, int, CRS]): The coordinate reference system (CRS) string for the GeoDataFrame.
        x_coord (str): Optional. If used, this defines the X dimension name of the dataframe being passed in.
        y_coord (str): Optional. If used, this defines the Y dimension name of the dataframe being passed in.

    Returns:
        gpd.GeoDataFrame: The resulting GeoDataFrame with Point geometries.

    """
    if x_coord and y_coord:
        geometry = [Point(xy) for xy in zip(df[x_coord], df[y_coord], strict=False)]
        df = df.drop([x_coord, y_coord], axis=1)
    # defaults to x and y dimensions
    elif not x_coord and not y_coord:
        geometry = [Point(xy) for xy in zip(df.x, df.y, strict=False)]
        df = df.drop(["x", "y"], axis=1)
    else:
        return ValueError("Both 'x_coord' and 'y_coord' either need to be None or defined as strings.")

    try:
        df = df.drop(['crs'])
    except KeyError:
        pass

    return gpd.GeoDataFrame(df, geometry=geometry, crs=crs)


def _process_period(period: list[str | pd.Timestamp | datetime.datetime | None]) -> list[str]:
    """Process the period list and convert elements to pd.Timestamp.

    Args:
        period: A list of elements representing a time period. Each element can be a string,
            pd.Timestamp, datetime.datetime, or None.

    Returns:
        List[pd.Timestamp]: A list of pd.Timestamp objects representing the processed period.

    Raises:
        ValueError: If period is not a list or if it does not contain 1 or 2 elements.
        ValueError: If the elements of period are not of the expected types.

    Examples:
        >>> _process_period(['2022-01-01', '2022-01-31'])
        [Timestamp('2022-01-01 00:00:00'), Timestamp('2022-01-31 00:00:00')]

    """
    # Check if period is a list
    if not isinstance(period, list):
        raise ValueError("period must be a list")

    # Check if the list contains 1 or 2 elements
    if len(period) not in [1, 2]:
        raise ValueError("period must contain 1 or 2 elements")

    # Convert strings to datetime and validate elements
    result = []
    for element in period:
        if isinstance(element, str):
            # Validate that string can be parsed as a date
            try:
                pd.to_datetime(element)
                result.append(element)
            except (ValueError, TypeError, pd.errors.ParserError) as e:
                raise ValueError(f"Invalid date string '{element}': {e}") from e
        elif isinstance(element, datetime.datetime):
            result.append(element.isoformat())
        elif isinstance(element, pd.Timestamp):
            result.append(element.isoformat())
        elif element is None:
            result.append(None)
        else:
            raise ValueError("Elements of period must be string, pd.Timestamp, datetime.datetime, or None")

    return result


def _make_valid(df: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Convert invalid geometries in a GeoDataFrame to valid ones.

    This function checks for invalid geometries in the provided GeoDataFrame.
    For invalid geometries, it uses the buffer trick (buffering by a distance of 0)
    to attempt to convert them into valid geometries. This approach is based on
    the method in Shapely and has been adapted for this specific use case.

    Notes:
        It's recommended to use this function with caution, as the buffer trick
    might not always produce the desired results for all types of invalid geometries.

    Adapted from Shapely:
    Copyright (c) 2007, Sean C. Gillies. 2019, Casper van der Wel. 2007-2022,
    Shapely Contributors. All rights reserved.

    Redistribution and use in source and binary forms, with or without
    modification, are permitted provided that the following conditions are met:

    1. Redistributions of source code must retain the above copyright notice, this
    list of conditions and the following disclaimer.

    2. Redistributions in binary form must reproduce the above copyright notice,
    this list of conditions and the following disclaimer in the documentation
    and/or other materials provided with the distribution.

    3. Neither the name of the copyright holder nor the names of its
    contributors may be used to endorse or promote products derived from
    this software without specific prior written permission.

    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
    AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
    IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
    DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
    FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
    DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
    SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
    CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
    OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
    OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

    Args:
        df (gpd.GeoDataFrame): A GeoDataFrame containing the geometries to be validated.

    Returns:
        gpd.GeoDataFrame: A GeoDataFrame with invalid geometries made valid. If no
            invalid geometries are found, the original GeoDataFrame is returned unchanged.

    """
    polys = ["Polygon", "MultiPolygon"]
    if df.geom_type.isin(polys).all():
        mask = ~df.geometry.is_valid
        print(f"     - fixing {len(mask[mask])} invalid polygons.")
        col = df._geometry_column_name
        df.loc[mask, col] = df.loc[mask, col].buffer(0)
    return df
