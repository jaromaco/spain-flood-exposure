"""Un municipio de Catastro (GML) a GeoParquet."""

from pathlib import Path

import geopandas as gpd
from shapely.geometry import MultiPolygon

COLUMNS = [
    "localId",
    "reference",
    "currentUse",
    "numberOfDwellings",
    "numberOfBuildingUnits",
    "numberOfFloorsAboveGround",
    "conditionOfConstruction",
    "value",
]


def to_multipolygon(geom):
    if geom is None or geom.is_empty:
        return None
    if geom.geom_type == "Polygon":
        return MultiPolygon([geom])
    if geom.geom_type == "MultiPolygon":
        return geom
    return None


def gml_to_geoparquet(gml_path: Path, out_path: Path) -> int:
    gdf = gpd.read_file(gml_path)
    gdf["geometry"] = gdf.geometry.map(to_multipolygon)
    gdf = gdf.dropna(subset=["geometry"])
    out = gdf[COLUMNS + ["geometry"]].set_crs(25830, allow_override=True)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out.to_parquet(out_path, compression="zstd")
    return len(out)
