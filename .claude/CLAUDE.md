# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# Versioning

We are recreating the R package found in `../versioning.R/` as a clean Python package with tests and documentation, so that it is fully ready to be uploaded to PyPI. The package name is "versioning".

The purpose of this package is to parse YAML config files that simplify file reading and writing, with some opinionated package choices for file reading and writing of particular file types. The package is also intended to make it easy to deploy different versions of data pipelines over time.

## Commands

```bash
# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run a single test file
pytest tests/test_config.py

# Run a single test by name
pytest tests/test_config.py::test_function_name

# Build the package
python -m build

# Build and serve docs locally
pip install -e ".[docs]"
cd docs && make html && python -m http.server -d _build/html
```

## Architecture

The package is at `src/config_versioned/` and exposes three top-level symbols:

- **`Config`** ([config.py](src/config_versioned/config.py)): Main class. Loads a YAML file, resolves directory paths (optionally appending a version subdirectory), and delegates file I/O to `autoread`/`autowrite`. Versioned directories append the version string from the `versions` section of the YAML (or from a constructor override) to the base path.

- **`autoread` / `autowrite`** ([autoread.py](src/config_versioned/autoread.py), [autowrite.py](src/config_versioned/autowrite.py)): Standalone functions that dispatch to format-specific readers/writers based on file extension. The dispatch table is returned by `get_file_reading_functions()` / `get_file_writing_functions()`, which lazy-imports optional dependencies (pandas, geopandas, rasterio, xarray, dbfread) and raises a helpful `ImportError` if the needed extra is missing.

- **`pull_from_config`** ([utilities.py](src/config_versioned/utilities.py)): Helper that reads a single value out of a YAML config file without instantiating a full `Config` object.

Optional dependencies are declared as extras in `pyproject.toml` (`pandas`, `geo`, `raster`, `xarray`, `dbfread`, `all`). Core dependencies are only `pyyaml`.

## Documentation

Sphinx docs live in `docs/` and are auto-deployed to GitHub Pages on every push to `main` via `.github/workflows/docs.yml`.

Docstring changes and signature updates are picked up automatically. However, when you **add a new public function, class, or module**, you must manually update `docs/api.rst` with the corresponding `.. autofunction::`, `.. autoclass::`, or `.. automodule::` directive. If the new symbol depends on a new optional third-party package, also add that package to `autodoc_mock_imports` in `docs/conf.py`.

The version shown in the docs is read automatically from `__version__` in `src/config_versioned/__init__.py`; update that string when releasing a new version.
