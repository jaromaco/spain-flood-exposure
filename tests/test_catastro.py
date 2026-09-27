from datetime import date

from flood_exposure.ingestion.catastro import CODE_RE, build_s3_key


def test_build_s3_key():
    key = build_s3_key("46001", date(2026, 9, 26))
    assert key == (
        "bronze/catastro/buildings/ingest_date=2026-09-26/A.ES.SDGC.BU.46001.zip"
    )


def test_code_regex_extracts_code():
    url = "https://www.catastro.hacienda.gob.es/INSPIRE/Buildings/46/46900-VALENCIA/A.ES.SDGC.BU.46900.zip"
    assert CODE_RE.search(url).group(1) == "46900"


def test_code_regex_ignores_other_files():
    assert CODE_RE.search("https://ejemplo.com/metadata.xml") is None
