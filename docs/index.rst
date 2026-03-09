versioning
==========

YAML-based configuration management for versioned data pipelines, with
automatic file I/O by extension.

.. code-block:: bash

   pip install versioning

**Quick example:**

.. code-block:: python

   from versioning import Config

   cfg = Config("project_config.yaml")

   # Retrieve settings
   cfg.get("project_name")

   # Build paths (versioned or not)
   cfg.get_dir_path("results")          # ~/data/results/v1
   cfg.get_file_path("raw", "input")    # ~/data/raw/records.csv

   # Read and write by extension
   df = cfg.read("raw", "input")
   cfg.write(df.head(10), "results", "output")

   # Override the version at runtime
   cfg_v2 = Config("project_config.yaml", versions={"results": "v2"})

.. toctree::
   :maxdepth: 1
   :caption: Contents

   installation
   api
