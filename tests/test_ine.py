from datetime import date

from flood_exposure.ingestion.ine import build_s3_key, looks_like_ine_csv


def test_build_s3_key():
    assert build_s3_key("69277", date(2026, 9, 27)) == (
        "bronze/ine/population/table=69277/ingest_date=2026-09-27/69277.csv"
    )


def test_accepts_ine_csv_with_bom():
    content = "\ufeffMunicipios;Sexo;Periodo;Total\n".encode("utf-8")
    assert looks_like_ine_csv(content)


def test_rejects_html_error_page():
    assert not looks_like_ine_csv(b"<!DOCTYPE html><html><body>Error</body></html>")
