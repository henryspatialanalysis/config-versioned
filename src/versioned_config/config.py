"""Config class for YAML-based pipeline configuration with versioned directories."""

import os
import pprint
from pathlib import Path

from versioned_config.utilities import pull_from_config
from versioned_config.autoread import autoread
from versioned_config.autowrite import autowrite


class Config:
    """Configuration object for versioned file I/O pipelines.

    Loads settings from a YAML file (or a plain dict) and provides methods
    to construct directory and file paths, read files, and write files. Supports
    versioned directories where the full path is ``{base_path}/{version}``.

    The ``directories`` key in the config dict is special. Each entry must have:
    - ``versioned`` (bool): whether the directory has version subdirectories
    - ``path`` (str): base path to the directory
    - ``files`` (dict): named file stubs within the directory

    For versioned directories, a corresponding entry must exist in the
    ``versions`` dict (top-level key) whose value is the version string for
    the current run.

    Parameters
    ----------
    config : dict, str, or Path
        Either a dict of settings or a filepath to a YAML file.
    versions : dict, optional
        Key/value pairs to set or override in ``config['versions']``.

    Attributes
    ----------
    config : dict
        The dictionary representation of the loaded configuration.

    Examples
    --------
    >>> import importlib.resources as r
    >>> p = str(r.files("versioning") / "data" / "example_config.yaml")
    >>> cfg = Config(p)
    >>> cfg.get("a")
    'foo'
    >>> cfg.get_dir_path("prepared_data")
    PosixPath('/path/to/prepared_data/v1')
    """

    def __init__(self, config, versions=None):
        if isinstance(config, (str, Path)):
            config = autoread(config)
        if not isinstance(config, dict):
            raise TypeError(
                f"config must be a dict or a path to a YAML file, "
                f"got {type(config).__name__}"
            )
        if versions is not None:
            if not isinstance(versions, dict):
                raise TypeError(
                    f"versions must be a dict, got {type(versions).__name__}"
                )
            config.setdefault("versions", {}).update(versions)
        self.config = config

    def __repr__(self):
        return pprint.pformat(self.config)

    def get(self, *keys, **kwargs):
        """Retrieve a nested value from the config.

        Parameters
        ----------
        *keys : str or int
            Sequential keys to traverse the config dict.
        **kwargs
            Keyword arguments passed to ``pull_from_config``, e.g.
            ``fail_if_none=False`` to return ``None`` instead of raising
            when a key is missing or the value is ``None``.

        Returns
        -------
        The value at the specified path. Returns the full config dict if
        no keys are provided.

        Raises
        ------
        KeyError
            If a key does not exist at any level (unless ``fail_if_none=False``).
        """
        if not keys:
            return self.config
        return pull_from_config(self.config, *keys, **kwargs)

    def get_dir_path(self, dir_name, custom_version=None, fail_if_does_not_exist=False):
        """Construct the full path for a named directory.

        For non-versioned directories, returns the base path. For versioned
        directories, returns ``{base_path}/{version}``.

        Parameters
        ----------
        dir_name : str
            Name of the directory as defined in ``config['directories']``.
        custom_version : str, optional
            Override the version for this call instead of using
            ``config['versions'][dir_name]``.
        fail_if_does_not_exist : bool, default False
            Raise FileNotFoundError if the directory does not exist on disk.

        Returns
        -------
        pathlib.Path
            Full path to the directory.
        """
        dir_info = self.get("directories", dir_name)
        versioned = pull_from_config(dir_info, "versioned")
        base_path = pull_from_config(dir_info, "path")
        if not isinstance(versioned, bool):
            raise TypeError(
                f"'versioned' for directory '{dir_name}' must be bool, "
                f"got {type(versioned).__name__}"
            )
        if versioned:
            version = custom_version if custom_version is not None else self.get("versions", dir_name)
            dir_path = Path(os.path.expanduser(base_path)) / version
        else:
            dir_path = Path(os.path.expanduser(base_path))
        if fail_if_does_not_exist and not dir_path.exists():
            raise FileNotFoundError(f"Directory '{dir_path}' does not exist.")
        return dir_path

    def get_file_path(self, dir_name, file_name, custom_version=None, fail_if_does_not_exist=False):
        """Construct the full path for a named file within a directory.

        Parameters
        ----------
        dir_name : str
            Name of the directory as defined in ``config['directories']``.
        file_name : str
            Name of the file as defined in ``config['directories'][dir_name]['files']``.
        custom_version : str, optional
            Override the directory version for this call.
        fail_if_does_not_exist : bool, default False
            Raise FileNotFoundError if the file does not exist on disk.

        Returns
        -------
        pathlib.Path
            Full path to the file.
        """
        dir_path = self.get_dir_path(
            dir_name, custom_version=custom_version,
            fail_if_does_not_exist=fail_if_does_not_exist
        )
        file_stub = self.get("directories", dir_name, "files", file_name)
        file_path = dir_path / file_stub
        if fail_if_does_not_exist and not file_path.exists():
            raise FileNotFoundError(f"File '{file_path}' does not exist.")
        return file_path

    def read(self, dir_name, file_name, custom_version=None, **kwargs):
        """Read a file using autoread, resolving the path from the config.

        Parameters
        ----------
        dir_name : str
            Directory name from ``config['directories']``.
        file_name : str
            File name from ``config['directories'][dir_name]['files']``.
        custom_version : str, optional
            Override the directory version for this call.
        **kwargs
            Additional keyword arguments passed to the format-specific reader.

        Returns
        -------
        The object loaded from the file.
        """
        file_path = self.get_file_path(
            dir_name, file_name,
            custom_version=custom_version,
            fail_if_does_not_exist=True
        )
        return autoread(file_path, **kwargs)

    def write(self, x, dir_name, file_name, custom_version=None, **kwargs):
        """Write an object to a file using autowrite, resolving the path from config.

        Parameters
        ----------
        x : object
            The object to write.
        dir_name : str
            Directory name from ``config['directories']``.
        file_name : str
            File name from ``config['directories'][dir_name]['files']``.
        custom_version : str, optional
            Override the directory version for this call.
        **kwargs
            Additional keyword arguments passed to the format-specific writer.
        """
        file_path = self.get_file_path(
            dir_name, file_name,
            custom_version=custom_version,
            fail_if_does_not_exist=False
        )
        autowrite(x, file_path, **kwargs)

    def write_self(self, dir_name, custom_version=None, **kwargs):
        """Write the config dict as ``config.yaml`` to a directory.

        Parameters
        ----------
        dir_name : str
            Directory name from ``config['directories']``. The directory
            must already exist on disk.
        custom_version : str, optional
            Override the directory version for this call.
        **kwargs
            Additional keyword arguments passed to the YAML writer.
        """
        dir_path = self.get_dir_path(
            dir_name, custom_version=custom_version,
            fail_if_does_not_exist=True
        )
        file_path = dir_path / "config.yaml"
        autowrite(self.config, file_path, **kwargs)
