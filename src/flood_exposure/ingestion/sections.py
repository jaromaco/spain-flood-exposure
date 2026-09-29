"""Secciones censales del INE (WFS) al bronze."""

import json
import os
from datetime import date, datetime, timezone

import boto3
import requests

WFS_URL = "https://www.ine.es/geoserver/WMS_INE_SECCIONES_G01/wfs"
LAYER = "WMS_INE_SECCIONES_G01:Secciones_2025"
PROVINCE = "46"
YEAR = "2025"


def build_s3_key(ingest_date: str | None = None) -> str:
    day = ingest_date or datetime.now(timezone.utc).date().isoformat()
    return (
        f"bronze/ine/sections/year={YEAR}/province={PROVINCE}"
        f"/ingest_date={day}/secciones.geojson"
    )


def fetch_sections() -> bytes:
    """Pide solo las secciones de Valencia y devuelve el GeoJSON."""
    response = requests.get(
        WFS_URL,
        params={
            "service": "WFS",
            "version": "2.0.0",
            "request": "GetFeature",
            "typeNames": LAYER,
            "outputFormat": "application/json",
            "CQL_FILTER": f"CPRO='{PROVINCE}' AND TIPO='SECCIONADO'",
        },
        timeout=(10, 120),
    )
    response.raise_for_status()
    payload = response.content
    if not looks_like_sections(payload):
        raise ValueError("La respuesta del WFS no es el GeoJSON esperado")
    return payload


def looks_like_sections(payload: bytes) -> bool:
    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        return False
    features = data.get("features") or []
    if data.get("type") != "FeatureCollection" or not features:
        return False
    return all(f.get("properties", {}).get("TIPO") == "SECCIONADO" for f in features)


def download_to_s3(bucket: str | None = None, ingest_date: str | None = None) -> str:
    bucket = bucket or os.environ["DATALAKE_BUCKET"]
    body = fetch_sections()
    key = build_s3_key(ingest_date)
    boto3.client("s3").put_object(
        Bucket=bucket,
        Key=key,
        Body=body,
        ContentType="application/geo+json",
    )
    return f"s3://{bucket}/{key}"
