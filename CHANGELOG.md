# Acquifer-Python-API - Changelog

## 2.0.0 - Unreleased

### Changed
- Remove dependency on acquifer-dask and move utilitary functions to load a dataset as dask array to acquifer-napari
This is mostly to simplify the acquifer package, to avoid bloating it with extra stuff only used for acquifer-napari

### Removed
- Open_in_napari.py example