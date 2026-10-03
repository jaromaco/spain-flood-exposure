"""Secciones censales (GeoJSON) a GeoParquet."""

from pathlib import Path

import geopandas as gpd

from flood_exposure.transform.buildings import to_multipolygon

COLUMNS = ["CUSEC", "CPRO", "CMUN", "CSEC", "NMUN", "TIPO"]


def geojson_to_geoparquet(src: Path, out_path: Path) -> int:
    gdf = gpd.read_file(src)
    gdf["geometry"] = gdf.geometry.map(to_multipolygon)
    gdf = gdf.dropna(subset=["geometry"])
    out = gdf[COLUMNS + ["geometry"]].set_crs(25830, allow_override=True)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out.to_parquet(out_path, compression="zstd")
    return len(out)
