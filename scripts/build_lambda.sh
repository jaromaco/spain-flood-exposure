#!/usr/bin/env bash
# Uso: ./scripts/build_lambda.sh <nombre>   (p. ej. catastro_ingest, ine_ingest)
set -euo pipefail

NAME="${1:?Indica el nombre de la lambda, p. ej. catastro_ingest}"
[[ -d "lambdas/$NAME" ]] || { echo "No existe lambdas/$NAME" >&2; exit 1; }

BUILD="build/$NAME"
ZIP="dist/$NAME.zip"
rm -rf "$BUILD" "$ZIP"
mkdir -p "$BUILD" dist

uv pip install requests \
  --target "$BUILD" \
  --python-platform aarch64-manylinux2014 \
  --python-version 3.11

cp -r src/flood_exposure "$BUILD/"
mkdir -p "$BUILD/lambdas"
cp -r "lambdas/$NAME" "$BUILD/lambdas/"
find "$BUILD" -name "__pycache__" -type d -prune -exec rm -rf {} +

(cd "$BUILD" && zip -qr "../../$ZIP" .)
ls -lh "$ZIP"
