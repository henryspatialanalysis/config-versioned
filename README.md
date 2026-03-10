# Package `config-versioned` <img src="docs/_static/logo.png" align="right" height="139" />

A Python package for YAML-based configuration management in data pipelines, with versioned directory support and automatic file I/O by extension.

* _[Docs](https://henryspatialanalysis.github.io/config-versioned/)_
* _[View on PyPI](https://pypi.org/project/config-versioned/)_
* _This is the Python implementation of the versioning package; this same package is implemented in R, and can be viewed on [GitHub](https://github.com/henryspatialanalysis/versioning) and [CRAN](https://cran.r-project.org/web/packages/versioning/index.html)._

## Installation

```bash
pip install config-versioned
```

Install optional extras for specific file formats:

```bash
pip install config-versioned[pandas]   # CSV, TSV, Excel, Stata
pip install config-versioned[geo]      # Shapefiles, GeoJSON, GeoPackage, etc.
pip install config-versioned[raster]   # GeoTIFF, rasterio formats
pip install config-versioned[xarray]   # NetCDF
pip install config-versioned[dbfread]  # DBF files
pip install config-versioned[all]      # All of the above
```

## Quick Start

### 1. Create a config YAML file

```yaml
# project_config.yaml
project_name: 'my_analysis'

directories:
  raw_data:
    versioned: false
    path: '~/data/raw'
    files:
      input_table: 'records.csv'

  results:
    versioned: true
    path: '~/data/results'
    files:
      output_table: 'processed.csv'
      summary: 'summary.txt'

versions:
  results: 'v1'
```

### 2. Load the config

```python
from config_versioned import Config

cfg = Config('project_config.yaml')
```

### 3. Access settings

```python
cfg.get('project_name')           # 'my_analysis'
cfg.get('versions', 'results')    # 'v1'
cfg.get()                         # full config dict
```

### 4. Build paths

```python
# Non-versioned: returns ~/data/raw
cfg.get_dir_path('raw_data')

# Versioned: returns ~/data/results/v1
cfg.get_dir_path('results')

# With a custom version override
cfg.get_dir_path('results', custom_version='v2')

# Full file path
cfg.get_file_path('raw_data', 'input_table')   # ~/data/raw/records.csv
cfg.get_file_path('results', 'output_table')   # ~/data/results/v1/processed.csv
```

All path methods return `pathlib.Path` objects.

### 5. Read and write files

```python
import pandas as pd

# Read a file (path resolved from config)
df = cfg.read('raw_data', 'input_table')

# Process data
processed = df.head(10)

# Write results (directory must exist)
cfg.write(processed, 'results', 'output_table')
cfg.write(['Summary: 10 rows written\n'], 'results', 'summary')

# Write the config itself to the results directory
cfg.write_self('results')
```

### 6. Override versions at load time

```python
# Run the same pipeline with a new version
cfg_v2 = Config('project_config.yaml', versions={'results': 'v2'})
cfg_v2.get_dir_path('results')  # ~/data/results/v2
```

## Standalone autoread / autowrite

```python
from config_versioned import autoread, autowrite

# Read by extension
df = autoread('data/records.csv')
config = autoread('config.yaml')
lines = autoread('notes.txt')

# Write by extension
autowrite(df, 'output/results.csv')
autowrite({'key': 'value'}, 'output/config.yaml')
autowrite(['line one\n', 'line two\n'], 'output/notes.txt')
```

## Supported File Extensions

| Format | Extensions | Requires |
|--------|-----------|---------|
| CSV / TSV | csv, tsv, gz, bz2 | `pandas` |
| Excel | xls, xlsx | `pandas`, `openpyxl` |
| Stata | dta | `pandas` |
| DBF | dbf | `dbfread` |
| YAML | yaml, yml | *(core)* |
| Text | txt | *(core)* |
| Shapefile / Vector | shp, geojson, gpkg, fgb, gml, kml, and more | `geopandas` |
| Raster | tif, geotiff | `rasterio` |
| NetCDF | nc | `xarray` |

For raster files, `autoread` returns `{"data": np.ndarray, "profile": dict}` and `autowrite` accepts that same structure (or a `(data, profile)` tuple).

## Example Config File

A bundled example is included with the package:

```python
import importlib.resources as r
from config_versioned import Config

path = str(r.files("config_versioned") / "data" / "example_config.yaml")
cfg = Config(path)
```
