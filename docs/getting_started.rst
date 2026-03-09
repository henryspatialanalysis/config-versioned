Getting Started
===============

This guide introduces the **versioned-config** package, which simplifies management of
project settings and file I/O by combining them in a single :class:`~versioned_config.Config`
object.

Data pipelines commonly require reading and writing data to versioned directories. Each
directory might correspond to one step of a multi-step process, where the version
corresponds to particular settings for that step and a chain of prior steps that each
have their own respective versions. The :class:`~versioned_config.Config` class makes it easy
to read and write versioned data based on YAML configuration files that can be saved
alongside each versioned output folder.

Loading a config file
---------------------

YAML is a natural format for storing project settings, since it can represent numeric,
string, and boolean settings as well as hierarchically nested values. The
**versioning** package ships with an example config file you can use to follow along:

.. code-block:: python

    import importlib.resources as r
    from versioned_config import Config

    example_config_path = str(r.files("versioned_config") / "data" / "example_config.yaml")

The example YAML file looks like this:

.. code-block:: yaml

    a: 'foo'
    b: ['bar', 'baz']
    group_c:
      d: 1e5
      e: false
    directories:
      raw_data:
        versioned: false
        path: '~/versioning_test/raw_data'
        files:
          a: 'example_input_file.csv'
      prepared_data:
        versioned: true
        path: '~/versioning_test/prepared_data'
        files:
          prepared_table: 'example_prepared_table.csv'
          summary_text:   'summary_of_rows.txt'
    versions:
      prepared_data: 'v1'

Create a :class:`~versioned_config.Config` object by passing either a path to a YAML file
or a plain Python dict. The full config is stored in the ``config`` attribute:

.. code-block:: python

    config = Config(example_config_path)
    print(config)   # pprint-formatted view of the config dict

Retrieving settings
-------------------

You can access the config dict directly (``config.config["a"]``), but
:meth:`~versioned_config.Config.get` is preferable — it raises a clear ``KeyError`` if a
setting is missing rather than returning ``None`` silently:

.. code-block:: python

    config.get("a")               # 'foo'
    config.get("b")               # ['bar', 'baz']
    config.get("group_c", "d")    # 100000.0  (nested access)

    # Returns None instead of raising, when fail_if_none=False
    config.get("nonexistent", fail_if_none=False)   # None

Settings can be updated in place by editing ``config.config`` directly:

.. code-block:: python

    config.config["a"] = 12345
    config.get("a")   # 12345

Working with directories
------------------------

Two top-level keys — ``directories`` and ``versions`` — give the
:class:`~versioned_config.Config` object its versioning capability. Each entry under
``directories`` must have:

- **versioned** (bool) — whether the directory has version subdirectories
- **path** (str) — base path to the directory (tilde expansion applied)
- **files** (dict) — named file stubs within the directory

For **versioned** directories the full path is ``{path}/{version}``, where the version
string comes from the ``versions`` dict. For **non-versioned** directories the full
path is just ``path``.

Use :meth:`~versioned_config.Config.get_dir_path` and
:meth:`~versioned_config.Config.get_file_path` to build these paths:

.. code-block:: python

    import tempfile, shutil
    from pathlib import Path

    # Redirect both directories to temporary folders for this example
    tmp = Path(tempfile.mkdtemp())
    raw_dir      = tmp / "raw_data"
    prepared_dir = tmp / "prepared_data"
    raw_dir.mkdir()
    prepared_dir.mkdir()

    config.config["directories"]["raw_data"]["path"]      = str(raw_dir)
    config.config["directories"]["prepared_data"]["path"] = str(prepared_dir)

    # get_dir_path() returns a pathlib.Path
    config.get_dir_path("raw_data")       # tmp/raw_data   (not versioned)
    config.get_dir_path("prepared_data")  # tmp/prepared_data/v1  (versioned → appends version)

    # Create the versioned subdirectory
    config.get_dir_path("prepared_data").mkdir()

    # get_file_path() appends the named file stub
    config.get_file_path("raw_data", "a")
    # tmp/raw_data/example_input_file.csv

    config.get_file_path("prepared_data", "prepared_table")
    # tmp/prepared_data/v1/example_prepared_table.csv

Notice that the "prepared_data" path ends in ``v1`` because
``config.get("versions", "prepared_data")`` is ``"v1"``. Changing that setting changes
where all subsequent reads and writes for that directory go.

Reading and writing files
-------------------------

Copy the bundled example CSV into the raw data directory, then use
:meth:`~versioned_config.Config.read` and :meth:`~versioned_config.Config.write` to move data
through the pipeline:

.. code-block:: python

    # Copy the example input file into the raw_data directory
    example_csv = str(r.files("versioned_config") / "data" / "example_input_file.csv")
    shutil.copy(example_csv, config.get_file_path("raw_data", "a"))

    # Read the CSV (returns a pandas DataFrame)
    df = config.read("raw_data", "a")

    # Write a prepared table and a plain-text summary to the versioned directory
    config.write(df, "prepared_data", "prepared_table")
    config.write(
        f"The prepared table has {len(df)} rows and {len(df.columns)} columns.\n",
        "prepared_data",
        "summary_text",
    )

    # Both files now appear in the versioned directory
    list(config.get_dir_path("prepared_data").iterdir())

These methods delegate to :func:`~versioned_config.autoread` and
:func:`~versioned_config.autowrite`, which dispatch on file extension. To see every
supported extension:

.. code-block:: python

    from versioned_config import get_file_reading_functions, get_file_writing_functions

    sorted(get_file_reading_functions().keys())
    sorted(get_file_writing_functions().keys())

Saving the config alongside outputs
------------------------------------

:meth:`~versioned_config.Config.write_self` writes the current config dict as
``config.yaml`` into a named directory. This is useful for reproducibility — you can
always see exactly which settings produced a given set of outputs:

.. code-block:: python

    config.write_self("prepared_data")

    # config.yaml now appears alongside the outputs
    list(config.get_dir_path("prepared_data").iterdir())

Overriding versions at runtime
-------------------------------

Rather than editing the YAML file between runs, you can pass a ``versions`` dict when
constructing a :class:`~versioned_config.Config` object. This sets or overwrites the
specified versions while leaving all other settings unchanged — useful for command-line
scripts or automated pipelines:

.. code-block:: python

    config_v2 = Config(example_config_path, versions={"prepared_data": "v2"})

    config_v2.get_dir_path("prepared_data")
    # tmp/prepared_data/v2

    # Other versions (and all other settings) are untouched
    config_v2.get("versions", "prepared_data")   # 'v2'

Next steps
----------

- :doc:`installation` — full installation options and supported file extensions
- :doc:`api` — complete API reference
