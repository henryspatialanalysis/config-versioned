Installation
============

Core package (YAML support only):

.. code-block:: bash

   pip install versioned-config

With optional file-format extras:

.. code-block:: bash

   pip install versioned-config[pandas]    # CSV, TSV, Excel, Stata
   pip install versioned-config[geo]       # Shapefiles, GeoJSON, GeoPackage, etc.
   pip install versioned-config[raster]    # GeoTIFF and other raster formats
   pip install versioned-config[xarray]    # NetCDF
   pip install versioned-config[dbfread]   # DBF files
   pip install versioned-config[all]       # All of the above

Config file structure
---------------------

The config YAML has two special top-level keys — ``directories`` and
``versions`` — alongside any arbitrary settings your pipeline needs:

.. code-block:: yaml

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
         summary:      'summary.txt'

   versions:
     results: 'v1'

Each entry under ``directories`` requires three fields:

- **versioned** (bool) — whether the directory uses version subdirectories.
- **path** (str) — base path (tilde expansion is applied).
- **files** (dict) — named file stubs within the directory.

For versioned directories the full path is ``{path}/{version}``, where the
version comes from the ``versions`` dict (or a ``custom_version`` argument).

Supported file extensions
-------------------------

.. list-table::
   :header-rows: 1
   :widths: 20 30 30

   * - Format
     - Extensions
     - Requires
   * - CSV / TSV
     - csv, tsv, gz, bz2
     - ``pandas``
   * - Excel
     - xls, xlsx
     - ``pandas``, ``openpyxl``
   * - Stata
     - dta
     - ``pandas``
   * - DBF
     - dbf
     - ``dbfread``
   * - YAML
     - yaml, yml
     - *(core)*
   * - Plain text
     - txt
     - *(core)*
   * - Vector geospatial
     - shp, geojson, gpkg, fgb, gml, kml, …
     - ``geopandas``
   * - Raster
     - tif, geotiff
     - ``rasterio``
   * - NetCDF
     - nc
     - ``xarray``

For raster files, :func:`~versioned_config.autoread` returns
``{"data": np.ndarray, "profile": dict}`` and
:func:`~versioned_config.autowrite` accepts that same structure (or a
``(data, profile)`` tuple).
