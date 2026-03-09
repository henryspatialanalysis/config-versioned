# Versioning

We are recreating the R package found in `../versioning.R/` as a clean Python package with tests and documentation, so that it is fully ready to be uploaded to PyPL. The package name is "versioning".

The purpose of this package is to parse YAML config files that simplify file reading and writing, with some opinionated package choices for file reading and writing of particular file types. The package is also intended to make it easy to deploy different versions of data pipelines over time.

## Documentation

Sphinx docs live in `docs/` and are auto-deployed to GitHub Pages on every push to `main` via `.github/workflows/docs.yml`.

Docstring changes and signature updates are picked up automatically. However, when you **add a new public function, class, or module**, you must manually update `docs/api.rst` with the corresponding `.. autofunction::`, `.. autoclass::`, or `.. automodule::` directive. If the new symbol depends on a new optional third-party package, also add that package to `autodoc_mock_imports` in `docs/conf.py`.

The version shown in the docs is read automatically from `__version__` in `src/versioning/__init__.py`; update that string when releasing a new version.