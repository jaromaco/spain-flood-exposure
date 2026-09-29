import json
from flood_exposure.ingestion.sections import build_s3_key, looks_like_sections

def test_build_s3_key():
    assert build_s3_key("2026-09-29") == (
        "bronze/ine/sections/year=2025/province=46"
        "/ingest_date=2026-09-29/secciones.geojson"
    )

def test_rejects_html():
    assert looks_like_sections(b"<html>error</html>") is False

def test_accepts_only_sections():
    ok = {"type": "FeatureCollection", "features": [
        {"properties": {"TIPO": "SECCIONADO"}}
    ]}
    assert looks_like_sections(json.dumps(ok).encode()) is True

def test_rejects_districts():
    bad = {"type": "FeatureCollection", "features": [
        {"properties": {"TIPO": "DISTRITO"}}
    ]}
    assert looks_like_sections(json.dumps(bad).encode()) is False
