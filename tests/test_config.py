"""Tests for the Config class."""

import importlib.resources as pkg_resources
from pathlib import Path

import pytest
import yaml

from versioned_config import Config


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _example_config_str(example_config_path):
    return str(example_config_path)


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------

class TestConstruction:
    def test_from_yaml_path(self, example_config_path):
        cfg = Config(str(example_config_path))
        assert isinstance(cfg.config, dict)

    def test_from_path_object(self, example_config_path):
        cfg = Config(example_config_path)
        assert isinstance(cfg.config, dict)

    def test_from_dict(self):
        cfg = Config({"a": 1, "b": 2})
        assert cfg.get("a") == 1

    def test_rejects_non_dict(self):
        with pytest.raises(TypeError):
            Config(["not", "a", "dict"])

    def test_rejects_list_from_yaml(self, tmp_path):
        bad_yaml = tmp_path / "bad.yaml"
        bad_yaml.write_text("- item1\n- item2\n")
        with pytest.raises(TypeError):
            Config(str(bad_yaml))

    def test_versions_override(self, example_config_path):
        cfg = Config(str(example_config_path), versions={"prepared_data": "v2"})
        assert cfg.get("versions", "prepared_data") == "v2"

    def test_versions_override_does_not_clobber_others(self, example_config_path):
        cfg_orig = Config(str(example_config_path))
        orig_keys = list(cfg_orig.get("versions").keys())
        cfg = Config(str(example_config_path), versions={"new_dir": "v99"})
        for key in orig_keys:
            assert cfg.get("versions", key) == cfg_orig.get("versions", key)

    def test_versions_must_be_dict(self, example_config_path):
        with pytest.raises(TypeError):
            Config(str(example_config_path), versions=["v1"])

    def test_repr_is_string(self, example_config_path):
        cfg = Config(str(example_config_path))
        assert isinstance(repr(cfg), str)
        assert len(repr(cfg)) > 0


# ---------------------------------------------------------------------------
# get()
# ---------------------------------------------------------------------------

class TestGet:
    def test_top_level(self, example_config_path):
        cfg = Config(str(example_config_path))
        assert cfg.get("a") == "foo"

    def test_nested(self, example_config_path):
        cfg = Config(str(example_config_path))
        assert cfg.get("group_c", "e") is False

    def test_no_args_returns_full_dict(self, example_config_path):
        cfg = Config(str(example_config_path))
        assert cfg.get() is cfg.config

    def test_missing_key_raises(self, example_config_path):
        cfg = Config(str(example_config_path))
        with pytest.raises(KeyError):
            cfg.get("nonexistent_key")

    def test_nested_missing_key_raises(self, example_config_path):
        cfg = Config(str(example_config_path))
        with pytest.raises(KeyError):
            cfg.get("group_c", "z")


# ---------------------------------------------------------------------------
# get_dir_path()
# ---------------------------------------------------------------------------

class TestGetDirPath:
    def test_unversioned(self, example_config_path):
        cfg = Config(str(example_config_path))
        result = cfg.get_dir_path("raw_data")
        expected = Path(cfg.get("directories", "raw_data", "path")).expanduser()
        assert result == expected

    def test_versioned(self, example_config_path):
        cfg = Config(str(example_config_path))
        result = cfg.get_dir_path("prepared_data")
        base = Path(cfg.get("directories", "prepared_data", "path")).expanduser()
        version = cfg.get("versions", "prepared_data")
        assert result == base / version

    def test_custom_version(self, example_config_path):
        cfg = Config(str(example_config_path))
        result = cfg.get_dir_path("prepared_data", custom_version="v99")
        base = Path(cfg.get("directories", "prepared_data", "path")).expanduser()
        assert result == base / "v99"

    def test_fail_if_does_not_exist(self, example_config_path):
        cfg = Config(str(example_config_path))
        with pytest.raises(FileNotFoundError):
            cfg.get_dir_path("raw_data", fail_if_does_not_exist=True)

    def test_returns_path_object(self, example_config_path):
        cfg = Config(str(example_config_path))
        assert isinstance(cfg.get_dir_path("raw_data"), Path)

    def test_versions_override_affects_dir_path(self, example_config_path):
        cfg = Config(str(example_config_path), versions={"prepared_data": "v2"})
        base = Path(cfg.get("directories", "prepared_data", "path")).expanduser()
        assert cfg.get_dir_path("prepared_data") == base / "v2"


# ---------------------------------------------------------------------------
# get_file_path()
# ---------------------------------------------------------------------------

class TestGetFilePath:
    def test_unversioned(self, example_config_path):
        cfg = Config(str(example_config_path))
        result = cfg.get_file_path("raw_data", "a")
        dir_path = cfg.get_dir_path("raw_data")
        stub = cfg.get("directories", "raw_data", "files", "a")
        assert result == dir_path / stub

    def test_versioned(self, example_config_path):
        cfg = Config(str(example_config_path))
        result = cfg.get_file_path("prepared_data", "prepared_table")
        dir_path = cfg.get_dir_path("prepared_data")
        stub = cfg.get("directories", "prepared_data", "files", "prepared_table")
        assert result == dir_path / stub

    def test_fail_if_not_exists_raises(self, config_with_tmp_dirs):
        with pytest.raises(FileNotFoundError):
            config_with_tmp_dirs.get_file_path(
                "raw_data", "a", fail_if_does_not_exist=True
            )


# ---------------------------------------------------------------------------
# read() and write()
# ---------------------------------------------------------------------------

class TestReadWrite:
    def test_write_and_read_csv(self, config_with_tmp_dirs, example_csv_path):
        import pandas as pd

        df_orig = pd.read_csv(example_csv_path)
        # Copy CSV to raw_data dir so it's at the right filename
        raw_dir = config_with_tmp_dirs.get_dir_path("raw_data")
        stub = config_with_tmp_dirs.get("directories", "raw_data", "files", "a")
        import shutil
        shutil.copy(example_csv_path, raw_dir / stub)

        df_read = config_with_tmp_dirs.read("raw_data", "a")
        assert isinstance(df_read, pd.DataFrame)
        assert df_read.shape == df_orig.shape

    def test_write_and_read_txt(self, config_with_tmp_dirs):
        lines = ["line one\n", "line two\n"]
        config_with_tmp_dirs.write(lines, "prepared_data", "summary_text")
        result = config_with_tmp_dirs.read("prepared_data", "summary_text")
        assert result == lines

    def test_read_nonexistent_raises(self, config_with_tmp_dirs):
        with pytest.raises(FileNotFoundError):
            config_with_tmp_dirs.read("raw_data", "a")


# ---------------------------------------------------------------------------
# write_self()
# ---------------------------------------------------------------------------

class TestWriteSelf:
    def test_write_self(self, config_with_tmp_dirs):
        config_with_tmp_dirs.write_self("prepared_data")
        dir_path = config_with_tmp_dirs.get_dir_path("prepared_data")
        config_yaml = dir_path / "config.yaml"
        assert config_yaml.exists()
        with open(config_yaml) as f:
            loaded = yaml.safe_load(f)
        assert loaded == config_with_tmp_dirs.config

    def test_write_self_fails_if_dir_missing(self, example_config_path):
        cfg = Config(str(example_config_path))
        with pytest.raises(FileNotFoundError):
            cfg.write_self("prepared_data")
