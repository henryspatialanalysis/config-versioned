# Remove previous build artifacts
clean:
	rm -rf dist/ build/ src/*.egg-info src/config_versioned.egg-info

# Build source distribution and wheel
build: clean
	python -m build

# Validate the distributions before uploading
check: build
	python -m twine check dist/*

# Upload to PyPI (https://pypi.org)
upload: check
	python -m twine upload dist/*

# Convenience target to print all of the available targets in this file
# From https://stackoverflow.com/questions/4219255
.PHONY: list
list:
	@LC_ALL=C $(MAKE) -pRrq -f $(lastword $(MAKEFILE_LIST)) : 2>/dev/null | \
		awk -v RS= -F: '/^# File/,/^# Finished Make data base/ \
		{if ($$1 !~ "^[#.]") {print $$1}}' | \
		sort | egrep -v -e '^[^[:alnum:]]' -e '^$@$$'
