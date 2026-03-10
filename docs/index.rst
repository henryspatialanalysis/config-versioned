versioning
==========

YAML-based configuration management for versioned data pipelines, with
automatic file I/O by extension.

.. code-block:: bash

   pip install config-versioned

**Quick example:**

.. code-block:: python

   import importlib.resources as r
   from config_versioned import Config

   # Load the bundled example config
   path = str(r.files("config_versioned") / "data" / "example_config.yaml")
   cfg = Config(path)

   # Retrieve settings (top-level and nested)
   cfg.get("a")                  # 'foo'
   cfg.get("group_c", "e")       # False

   # Build paths (versioned and non-versioned directories)
   cfg.get_dir_path("raw_data")       # PosixPath('.../raw_data')
   cfg.get_dir_path("prepared_data")  # PosixPath('.../prepared_data/v1')
   cfg.get_file_path("raw_data", "a") # PosixPath('.../raw_data/example_input_file.csv')

   # Override the version at runtime — all path lookups update automatically
   cfg_v2 = Config(path, versions={"prepared_data": "v2"})
   cfg_v2.get_dir_path("prepared_data")  # PosixPath('.../prepared_data/v2')

.. toctree::
   :maxdepth: 1
   :caption: Contents

   getting_started
   installation
   api
