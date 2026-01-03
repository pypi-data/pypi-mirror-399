"""Writers for saving spatial aggregation results.

This module provides a set of writer classes for saving the results of
spatial aggregation operations to various file formats. It uses an abstract
base class (`AggDataWriter`) to define a common interface for all writers,
ensuring consistent behavior.

Concrete implementations are provided for common formats:
- `CSVWriter`: For writing to comma-separated value files.
- `JSONWriter`: For writing to JSON files.
- `ParquetWriter`: For writing to compressed Parquet files.
- `NetCDFWriter`: For writing to CF-compliant NetCDF files.
"""

import warnings
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path

import geopandas as gpd
import netCDF4
import numpy as np
import numpy.typing as npt
import pandas as pd
import pyproj
import xarray as xr
from shapely.geometry import Point

from gdptools.data.agg_gen_data import AggData


class AggDataWriter(ABC):
    """Abstract base class for writing aggregation data to different file formats.

    This class uses the template method pattern, where `save_file` orchestrates
    the file-saving process, and concrete subclasses must implement the
    `create_out_file` method to provide format-specific writing logic.
    """

    def save_file(
        self: "AggDataWriter",
        agg_data: dict[str, AggData],
        target_gdf: gpd.GeoDataFrame,
        vals: list[npt.NDArray[np.int_ | np.double]],
        p_out: str,
        file_prefix: str,
        append_date: bool | None = False,
        precision: int | None = None,
    ) -> None:
        """Save aggregated data to a file.

        This is the main entry point for all writer classes. It sets up the
        necessary instance variables and calls the `create_out_file` method.

        Args:
            agg_data (dict[str, AggData]): Dictionary of aggregation results keyed
                by variable or identifier, each value an `AggData` instance.
            target_gdf (gpd.GeoDataFrame): GeoDataFrame of target geometries.
            vals (list[npt.NDArray[np.int_ | np.double]]): Aggregated values aligned
                with `agg_data` order.
            p_out (str): Output directory path. Must exist.
            file_prefix (str): Prefix for the output file name.
            append_date (bool | None): If True, append the current date/time to the
                file name. Defaults to False.
            precision (int | None): Number of decimal places to round output values
                to, when supported by the writer. Defaults to None (no rounding).

        Raises:
            FileNotFoundError: If the output path does not exist.

        """
        self.agg_data = agg_data
        self.target_gdf = target_gdf
        self.vals = vals
        self.append_date = append_date
        self.precision = precision
        self.fdate = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        self.outpath = Path(p_out)
        if not self.outpath.exists():
            raise FileNotFoundError(f"Path: {p_out} does not exist")
        if self.append_date:
            self.fname = f"{self.fdate}_{file_prefix}"
        else:
            self.fname = f"{file_prefix}"

        self.create_out_file()

    @abstractmethod
    def create_out_file(self) -> None:
        """Abstract method for writing aggregation data to a specific format."""
        pass


class CSVWriter(AggDataWriter):
    """A writer for saving aggregated data to CSV files."""

    def create_out_file(self) -> None:
        """Write the aggregated data to a CSV file."""
        # for idx in range(len(self.agg_data)):
        for idx, (_key, value) in enumerate(self.agg_data.items()):
            gdf = self.target_gdf
            gdf_idx = self.agg_data[_key].target_id
            param_values = value.cat_cr
            t_coord = param_values.T_name
            units = param_values.units
            varname = param_values.varname
            time = value.da.coords[t_coord].values
            # units = self.agg_data[idx].param_dict

            df_key = pd.DataFrame(data=self.vals[idx], columns=gdf[gdf_idx].T.values)

            df_key.insert(0, "units", [units] * df_key.shape[0])
            df_key.insert(0, "varname", [varname] * df_key.shape[0])
            df_key.insert(0, "time", time)

            if idx == 0:
                df = df_key
            else:
                df = pd.concat([df, df_key])
        df.reset_index(inplace=True)
        if self.precision is not None:
            df = df.round(self.precision)
        path_to_file = self.outpath / f"{self.fname}.csv"
        print(f"Saving csv file to {path_to_file}")
        df.to_csv(path_to_file, index=False)


class JSONWriter(AggDataWriter):
    """A writer for saving aggregated data to JSON files."""

    def create_out_file(self) -> None:
        """Write the aggregated data to a JSON file."""
        # for idx in range(len(self.agg_data)):
        for idx, (_key, value) in enumerate(self.agg_data.items()):
            gdf = self.target_gdf
            gdf_idx = self.agg_data[_key].target_id
            param_values = value.cat_cr
            t_coord = param_values.T_name
            units = param_values.units
            varname = param_values.varname
            time = value.da.coords[t_coord].values
            # units = self.agg_data[idx].param_dict

            df_key = pd.DataFrame(data=self.vals[idx], columns=gdf[gdf_idx].T.values)

            df_key.insert(0, "units", [units] * df_key.shape[0])
            df_key.insert(0, "varname", [varname] * df_key.shape[0])
            df_key.insert(0, "time", time)

            if idx == 0:
                df = df_key
            else:
                df = pd.concat([df, df_key])
        df.reset_index(inplace=True)
        path_to_file = self.outpath / f"{self.fname}.json"
        print(f"Saving json file to {path_to_file}")
        df.to_json(path_to_file, orient="records", date_format="iso")


