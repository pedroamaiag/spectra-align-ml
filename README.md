# Spectra Align ML

Supervised learning for approximating Sentinel-2 Level-2A products from Level-1C imagery over the Caatinga biome in Ceará, Brazil.

The study compares model performance during dry and rainy seasons.

## Documentation

- [Problem Definition](docs/problem-definition.md)
- [Deep Learning Literature Review](docs/literature-review-deep-learning.md)
- [Atmospheric Correction Benchmarks](docs/literature-review-benchmarks.md)
- [Environment Setup](docs/environment-setup.md)

## Structure

- `gee/` — Data collection
- `src/` — Python scripts
- `data/` — Satellite imagery
- `outputs/` — Generated previews

## Stack

Google Earth Engine, Python, PyTorch, Rasterio, NumPy, Matplotlib, scikit-image and scikit-learn.
