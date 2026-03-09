"""Auto-read files based on their extension."""

import os
from pathlib import Path

from versioned_config.utilities import pull_from_config


def _require_or_raise(pkg_name, install_extra=None):
    """Import a package, raising a helpful ImportError if it is not installed."""
    import importlib
    try:
        return importlib.import_module(pkg_name)
    except ImportError:
        hint = (
            f" Install with: pip install versioning[{install_extra}]"
            if install_extra
            else f" Install with: pip install {pkg_name}"
        )
        raise ImportError(
            f"Package '{pkg_name}' is required to read this file type.{hint}"
        )


def get_file_reading_functions():
    """Return a dict mapping file extensions to reading functions.

    Returns
    -------
    dict
        Keys are lowercase file extensions (without the dot). Values are
        callables with signature ``f(file, **kwargs)`` that read the file
        and return the loaded object.
    """
    def read_csv(file, **kwargs):
        pd = _require_or_raise("pandas", "pandas")
        return pd.read_csv(file, **kwargs)

    def read_tsv(file, **kwargs):
        pd = _require_or_raise("pandas", "pandas")
        kwargs.setdefault("sep", "\t")
        return pd.read_csv(file, **kwargs)

    def read_dbf(file, **kwargs):
        dbfread = _require_or_raise("dbfread", "dbfread")
        try:
            pd = _require_or_raise("pandas", "pandas")
            return pd.DataFrame(iter(dbfread.DBF(str(file), **kwargs)))
        except ImportError:
            return list(dbfread.DBF(str(file), **kwargs))

    def read_dta(file, **kwargs):
        pd = _require_or_raise("pandas", "pandas")
        return pd.read_stata(file, **kwargs)

    def read_geo(file, **kwargs):
        gpd = _require_or_raise("geopandas", "geo")
        return gpd.read_file(file, **kwargs)

    def read_tif(file, **kwargs):
        rasterio = _require_or_raise("rasterio", "raster")
        import numpy as np  # bundled with rasterio
        with rasterio.open(str(file), **kwargs) as src:
            data = src.read()
            profile = src.profile.copy()
        return {"data": data, "profile": profile}

    def read_txt(file, **kwargs):
        with open(file, **kwargs) as f:
            return f.readlines()

    def read_excel(file, **kwargs):
        pd = _require_or_raise("pandas", "pandas")
        return pd.read_excel(file, **kwargs)

    def read_yaml(file, **kwargs):
        import yaml
        with open(file, **kwargs) as f:
            return yaml.safe_load(f)

    def read_nc(file, **kwargs):
        xr = _require_or_raise("xarray", "xarray")
        return xr.open_dataset(file, **kwargs)

    funs = {
        "csv": read_csv,
        "tsv": read_tsv,
        "gz": read_csv,
        "bz2": read_csv,
        "dbf": read_dbf,
        "dta": read_dta,
        "shp": read_geo,
        "tif": read_tif,
        "geotiff": read_tif,
        "txt": read_txt,
        "xls": read_excel,
        "xlsx": read_excel,
        "yaml": read_yaml,
        "yml": read_yaml,
        "nc": read_nc,
    }

    # Additional geospatial vector formats (via geopandas/GDAL)
    geo_exts = [
        "e00", "fgb", "gdb", "geojson", "geojsonseq", "gml", "gpkg", "gps",
        "gpx", "gtm", "gxt", "jml", "kml", "map", "mdb", "ods", "osm", "pbf",
        "sqlite", "vdv",
    ]
    for ext in geo_exts:
        funs[ext] = read_geo

    return funs


def autoread(file, **kwargs):
    """Automatically read a file based on its extension.

    Parameters
    ----------
    file : str or Path
        Full path to the file to read. Tilde expansion is applied.
    **kwargs
        Additional keyword arguments passed to the format-specific reader.

    Returns
    -------
    The object loaded from the file. Return type depends on the format:
    - csv/tsv/xlsx/dta: pandas DataFrame
    - yaml/yml: dict
    - txt: list of str
    - shp/geojson/etc.: geopandas GeoDataFrame
    - tif/geotiff: dict with keys "data" (numpy ndarray) and "profile" (dict)
    - nc: xarray Dataset
    - dbf: pandas DataFrame (or list of dicts if pandas not installed)

    Raises
    ------
    FileNotFoundError
        If the file does not exist.
    IsADirectoryError
        If the path points to a directory.
    ValueError
        If the file has no extension or the extension is not supported.
    """
    file = Path(os.path.expanduser(str(file)))
    if not file.exists():
        raise FileNotFoundError(f"Input file '{file}' does not exist.")
    if file.is_dir():
        raise IsADirectoryError(f"Input path '{file}' is a directory, not a file.")
    ext = file.suffix.lstrip(".").lower()
    if not ext:
        raise ValueError(f"File '{file}' has no extension.")
    reading_fns = get_file_reading_functions()
    if ext not in reading_fns:
        raise ValueError(
            f"Unsupported file extension '.{ext}'. "
            f"Supported extensions: {sorted(reading_fns.keys())}"
        )
    return reading_fns[ext](file, **kwargs)