class ParquetWriter(AggDataWriter):
    """A writer for saving aggregated data to Parquet files."""

    def create_out_file(self) -> None:
        """Write the aggregated data to a Parquet file."""
        # for idx in range(len(self.agg_data)):
        for idx, (_key, value) in enumerate(self.agg_data.items()):
            gdf = self.target_gdf
            gdf_idx = self.agg_data[_key].target_id
            param_values = value.cat_cr
            t_coord = param_values.T_name
            units = param_values.units
            varname = param_values.varname
            time = value.da.coords[t_coord].values
            # units = self.agg_data[idx].param_dict

            df_key = pd.DataFrame(data=self.vals[idx], columns=gdf[gdf_idx].T.values)

            df_key.insert(0, "units", [units] * df_key.shape[0])
            df_key.insert(0, "varname", [varname] * df_key.shape[0])
            df_key.insert(0, "time", time)

            if idx == 0:
                df = df_key
            else:
                df = pd.concat([df, df_key])
        df.reset_index(inplace=True)
        if self.precision is not None:
            df = df.round(self.precision)
        # df.columns = df.columns.map(str)
        path_to_file = self.outpath / f"{self.fname}.parquet.gzip"
        print(f"Saving parquet file to {path_to_file}")
        df.to_parquet(path_to_file, compression="gzip")


class NetCDFWriter(AggDataWriter):
    """A writer for saving aggregated data to NetCDF files."""

    def create_out_file(self) -> None:
        """Write the aggregated data to a CF-compliant NetCDF file."""
        # Suppres UserWarning from centroid calc - Here lat/lon centroid are
        # a convenience method.
        warnings.filterwarnings(action="ignore", category=UserWarning)
        dataset = []
        # for idx in range(len(self.agg_data)):
        for idx, (_key, value) in enumerate(self.agg_data.items()):
            # convert geometry to 4326
            gdf = self.target_gdf.to_crs(4326)
            gdf_idx = value.target_id
            param_values = value.cat_cr
            t_coord = param_values.T_name
            v_units = param_values.units
            v_varname = param_values.varname
            v_long_name = param_values.long_name
            time = value.da.coords[t_coord].values
            locs = gdf[gdf_idx].values

            def getxy(pt: Point) -> tuple[np.double, np.double]:
                """Return x and y components of a point.

                Args:
                    pt (Point): The input point geometry.

                Returns:
                    tuple[np.double, np.double]: The x and y coordinates.

                """
                return pt.x, pt.y

            centroid_series = gdf.geometry.centroid
            tlon, tlat = [list(t) for t in zip(*map(getxy, centroid_series))]  # noqa B905
            crs_meta = pyproj.CRS(gdf.crs).to_cf()
            if self.precision is not None:
                # Assuming self.vals[idx] is the array you want to round
                data_vals = np.round(self.vals[idx], self.precision)
            else:
                data_vals = self.vals[idx]
            dsn = xr.Dataset(
                data_vars={
                    v_varname: (
                        ["time", gdf_idx],
                        data_vals,
                        {
                            "units": v_units,
                            "long_name": v_long_name,
                            "coordinates": "time lat lon",
                            "grid_mapping": "crs",
                        },
                    ),
                    # "crs": (["one"], np.ones((1), dtype=np.double), crs_meta),
                    "crs": ([], 1.0, crs_meta),
                },
                coords={
                    "time": time,
                    gdf_idx: ([gdf_idx], locs, {"feature_id": gdf_idx}),
                    "lat": (
                        [gdf_idx],
                        tlat,
                        {
                            "long_name": "Latitude of HRU centroid",
                            "units": "degrees_north",
                            "standard_name": "latitude",
                            "axis": "Y",
                        },
                    ),
                    "lon": (
                        [gdf_idx],
                        tlon,
                        {
                            "long_name": "Longitude of HRU centroid",
                            "units": "degrees_east",
                            "standard_name": "longitude",
                            "axis": "X",
                        },
                    ),
                },
            )
            if self.vals[idx].dtype.str == "<f8":
                dsn[v_varname].encoding.update({"_FillValue": netCDF4.default_fillvals["f8"]})
            elif self.vals[idx].dtype.str == "<i8":
                dsn[v_varname].encoding.update({"_FillValue": netCDF4.default_fillvals["i8"]})

            dataset.append(dsn)

        ds = xr.merge(dataset)
        ds.encoding["time"] = {"unlimited": True}
        ds.attrs = {
            "Conventions": "CF-1.8",
            "featureType": "timeSeries",
            "history": (
                f"{self.fdate} Original file created by gdptools package: "
                "https://code.usgs.gov/wma/nhgf/toolsteam/gdptools \n"
            ),
        }
        path_to_file = self.outpath / f"{self.fname}.nc"
        print(f"Saving netcdf file to {path_to_file}")
        ds.to_netcdf(path_to_file, format="NETCDF4", engine="netcdf4")
