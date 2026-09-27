#!/usr/bin/env bash
set -euo pipefail
BUILD=build/catastro_ingest
rm -rf "$BUILD" dist/catastro_ingest.zip
mkdir -p "$BUILD" dist
# Dependencias para Linux arm64 y Python 3.11 (el entorno de Lambda)
uv pip install requests \
  --target "$BUILD" \
  --python-platform aarch64-manylinux2014 \
  --python-version 3.11
# Nuestro código
cp -r src/flood_exposure "$BUILD/"
mkdir -p "$BUILD/lambdas"
cp -r lambdas/catastro_ingest "$BUILD/lambdas/"
find "$BUILD" -name "__pycache__" -type d -prune -exec rm -rf {} +
(cd "$BUILD" && zip -qr ../../dist/catastro_ingest.zip .)
ls -lh dist/catastro_ingest.zip
