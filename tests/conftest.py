"""Shared pytest fixtures for the versioning test suite."""

import importlib.resources as pkg_resources
import shutil

import pytest


@pytest.fixture(scope="session")
def example_config_path(tmp_path_factory):
    """Path to the bundled example_config.yaml, copied to a temp file."""
    src = pkg_resources.files("versioning") / "data" / "example_config.yaml"
    tmp = tmp_path_factory.mktemp("data") / "example_config.yaml"
    tmp.write_bytes(src.read_bytes())
    return tmp


@pytest.fixture(scope="session")
def example_csv_path(tmp_path_factory):
    """Path to the bundled example_input_file.csv, copied to a temp file."""
    src = pkg_resources.files("versioning") / "data" / "example_input_file.csv"
    tmp = tmp_path_factory.mktemp("data") / "example_input_file.csv"
    tmp.write_bytes(src.read_bytes())
    return tmp


@pytest.fixture()
def config_with_tmp_dirs(example_config_path, tmp_path):
    """Config loaded from example YAML with directory paths redirected to tmp_path."""
    from versioning import Config

    cfg = Config(str(example_config_path))
    raw_dir = tmp_path / "raw_data"
    raw_dir.mkdir()
    prepared_base = tmp_path / "prepared_data"
    prepared_base.mkdir()
    version = cfg.get("versions", "prepared_data")
    (prepared_base / version).mkdir()

    cfg.config["directories"]["raw_data"]["path"] = str(raw_dir)
    cfg.config["directories"]["prepared_data"]["path"] = str(prepared_base)
    return cfg
