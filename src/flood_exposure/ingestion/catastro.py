"""Ingesta de edificios del Catastro INSPIRE (tema Buildings)."""

import re
import xml.etree.ElementTree as ET
from urllib.parse import quote

import requests

FEED_URL = (
    "http://www.catastro.hacienda.gob.es/INSPIRE/buildings/46/"
    "ES.SDGC.bu.atom_46.xml"
)
ATOM_NS = {"atom": "http://www.w3.org/2005/Atom"}
CODE_RE = re.compile(r"A\.ES\.SDGC\.BU\.(\d{5})\.zip$", re.IGNORECASE)


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


if __name__ == "__main__":
    munis = list_municipalities()
    print(f"Municipios encontrados: {len(munis)}")
    for m in munis[:5]:
        print(m)
