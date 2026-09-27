"""Ingesta de la tabla de población del INE al bronze."""

import os
from datetime import date

import boto3
import requests

TABLE_ID = "69277"
BUCKET = os.environ.get("DATALAKE_BUCKET", "jaromaco-flood-datalake")


def csv_url(table_id: str) -> str:
    return f"https://www.ine.es/jaxiT3/files/t/es/csv_bdsc/{table_id}.csv"


def build_s3_key(table_id: str, ingest_date: date) -> str:
    return (
        f"bronze/ine/population/table={table_id}/"
        f"ingest_date={ingest_date.isoformat()}/{table_id}.csv"
    )


def looks_like_ine_csv(first_bytes: bytes) -> bool:
    """True si el contenido parece un CSV del INE y no una página HTML."""
    text = first_bytes.decode("utf-8-sig", errors="replace").lstrip().lower()
    return not text.startswith(("<!doctype", "<html")) and ";" in text


def download_to_s3(table_id: str = TABLE_ID) -> str:
    url = csv_url(table_id)
    resp = requests.get(url, timeout=(10, 300))
    resp.raise_for_status()

    if not looks_like_ine_csv(resp.content[:2048]):
        raise ValueError(f"La respuesta de {url} no parece un CSV del INE")

    key = build_s3_key(table_id, date.today())
    boto3.client("s3").put_object(
        Bucket=BUCKET,
        Key=key,
        Body=resp.content,
        ContentType="text/csv; charset=utf-8",
        Metadata={"source-url": url, "table-id": table_id},
    )
    return f"s3://{BUCKET}/{key}"


if __name__ == "__main__":
    print(download_to_s3())
