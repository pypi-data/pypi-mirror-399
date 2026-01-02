# staticjinjaplus

A sweet spot between [staticjinja](https://staticjinja.readthedocs.io/en/latest/) and a full-blown static  site generator.

![Python versions](https://img.shields.io/pypi/pyversions/staticjinjaplus.svg) ![Version](https://img.shields.io/pypi/v/staticjinjaplus.svg) ![License](https://img.shields.io/pypi/l/staticjinjaplus.svg)

[PyPI](https://pypi.org/project/staticjinjaplus/) - [Documentation](https://epocdotfr.github.io/staticjinjaplus/) - [Source code](https://github.com/EpocDotFr/staticjinjaplus) - [Issue tracker](https://github.com/EpocDotFr/staticjinjaplus/issues) - [Changelog](https://github.com/EpocDotFr/staticjinjaplus/releases)

## Development

### Getting source code and installing the package with dev dependencies

  1. Clone the repository
  2. From the root directory, run: `pip install -e ".[dev]"`

### Releasing the package

From the root directory, run `python setup.py upload`. This will build the package, create a git tag and publish on PyPI.

`__version__` in `staticjinjaplus/__version__.py` must be updated beforehand. It should adhere to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

An associated GitHub release must be created following the [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format.
