"""Placeholder __init__.py for data package."""

import logging

from .user_data import ClimRCatData, NHGFStacData, UserCatData, UserTiffData

logging.getLogger(__name__).addHandler(logging.NullHandler())

__all__ = ["ClimRCatData", "UserCatData", "UserTiffData", "NHGFStacData"]
