"""Sphinx configuration for the config-versioned package."""

import os
import sys

# Allow building docs without installing the package (local dev)
sys.path.insert(0, os.path.abspath("../src"))

# -- Project information -----------------------------------------------------

from config_versioned import __version__

project = "config-versioned"
copyright = "2026, Nathaniel Henry"
author = "Nathaniel Henry"
release = __version__

# -- General configuration ---------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "pandas": ("https://pandas.pydata.org/docs/", None),
}

# Mock optional heavy dependencies so docs build without them installed
autodoc_mock_imports = [
    "pandas",
    "geopandas",
    "rasterio",
    "xarray",
    "dbfread",
    "openpyxl",
    "numpy",
]

autodoc_default_options = {
    "members": True,
    "undoc-members": False,
    "show-inheritance": True,
    "special-members": "__init__",
}

# NumPy-style docstrings
napoleon_numpy_docstring = True
napoleon_google_docstring = False
napoleon_include_init_with_doc = True

# -- HTML output -------------------------------------------------------------

html_theme = "furo"
html_static_path = ["_static"]
html_logo = "_static/logo.png"

html_theme_options = {
    "source_repository": "https://github.com/henryspatialanalysis/config-versioned",
    "source_branch": "main",
    "source_directory": "docs/",
}
