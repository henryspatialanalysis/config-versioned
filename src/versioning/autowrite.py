"""Auto-write objects to files based on their extension."""

import os
from pathlib import Path

from versioning.autoread import _require_or_raise


def get_file_writing_functions():
    """Return a dict mapping file extensions to writing functions.

    Returns
    -------
    dict
        Keys are lowercase file extensions (without the dot). Values are
        callables with signature ``f(x, file, **kwargs)`` that write the
        object to the file.
    """
    def write_csv(x, file, **kwargs):
        kwargs.setdefault("index", False)
        x.to_csv(file, **kwargs)

    def write_geo(x, file, **kwargs):
        x.to_file(file, **kwargs)

    def write_tif(x, file, **kwargs):
        rasterio = _require_or_raise("rasterio", "raster")
        if isinstance(x, tuple):
            data, profile = x
        elif isinstance(x, dict):
            data, profile = x["data"], x["profile"]
        else:
            raise TypeError(
                "For .tif/.geotiff, x must be a (data, profile) tuple or "
                "dict with keys 'data' and 'profile'."
            )
        with rasterio.open(str(file), "w", **profile) as dst:
            dst.write(data)

    def write_txt(x, file, **kwargs):
        with open(file, "w", **kwargs) as f:
            if isinstance(x, str):
                f.write(x)
            else:
                f.writelines(x)

    def write_yaml(x, file, **kwargs):
        import yaml
        kwargs.setdefault("default_flow_style", False)
        with open(file, "w") as f:
            yaml.dump(x, f, **kwargs)

    def write_nc(x, file, **kwargs):
        x.to_netcdf(file, **kwargs)

    funs = {
        "csv": write_csv,
        "shp": write_geo,
        "tif": write_tif,
        "geotiff": write_tif,
        "txt": write_txt,
        "yaml": write_yaml,
        "yml": write_yaml,
        "nc": write_nc,
    }

    # Additional geospatial vector formats (via geopandas/GDAL)
    geo_exts = [
        "fgb", "geojson", "geojsonseq", "gml", "gpkg", "gps", "gpx", "gtm",
        "gxt", "jml", "kml", "map", "ods", "sqlite", "vdv",
    ]
    for ext in geo_exts:
        funs[ext] = write_geo

    return funs


def autowrite(x, file, **kwargs):
    """Automatically write an object to a file based on its extension.

    Parameters
    ----------
    x : object
        The object to write. Expected types per format:
        - csv: pandas DataFrame
        - shp/geojson/etc.: geopandas GeoDataFrame
        - tif/geotiff: (ndarray, profile) tuple or dict with "data"/"profile"
        - txt: str or list of str
        - yaml/yml: dict (or any yaml-serializable object)
        - nc: xarray Dataset
    file : str or Path
        Full path where the file should be saved. Tilde expansion is applied.
        The parent directory must already exist.
    **kwargs
        Additional keyword arguments passed to the format-specific writer.

    Raises
    ------
    FileNotFoundError
        If the parent directory does not exist.
    ValueError
        If the file has no extension or the extension is not supported.
    """
    file = Path(os.path.expanduser(str(file)))
    save_dir = file.parent
    if not save_dir.exists():
        raise FileNotFoundError(
            f"Save directory '{save_dir}' does not exist."
        )
    ext = file.suffix.lstrip(".").lower()
    if not ext:
        raise ValueError(f"Output file '{file}' has no extension.")
    writing_fns = get_file_writing_functions()
    if ext not in writing_fns:
        raise ValueError(
            f"Unsupported file extension '.{ext}'. "
            f"Supported extensions: {sorted(writing_fns.keys())}"
        )
    writing_fns[ext](x, file, **kwargs)
