# gdptools

![gdptools](docs/assets/gdptools_logo.png)

[![PyPI](https://img.shields.io/pypi/v/gdptools.svg)](https://pypi.org/project/gdptools/)
[![conda](https://anaconda.org/conda-forge/gdptools/badges/version.svg)](https://anaconda.org/conda-forge/gdptools)
[![Latest Release](https://code.usgs.gov/wma/nhgf/toolsteam/gdptools/-/badges/release.svg)](https://code.usgs.gov/wma/nhgf/toolsteam/gdptools/-/releases)

[![Status](https://img.shields.io/pypi/status/gdptools.svg)](https://pypi.org/project/gdptools/)
[![Python Version](https://img.shields.io/pypi/pyversions/gdptools)](https://pypi.org/project/gdptools)

[![License](https://img.shields.io/pypi/l/gdptools)](https://creativecommons.org/publicdomain/zero/1.0/legalcode)

[![Read the documentation at https://gdptools.readthedocs.io/](https://img.shields.io/readthedocs/gdptools/latest.svg?label=Read%20the%20Docs)](https://gdptools.readthedocs.io/)
[![pipeline status](https://code.usgs.gov/wma/nhgf/toolsteam/gdptools/badges/main/pipeline.svg)](https://code.usgs.gov/wma/nhgf/toolsteam/gdptools/-/commits/main)
[![coverage report](https://code.usgs.gov/wma/nhgf/toolsteam/gdptools/badges/main/coverage.svg)](https://code.usgs.gov/wma/nhgf/toolsteam/gdptools/-/commits/main)

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://code.usgs.gov/pre-commit/pre-commit)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Poetry](https://img.shields.io/badge/poetry-enabled-blue)](https://python-poetry.org/)
[![Conda](https://img.shields.io/badge/conda-enabled-green)](https://anaconda.org/)

**gdptools** is a Python package for calculating area-weighted statistics and spatial interpolations between gridded datasets and vector geometries. It provides efficient tools for **grid-to-polygon**, **grid-to-line**, and **polygon-to-polygon** interpolations with support for multiple data catalogs and custom datasets.

![Welcome figure](./docs/assets/Welcom_fig.png)

_Figure: Example grid-to-polygon interpolation. A) HUC12 basins for Delaware River Watershed. B) Gridded monthly water evaporation amount (mm) from TerraClimate dataset. C) Area-weighted-average interpolation of gridded TerraClimate data to HUC12 polygons._

## 🚀 Key Features

- **Multiple Interpolation Methods**: Grid-to-polygon, grid-to-line, and polygon-to-polygon area-weighted statistics
- **Catalog Integration**: Built-in support for STAC catalogs (NHGF, ClimateR) and custom metadata
- **Flexible Data Sources**: Works with any xarray-compatible gridded data and geopandas vector data
- **Scalable Processing**: Serial, parallel, and Dask-based computation methods
- **Multiple Output Formats**: NetCDF, CSV, and in-memory results
- **Extensive vs Intensive Variables**: Proper handling of different variable types in polygon-to-polygon operations
- **Intelligent Spatial Processing**: Automatic reprojection to equal-area coordinate systems and efficient spatial subsetting

## 🌍 Spatial Processing & Performance

gdptools automatically handles complex geospatial transformations to ensure accurate and efficient calculations:

### Automatic Reprojection

- **Equal-Area Projections**: Both source gridded data and target geometries are automatically reprojected to a common equal-area coordinate reference system (default: EPSG:6931 - US National Atlas Equal Area)
- **Accurate Area Calculations**: Equal-area projections ensure that area-weighted statistics are calculated correctly, regardless of the original coordinate systems
- **Flexible CRS Options**: Users can specify alternative projection systems via the `weight_gen_crs` parameter

### Efficient Spatial Subsetting

- **Bounding Box Optimization**: Gridded datasets are automatically subset to the bounding box of the target geometries plus a buffer
- **Smart Buffering**: Buffer size is calculated as twice the maximum grid resolution to ensure complete coverage
- **Memory Efficiency**: Only the necessary spatial extent is loaded into memory, dramatically reducing processing time and memory usage for large datasets

```python
# Example: Custom projection and efficient processing
from gdptools import AggGen

agg = AggGen(
    user_data=my_data,
    weight_gen_crs=6931,  # US National Atlas Equal Area (default)
    method="parallel"      # Leverage spatial optimizations
)
results = agg.get_zonal_stats()
```

## 📦 Installation

### Via pip

```bash
pip install gdptools
```

### Via conda

```bash
conda install -c conda-forge gdptools
```

### Development installation

```bash
git clone https://code.usgs.gov/wma/nhgf/toolsteam/gdptools.git
cd gdptools
conda env create -f environment.yml
conda activate gdptools
poetry install
pre-commit install --install-hooks
```

## 🔧 Core Components

### Data Classes

- **`ClimRCatData`**: Interface with ClimateR catalog datasets
- **`NHGFStacData`**: Interface with NHGF STAC catalog datasets
- **`UserCatData`**: Custom user-defined gridded datasets
- **`UserTiffData`**: GeoTIFF/raster data interface

### Processing Classes

- **`WeightGen`**: Calculate spatial intersection weights
- **`AggGen`**: Perform area-weighted aggregations
- **`InterpGen`**: Grid-to-line interpolation along vector paths

## 🎯 Quick Start

### Grid-to-Polygon Aggregation

```python
import geopandas as gpd
import xarray as xr
from gdptools import UserCatData, WeightGen, AggGen

# Load your data
gridded_data = xr.open_dataset("your_gridded_data.nc")
polygons = gpd.read_file("your_polygons.shp")

# Setup data interface
user_data = UserCatData(
    source_ds=gridded_data,
    source_crs="EPSG:4326",
    source_x_coord="lon",
    source_y_coord="lat",
    source_t_coord="time",
    source_var=["temperature", "precipitation"],
    target_gdf=polygons,
    target_crs="EPSG:4326",
    target_id="polygon_id",
    source_time_period=["2020-01-01", "2020-12-31"]
)

# Calculate intersection weights
weight_gen = WeightGen(user_data=user_data, method="parallel")
weights = weight_gen.calculate_weights()

# Perform aggregation
agg_gen = AggGen(
    user_data=user_data,
    stat_method="masked_mean",
    agg_engine="parallel",
    agg_writer="netcdf",
    weights=weights
)
result_gdf, result_dataset = agg_gen.calculate_agg()
```

### Using NHGF-STAC Catalogs

```python
from gdptools import NHGFStacData
import pystac

# Access NHGF STAC catalog
catalog = pystac.read_file("https://api.water.usgs.gov/gdp/pygeoapi/stac/stac-collection/")
collection = catalog.get_child("conus404-daily")

user_data = NHGFStacData(
    source_stac_item=collection,
    source_var=["PWAT"],
    target_gdf=watersheds,
    target_id="huc12",
    source_time_period=["1999-01-01", "1999-01-07"]
)
```

### Using ClimateR Catalog

```python
from gdptools import ClimRCatData
import pandas as pd

# Query ClimateR catalog
catalog = pd.read_parquet("https://github.com/mikejohnson51/climateR-catalogs/releases/download/June-2024/catalog.parquet")
terraclimate = catalog.query("id == 'terraclim' & variable == 'aet'")

user_data = ClimRCatData(
    source_cat_dict={"aet": terraclimate.to_dict("records")[0]},
    target_gdf=basins,
    target_id="basin_id",
    source_time_period=["1980-01-01", "1980-12-31"]
)
```

## 📊 Use Cases & Examples

### 1. Climate Data Aggregation

- **TerraClimate** monthly evapotranspiration to HUC12 basins
- **GridMET** daily temperature/precipitation to administrative boundaries
- **CONUS404** high-resolution climate data to custom polygons
- **MERRA-2** reanalysis data to watershed polygons

### 2. Hydrologic Applications

- **Stream network analysis**: Extract elevation profiles along river reaches using 3DEP data
- **Watershed statistics**: Calculate basin-averaged climate variables
- **Flow routing**: Grid-to-line interpolation for stream network analysis

### 3. Environmental Monitoring

- **Air quality**: Aggregate gridded pollution data to census tracts
- **Land cover**: Calculate fractional land use within administrative units
- **Biodiversity**: Combine species habitat models with management areas

## ⚡ Performance Options

### Processing Methods

- **`"serial"`**: Single-threaded processing (default, reliable)
- **`"parallel"`**: Multi-threaded processing (faster for large datasets)
- **`"dask"`**: Distributed processing (requires Dask cluster)

### Memory Management

- **Chunked processing**: Handle large datasets that don't fit in memory
- **Caching**: Cache intermediate results for repeated operations
- **Efficient data structures**: Optimized spatial indexing and intersection algorithms

### Large-scale heuristics

| Target polygons    | Recommended engine | Notes                                                        |
| ------------------ | ------------------ | ------------------------------------------------------------ |
| < 5k               | `"serial"`         | Fits comfortably in RAM; best for debugging                  |
| 5k–50k             | `"parallel"`       | Run with `jobs=-1` and monitor memory usage                  |
| > 50k / nationwide | `"dask"`           | Use a Dask cluster and consider 2,500–10,000 polygon batches |

- Persist the gridded dataset once, then iterate through polygon batches to keep memory flat.
- Write each batch of weights to Parquet/CSV immediately; append at the end instead of keeping all
  intersections in memory.
- Avoid `intersections=True` unless you need the geometries; it multiplies memory requirements.
- See `docs/weight_gen_classes.md` ⇢ "Scaling to Nationwide Datasets" for an end-to-end chunking example.

## 📈 Statistical Methods

### Available Statistics

- **`"masked_mean"`**: Area-weighted mean (most common)
- **`"masked_sum"`**: Area-weighted sum
- **`"masked_median"`**: Area-weighted median
- **`"masked_std"`**: Area-weighted standard deviation

### Variable Types for Polygon-to-Polygon

- **Extensive**: Variables that scale with area (e.g., total precipitation, population)
- **Intensive**: Variables that don't scale with area (e.g., temperature, concentration)

## 🔧 Advanced Features

### Custom Coordinate Reference Systems

```python
# Use custom projection for accurate area calculations
weight_gen = WeightGen(
    user_data=user_data,
    weight_gen_crs=6931  # US National Atlas Equal Area
)
```

### Intersection Analysis

```python
# Save detailed intersection geometries for validation
weights = weight_gen.calculate_weights(intersections=True)
intersection_gdf = weight_gen.intersections
```

### Output Formats

```python
# Multiple output options
agg_gen = AggGen(
    user_data=user_data,
    agg_writer="netcdf",      # or "csv", "none"
    out_path="./results/",
    file_prefix="climate_analysis"
)
```

## 📚 Documentation & Examples

- **Full Documentation**: [https://gdptools.readthedocs.io/](https://gdptools.readthedocs.io/)
- **Example Notebooks**: Comprehensive Jupyter notebooks in `docs/Examples/`
  - STAC catalog integration (CONUS404 example)
  - ClimateR catalog workflows (TerraClimate example)
  - Custom dataset processing (User-defined data)
  - Grid-to-line interpolation (Stream analysis)
  - Polygon-to-polygon aggregation (Administrative boundaries)

## Sample Catalog Datasets

gdptools integrates with multiple climate and environmental data catalogs through two primary interfaces:

### ClimateR-Catalog

See the complete [catalog datasets reference](catalog_datasets.md) for a comprehensive list of supported datasets including:

- **Climate Data**: TerraClimate, GridMET, Daymet, PRISM, MACA, CHIRPS
- **Topographic Data**: 3DEP elevation models
- **Land Cover**: LCMAP, LCMAP-derived products
- **Reanalysis**: GLDAS, NLDAS, MERRA-2
- **Downscaled Projections**: BCCA, BCSD, LOCA

### NHGF STAC Catalog

See the [NHGF STAC datasets reference](nhgf_stac_datasets.md) for cloud-optimized access to:

- **High-Resolution Models**: CONUS404 (4km daily meteorology)
- **Observational Data**: GridMET, PRISM, Stage IV precipitation
- **Climate Projections**: LOCA2, MACA, BCCA/BCSD downscaled scenarios
- **Regional Datasets**: Alaska, Hawaii, Puerto Rico, Western US
- **Specialized Products**: SSEBop ET, permafrost, sea level rise

## User Defined XArray Datasets

For datasets not available through catalogs, gdptools provides `UserCatData` to work with any xarray-compatible gridded dataset. This is ideal for custom datasets, local files, or specialized data sources.

### Basic Usage

```python
import xarray as xr
import geopandas as gpd
from gdptools import UserCatData, WeightGen, AggGen

# Load your custom gridded dataset
custom_data = xr.open_dataset("my_custom_data.nc")
polygons = gpd.read_file("my_polygons.shp")

# Configure UserCatData for your dataset
user_data = UserCatData(
    source_ds=custom_data,           # Your xarray Dataset
    source_crs="EPSG:4326",          # CRS of the gridded data
    source_x_coord="longitude",      # Name of x-coordinate variable
    source_y_coord="latitude",       # Name of y-coordinate variable
    source_t_coord="time",           # Name of time coordinate variable
    source_var=["temperature", "precipitation"],  # Variables to process
    target_gdf=polygons,             # Target polygon GeoDataFrame
    target_crs="EPSG:4326",          # CRS of target polygons
    target_id="polygon_id",          # Column name for polygon identifiers
    source_time_period=["2020-01-01", "2020-12-31"]  # Time range to process
)
```

### Working with Different Data Formats

#### NetCDF Files

```python
# Single NetCDF file
data = xr.open_dataset("weather_data.nc")

# Multiple NetCDF files
data = xr.open_mfdataset("weather_*.nc", combine='by_coords')

user_data = UserCatData(
    source_ds=data,
    source_crs="EPSG:4326",
    source_x_coord="lon",
    source_y_coord="lat",
    source_t_coord="time",
    source_var=["temp", "precip"],
    target_gdf=watersheds,
    target_crs="EPSG:4326",
    target_id="watershed_id"
)
```

#### Zarr Archives

```python
# Cloud-optimized Zarr store
data = xr.open_zarr("s3://bucket/climate_data.zarr")

user_data = UserCatData(
    source_ds=data,
    source_crs="EPSG:3857",  # Web Mercator projection
    source_x_coord="x",
    source_y_coord="y",
    source_t_coord="time",
    source_var=["surface_temp", "soil_moisture"],
    target_gdf=counties,
    target_crs="EPSG:4269",  # NAD83
    target_id="county_fips"
)
```

#### Custom Coordinate Systems

```python
# Dataset with non-standard coordinate names
data = xr.open_dataset("model_output.nc")

user_data = UserCatData(
    source_ds=data,
    source_crs="EPSG:32612",         # UTM Zone 12N
    source_x_coord="easting",        # Custom x-coordinate name
    source_y_coord="northing",       # Custom y-coordinate name
    source_t_coord="model_time",     # Custom time coordinate name
    source_var=["wind_speed", "wind_direction"],
    target_gdf=grid_cells,
    target_crs="EPSG:32612",
    target_id="cell_id",
    source_time_period=["2021-06-01", "2021-08-31"]
)
```

### Advanced Configuration

#### Subset by Geographic Area

```python
# Pre-subset data to region of interest for efficiency
bbox = [-120, 35, -115, 40]  # [west, south, east, north]
regional_data = data.sel(
    longitude=slice(bbox[0], bbox[2]),
    latitude=slice(bbox[1], bbox[3])
)

user_data = UserCatData(
    source_ds=regional_data,
    source_crs="EPSG:4326",
    source_x_coord="longitude",
    source_y_coord="latitude",
    source_t_coord="time",
    source_var=["evapotranspiration"],
    target_gdf=california_basins,
    target_crs="EPSG:4326",
    target_id="basin_id"
)
```

#### Multiple Variables with Different Units

```python
# Handle datasets with multiple variables
user_data = UserCatData(
    source_ds=climate_data,
    source_crs="EPSG:4326",
    source_x_coord="lon",
    source_y_coord="lat",
    source_t_coord="time",
    source_var=[
        "air_temperature",      # Kelvin
        "precipitation_flux",   # kg/m²/s
        "relative_humidity",    # %
        "wind_speed"           # m/s
    ],
    target_gdf=study_sites,
    target_crs="EPSG:4326",
    target_id="site_name",
    source_time_period=["2019-01-01", "2019-12-31"]
)
```

#### Processing Workflow

```python
# Complete workflow with UserCatData
user_data = UserCatData(
    source_ds=my_dataset,
    source_crs="EPSG:4326",
    source_x_coord="longitude",
    source_y_coord="latitude",
    source_t_coord="time",
    source_var=["surface_temperature"],
    target_gdf=administrative_boundaries,
    target_crs="EPSG:4326",
    target_id="admin_code"
)

# Generate intersection weights
weight_gen = WeightGen(
    user_data=user_data,
    method="parallel",           # Use parallel processing
    weight_gen_crs=6931         # Use equal-area projection for accurate weights
)
weights = weight_gen.calculate_weights()

# Perform area-weighted aggregation
agg_gen = AggGen(
    user_data=user_data,
    stat_method="masked_mean",   # Calculate area-weighted mean
    agg_engine="parallel",
    agg_writer="netcdf",         # Save results as NetCDF
    weights=weights,
    out_path="./results/",
    file_prefix="temperature_analysis"
)

result_gdf, result_dataset = agg_gen.calculate_agg()
```

### Data Requirements

Your xarray Dataset must include:

- **Spatial coordinates**: Regularly gridded x and y coordinates
- **Temporal coordinate**: Time dimension (if processing time series)
- **Data variables**: The variables you want to interpolate
- **CRS information**: Coordinate reference system (can be specified manually)

### Common Use Cases

- **Research datasets**: Custom model outputs, field measurements
- **Local weather stations**: Interpolated station data
- **Satellite products**: Processed remote sensing data
- **Reanalysis subsets**: Regional extracts from global datasets
- **Ensemble models**: Multi-model climate projections

## Requirements

### Data Formats

- **Gridded Data**: Any dataset readable by xarray with projected coordinates
- **Vector Data**: Any format readable by geopandas
- **Projections**: Any CRS readable by `pyproj.CRS`

### Dependencies

- Python 3.8+
- xarray (gridded data handling)
- geopandas (vector data handling)
- pandas (data manipulation)
- numpy (numerical operations)
- shapely (geometric operations)
- pyproj (coordinate transformations)

## 🤝 Contributing

We welcome contributions! Please see our development documentation for details on:

- Development environment setup
- Testing procedures
- Code style guidelines
- Issue reporting

## 📄 License

This project is in the public domain. See [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

gdptools integrates with several excellent open-source projects:

- **[xarray](http://xarray.pydata.org/)**: Multi-dimensional array processing
- **[geopandas](https://geopandas.org/)**: Geospatial data manipulation
- **[HyRiver](https://docs.hyriver.io/)**: Hydrologic data access (pynhd, pygeohydro)
- **[STAC](https://stacspec.org/)**: Spatiotemporal asset catalogs
- **[ClimateR](https://github.com/mikejohnson51/climateR-catalogs)**: Climate data catalogs

## History

The changelog can be found in [the changelog](HISTORY.md)

## Credits

This project was generated from [@hillc-usgs](https://code.usgs.gov/hillc-usgs)'s [Pygeoapi Plugin Cookiecutter](https://code.usgs.gov/wma/nhgf/pygeoapi-plugin-cookiecutter) template.

---

**Questions?** Open an issue on our [GitLab repository](https://code.usgs.gov/wma/nhgf/toolsteam/gdptools) or check the documentation for detailed examples and API reference.
