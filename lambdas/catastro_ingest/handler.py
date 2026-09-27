"""Lambda: descarga edificios del Catastro de uno o varios municipios a bronze."""

import logging

from flood_exposure.ingestion.catastro import download_to_s3, list_municipalities

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    codes = event.get("catastro_codes")  # p. ej. ["46001", "46002"]; None = todos
    munis = list_municipalities()
    if codes:
        munis = [m for m in munis if m["catastro_code"] in codes]

    ok, failed = [], []
    for muni in munis:
        # Paramos con margen si se acaba el tiempo de la Lambda
        if context and context.get_remaining_time_in_millis() < 30_000:
            logger.warning("Tiempo casi agotado, quedan municipios sin procesar")
            break
        try:
            uri = download_to_s3(muni)
            logger.info("OK %s -> %s", muni["catastro_code"], uri)
            ok.append(muni["catastro_code"])
        except Exception:
            logger.exception("Fallo en %s", muni["catastro_code"])
            failed.append(muni["catastro_code"])

    pending = [m["catastro_code"] for m in munis if m["catastro_code"] not in ok + failed]
    return {"ok": len(ok), "failed": failed, "pending": pending}
