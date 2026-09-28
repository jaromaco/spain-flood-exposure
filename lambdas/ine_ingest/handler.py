"""Lambda de ingesta de la población del INE al bronze."""

import logging

from flood_exposure.ingestion.ine import TABLE_ID, download_to_s3

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    table_id = (event or {}).get("table_id", TABLE_ID)
    uri = download_to_s3(table_id)
    logger.info("Subido %s", uri)
    return {"table_id": table_id, "s3_uri": uri}
