"""Ingesta de edificios del Catastro INSPIRE (tema Buildings)."""

import re
import os
from datetime import date
import xml.etree.ElementTree as ET
from urllib.parse import quote
import boto3

import requests

FEED_URL = (
    "http://www.catastro.hacienda.gob.es/INSPIRE/buildings/46/"
    "ES.SDGC.bu.atom_46.xml"
)
ATOM_NS = {"atom": "http://www.w3.org/2005/Atom"}
CODE_RE = re.compile(r"A\.ES\.SDGC\.BU\.(\d{5})\.zip$", re.IGNORECASE)
BUCKET = os.environ.get("DATALAKE_BUCKET", "jaromaco-flood-datalake")

def list_municipalities(feed_url: str = FEED_URL) -> list[dict]:
    """Devuelve una lista con código, nombre y URL del ZIP de cada municipio."""
    resp = requests.get(feed_url, timeout=60)
    resp.raise_for_status()

    # Pasamos bytes (no texto) para que el parser lea la codificación
    # declarada en la cabecera del XML (ISO-8859-1) y no la adivine.
    root = ET.fromstring(resp.content)

    municipalities = []
    for entry in root.findall("atom:entry", ATOM_NS):
        title = entry.findtext("atom:title", default="", namespaces=ATOM_NS)
        for link in entry.findall("atom:link", ATOM_NS):
            href = link.get("href", "")
            match = CODE_RE.search(href)
            if match:
                municipalities.append(
                    {
                        "catastro_code": match.group(1),
                        "name": title.strip(),
                        "url": quote(href, safe=":/%"),
                    }
                )
    return municipalities

def build_s3_key(catastro_code: str, ingest_date: date) -> str:
    """Ruta en bronze para el ZIP de un municipio."""
    return (
        f"bronze/catastro/buildings/ingest_date={ingest_date.isoformat()}/"
        f"A.ES.SDGC.BU.{catastro_code}.zip"
    )

def download_to_s3(muni: dict, bucket: str = BUCKET, ingest_date: date | None = None) -> str:
    """Descarga el ZIP de un municipio y lo sube a S3 sin guardarlo en disco."""
    ingest_date = ingest_date or date.today()
    key = build_s3_key(muni["catastro_code"], ingest_date)
    s3 = boto3.client("s3")
    with requests.get(muni["url"], stream=True, timeout=120) as resp:
        resp.raise_for_status()
        resp.raw.decode_content = True
        s3.upload_fileobj(
            resp.raw,
            bucket,
            key,
            ExtraArgs={
                "ContentType": "application/zip",
                "Metadata": {"source-url": muni["url"], "municipality": muni["catastro_code"]},
            },
        )
    return f"s3://{bucket}/{key}"

if __name__ == "__main__":
    munis = list_municipalities()
    print(f"Municipios encontrados: {len(munis)}")
    smallest = munis[0]
    print("Descargando:", smallest)
    print("Guardado en:", download_to_s3(smallest))
