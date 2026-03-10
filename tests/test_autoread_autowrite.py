"""Tests for autoread and autowrite."""

import pytest
import yaml

from config_versioned import autoread, autowrite, get_file_reading_functions, get_file_writing_functions


# ---------------------------------------------------------------------------
# autoread
# ---------------------------------------------------------------------------

class TestAutoread:
    def test_read_csv(self, example_csv_path):
        import pandas as pd
        result = autoread(example_csv_path)
        assert isinstance(result, pd.DataFrame)
        assert result.shape == (20, 2)
        assert list(result.columns) == ["observation", "value"]

    def test_read_yaml(self, tmp_path):
        data = {"key": "value", "nested": {"a": 1}}
        p = tmp_path / "test.yaml"
        p.write_text(yaml.dump(data))
        result = autoread(p)
        assert result == data

    def test_read_yml(self, tmp_path):
        data = {"x": 42}
        p = tmp_path / "test.yml"
        p.write_text(yaml.dump(data))
        result = autoread(p)
        assert result == data

    def test_read_txt(self, tmp_path):
        p = tmp_path / "test.txt"
        p.write_text("line one\nline two\n")
        result = autoread(p)
        assert result == ["line one\n", "line two\n"]

    def test_file_not_found(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            autoread(tmp_path / "nonexistent.csv")

    def test_is_directory_raises(self, tmp_path):
        with pytest.raises(IsADirectoryError):
            autoread(tmp_path)

    def test_no_extension_raises(self, tmp_path):
        p = tmp_path / "noext"
        p.write_text("content")
        with pytest.raises(ValueError, match="no extension"):
            autoread(p)

    def test_unsupported_extension_raises(self, tmp_path):
        p = tmp_path / "file.xyz"
        p.write_text("content")
        with pytest.raises(ValueError, match="Unsupported"):
            autoread(p)

    def test_tilde_expansion(self, tmp_path, monkeypatch):
        monkeypatch.setenv("HOME", str(tmp_path))
        p = tmp_path / "test.yaml"
        p.write_text("a: 1")
        result = autoread("~/test.yaml")
        assert result == {"a": 1}


# ---------------------------------------------------------------------------
# autowrite
# ---------------------------------------------------------------------------

class TestAutowrite:
    def test_write_yaml(self, tmp_path):
        data = {"key": "value"}
        p = tmp_path / "out.yaml"
        autowrite(data, p)
        assert p.exists()
        with open(p) as f:
            loaded = yaml.safe_load(f)
        assert loaded == data

    def test_write_yml(self, tmp_path):
        data = {"x": 99}
        p = tmp_path / "out.yml"
        autowrite(data, p)
        with open(p) as f:
            loaded = yaml.safe_load(f)
        assert loaded == data

    def test_write_csv(self, tmp_path):
        import pandas as pd
        df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
        p = tmp_path / "out.csv"
        autowrite(df, p)
        assert p.exists()

    def test_write_csv_no_index(self, tmp_path):
        import pandas as pd
        df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
        p = tmp_path / "out.csv"
        autowrite(df, p)
        result = pd.read_csv(p)
        assert list(result.columns) == ["a", "b"]

    def test_write_txt_string(self, tmp_path):
        p = tmp_path / "out.txt"
        autowrite("hello world", p)
        assert p.read_text() == "hello world"

    def test_write_txt_list(self, tmp_path):
        p = tmp_path / "out.txt"
        lines = ["line one\n", "line two\n"]
        autowrite(lines, p)
        assert p.read_text() == "line one\nline two\n"

    def test_dir_not_exist_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            autowrite({}, tmp_path / "nonexistent_dir" / "out.yaml")

    def test_no_extension_raises(self, tmp_path):
        with pytest.raises(ValueError, match="no extension"):
            autowrite({}, tmp_path / "noext")

    def test_unsupported_extension_raises(self, tmp_path):
        with pytest.raises(ValueError, match="Unsupported"):
            autowrite({}, tmp_path / "file.xyz")


# ---------------------------------------------------------------------------
# Round-trips
# ---------------------------------------------------------------------------

class TestRoundTrips:
    def test_csv_roundtrip(self, tmp_path):
        import pandas as pd
        df = pd.DataFrame({"x": [1.0, 2.0, 3.0], "y": ["a", "b", "c"]})
        p = tmp_path / "data.csv"
        autowrite(df, p)
        result = autoread(p)
        assert list(result.columns) == list(df.columns)
        assert result.shape == df.shape

    def test_yaml_roundtrip(self, tmp_path):
        data = {"a": 1, "b": [1, 2, 3], "c": {"nested": True}}
        p = tmp_path / "data.yaml"
        autowrite(data, p)
        result = autoread(p)
        assert result == data

    def test_txt_roundtrip(self, tmp_path):
        lines = ["first line\n", "second line\n"]
        p = tmp_path / "data.txt"
        autowrite(lines, p)
        result = autoread(p)
        assert result == lines


# ---------------------------------------------------------------------------
# Registry functions
# ---------------------------------------------------------------------------

class TestRegistries:
    def test_get_file_reading_functions_returns_dict(self):
        fns = get_file_reading_functions()
        assert isinstance(fns, dict)
        assert "csv" in fns
        assert "yaml" in fns
        assert "txt" in fns

    def test_get_file_writing_functions_returns_dict(self):
        fns = get_file_writing_functions()
        assert isinstance(fns, dict)
        assert "csv" in fns
        assert "yaml" in fns
        assert "txt" in fns
