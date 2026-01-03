# 3dmath

A header-only 3D math library used for building apps like [MeshViewer](https://github.com/mdh81/meshviewer)

[![Quality](https://github.com/mdh81/3dmath/actions/workflows/cmake-single-platform.yml/badge.svg)](https://github.com/mdh81/3dmath/actions/workflows/cmake-single-platform.yml)

## Python Bindings

Python bindings are generated using the excellent [pybind11](https://github.com/pybind/pybind11) library

### Building and testing python bindings

Poetry is a prerequisite. Install it via usual channels (e.g. `brew install poetry`) 

```bash
$ cd <path to 3dmath>
$ poetry config --local virtualenvs.in-project true (optional, use if in-project venvs are not set globally)
$ poetry install 
$ poetry run python -m build
$ source .venv/bin/activate
$ python
> import math3d
```