"""Test WeightGenP2P class for polygon-to-polygon weight generation."""

import gc
from collections.abc import Generator
from tempfile import TemporaryDirectory

import geopandas as gpd
import numpy as np
import pandas as pd
import pytest
from gdptools import WeightGenP2P
from shapely.geometry import Polygon


@pytest.fixture(scope="function")
def source_polygons() -> Generator[gpd.GeoDataFrame, None, None]:
    """Create source polygons for testing."""
    # Create a grid of source polygons
    polygons = []
    for i in range(3):
        for j in range(3):
            x_min, x_max = i * 10, (i + 1) * 10
            y_min, y_max = j * 10, (j + 1) * 10
            polygon = Polygon([(x_min, y_min), (x_max, y_min), (x_max, y_max), (x_min, y_max)])
            polygons.append(polygon)

    gdf = gpd.GeoDataFrame({
        'id': range(len(polygons)),
        'value': np.random.rand(len(polygons)) * 100,
        'geometry': polygons
    }, crs='EPSG:3857')

    yield gdf
    del gdf
    gc.collect()


@pytest.fixture(scope="function")
def target_polygons() -> Generator[gpd.GeoDataFrame, None, None]:
    """Create target polygons for testing (overlapping with source)."""
    # Create larger target polygons that overlap source polygons
    polygons = [
        Polygon([(5, 5), (25, 5), (25, 25), (5, 25)]),  # Overlaps multiple source polygons
        Polygon([(15, 15), (35, 15), (35, 35), (15, 35)])  # Overlaps different source polygons
    ]

    gdf = gpd.GeoDataFrame({
        'target_id': ['A', 'B'],
        'geometry': polygons
    }, crs='EPSG:3857')

    yield gdf
    del gdf
    gc.collect()


@pytest.fixture(scope="function")
def get_out_path() -> Generator[str, None, None]:
    """Get temporary output path."""
    with TemporaryDirectory() as temp_dir:
        yield temp_dir


def _create_weight_gen(
    source_polygons: gpd.GeoDataFrame,
    target_polygons: gpd.GeoDataFrame,
    weight_gen_crs: str = 'EPSG:6931'
) -> WeightGenP2P:
    """Create WeightGenP2P instance."""
    return WeightGenP2P(
        source_poly=source_polygons,
        source_poly_idx='id',
        target_poly=target_polygons,
        target_poly_idx='target_id',
        method='serial',
        weight_gen_crs=weight_gen_crs
    )


class TestWeightGenP2P:
    """Test WeightGenP2P functionality."""

    def test_init(self, source_polygons: gpd.GeoDataFrame, target_polygons: gpd.GeoDataFrame) -> None:
        """Test WeightGenP2P initialization."""
        weight_gen = _create_weight_gen(source_polygons, target_polygons)

        assert weight_gen.source_poly is not None
        assert weight_gen.target_poly is not None
        assert weight_gen.source_poly_idx == 'id'
        assert weight_gen.target_poly_idx == 'target_id'

    def test_serial_weight_calculation(
        self,
        source_polygons: gpd.GeoDataFrame,
        target_polygons: gpd.GeoDataFrame
    ) -> None:
        """Test serial weight calculation."""
        weight_gen = _create_weight_gen(source_polygons, target_polygons)

        weights = weight_gen.calculate_weights()

        # Verify weights structure
        assert isinstance(weights, pd.DataFrame)
        assert len(weights) > 0

        # Check for expected column names (the exact names may vary)
        columns = weights.columns.tolist()
        expected_weight_cols = ['wght', 'weight', 'weights', 'area_weight', 'normalized_area_weight']
        has_weight_col = any(col in columns for col in expected_weight_cols)
        assert has_weight_col, f"No weight column found in columns: {columns}"
