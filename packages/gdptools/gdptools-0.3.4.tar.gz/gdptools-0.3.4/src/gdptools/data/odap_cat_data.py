"""Pydantic models for handling ClimateR-style catalog metadata."""

from __future__ import annotations

from typing import Any

import numpy as np
from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, field_validator, model_validator


class CatClimRItem(BaseModel):
    """A Pydantic model for ClimateR-style catalog items.

    This class provides a structured representation of a single entry from a
    climateR-style data catalog, such as the one maintained by Mike Johnson.
    It includes fields for dataset identification, access information (URL),
    variable metadata, and spatiotemporal properties.

    The model includes validators to handle common data inconsistencies found
    in catalog files, such as converting NaN values to None, setting default
    values for projection, and ensuring boolean fields are correctly parsed.

    Source data from:
    `https://github.com/mikejohnson51/climateR-catalogs/releases/download/June-2024/catalog.parquet`

    Attributes:
        id: Unique identifier for the dataset (e.g., 'gridmet').
        asset: Name of the asset within the dataset.
        URL: The URL to access the data, typically an OPeNDAP or HTTP endpoint.
        varname: The specific variable name within the dataset.
        long_name: A descriptive, human-readable name for the variable.
        variable: An alternative or short name for the variable.
        description: A longer description of the variable.
        units: The physical units of the variable's data.
        model: The climate model that generated the data, if applicable.
        ensemble: The model ensemble member, if applicable.
        scenario: The climate scenario (e.g., 'ssp245'), if applicable.
        T_name: The name of the time coordinate dimension.
        duration: The temporal duration of each time step (e.g., '1 day').
        interval: The temporal interval between time steps.
        nT: The total number of time steps in the dataset.
        X_name: The name of the X-coordinate (longitude) dimension.
        Y_name: The name of the Y-coordinate (latitude) dimension.
        X1: The minimum X-coordinate value.
        Xn: The maximum X-coordinate value.
        Y1: The minimum Y-coordinate value.
        Yn: The maximum Y-coordinate value.
        resX: The spatial resolution in the X-direction.
        resY: The spatial resolution in the Y-direction.
        ncols: The number of columns in the grid.
        nrows: The number of rows in the grid.
        proj: The projection of the dataset as a PROJ string or similar.
        toptobottom: Boolean indicating if the Y-axis is oriented from top to bottom.
        tiled: Tiling scheme of the data, if any (e.g., 'T', 'XY').
        crs: The coordinate reference system, often as an EPSG code or WKT.

    """

    id: str | None = None
    asset: str | None = None
    URL: str
    varname: str
    long_name: str | None = None
    variable: str | None = None
    description: str | None = None
    units: str | None = None
    model: str | None = None
    ensemble: str | None = None
    scenario: str | None = None
    T_name: str | None = None
    duration: str | None = None
    interval: str | None = None
    nT: int | None = Field(default=0)  # noqa: N815
    X_name: str
    Y_name: str
    X1: float | None = None
    Xn: float | None = None
    Y1: float | None = None
    Yn: float | None = None
    resX: float  # noqa: N815
    resY: float  # noqa: N815
    ncols: int | None = None
    nrows: int | None = None
    proj: str | None = None
    toptobottom: bool
    tiled: str | None = None
    crs: str | None = None

    @field_validator("model", "ensemble", mode="before", check_fields=False)
    @classmethod
    def _nan_to_none(cls, v: str | float | None) -> str | None:
        """Convert NaN floats to None before validation.

        Args:
            v: The value to validate.

        Returns:
            The original value, or None if the value is NaN.

        """
        # Handle both numpy.nan and Python float nan
        return None if isinstance(v, float) and np.isnan(v) else v

    @model_validator(mode="after")
    def set_default_long_name(self, info: ValidationInfo) -> CatClimRItem:
        """Set `long_name` from `description` if missing.

        This validator ensures that `long_name` has a value, falling back to
        the `description` field or "None" if both are missing.

        Args:
            info: Pydantic validation information.

        Returns:
            The validated model instance.

        """
        if not self.long_name:
            self.long_name = self.description or "None"
        return self

    @model_validator(mode="after")
    def _set_proj(self, info: ValidationInfo) -> CatClimRItem:
        """Set `proj` from `crs` if `proj` is missing.

        This validator ensures that `proj` has a value, falling back to the
        `crs` field or a default of "EPSG:4326" if both are missing.

        Args:
            info: Pydantic validation information.

        Returns:
            The validated model instance.

        """
        if not self.proj:
            self.proj = self.crs or "EPSG:4326"
        return self

    @field_validator("nT", mode="before", check_fields=False)
    @classmethod
    def set_nt(cls, v: Any) -> int:  # noqa: ANN401
        """Convert nT to int, handling potential NaN or None values.

        Args:
            v: The value to validate for the `nT` field.

        Returns:
            The value as an integer, or 0 if it's None or NaN.

        """
        if v is None:
            return 0
        if isinstance(v, float | np.floating) and np.isnan(v):
            return 0
        return int(v)

    @field_validator("toptobottom", mode="before")
    @classmethod
    def _toptobottom_as_bool(cls, v: Any) -> bool:  # noqa: ANN401
        """Convert 'TRUE'/'FALSE' strings to boolean.

        This validator handles string representations of booleans often found
        in catalog files.

        Args:
            v: The value to validate for the `toptobottom` field.

        Returns:
            The boolean representation of the value.

        """
        if isinstance(v, str):
            return v.strip().upper() == "TRUE"
        return bool(v)

    @field_validator("tiled", mode="before", check_fields=False)
    @classmethod
    def _tiled(cls, val: str | None) -> str:
        """Ensure the `tiled` value is valid.

        Validates that the `tiled` field is one of the expected values.
        Defaults to "NA" if the input is None or empty.

        Args:
            val: The value to validate for the `tiled` field.

        Returns:
            The validated and capitalized tile value.

        Raises:
            ValueError: If the value is not one of the allowed options.

        """
        if not val:
            return "NA"
        val = val.upper()
        if val not in ["", "NA", "T", "XY"]:
            raise ValueError("tiled must be one of ['', 'NA', 'T', 'XY']")
        return val

    model_config = ConfigDict(
        str_strip_whitespace=False,
        frozen=False,  # allow mutation (new way)
    )
