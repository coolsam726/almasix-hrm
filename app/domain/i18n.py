"""XLIFF language packs and OpenID authorize URLs."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from urllib.parse import urlencode


def parse_xliff(xml_text: str) -> tuple[str, dict[str, str]]:
    """Return (target language, id -> translated string) from an XLIFF 1.2 file."""
    root = ET.fromstring(xml_text)
    file_el = root.find(".//file")
    if file_el is None:
        file_el = root
    language = file_el.attrib.get("target-language") or file_el.attrib.get("source-language") or ""
    if not language:
        raise ValueError("XLIFF file is missing a language.")
    catalog: dict[str, str] = {}
    for unit in root.iter("trans-unit"):
        unit_id = unit.attrib.get("id")
        target = unit.find("target")
        if unit_id and target is not None and target.text:
            catalog[unit_id] = target.text
    if not catalog:
        raise ValueError("XLIFF file has no translations.")
    return language, catalog


def authorize_url(*, issuer: str, client_id: str, redirect_uri: str, state: str) -> str:
    if not issuer.startswith("https://"):
        raise ValueError("The issuer must be an https URL.")
    if not client_id.strip():
        raise ValueError("A client id is required.")
    if not redirect_uri.strip() or not state.strip():
        raise ValueError("Redirect URI and state are required.")
    base = issuer.rstrip("/") + "/authorize"
    query = urlencode(
        {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "state": state,
            "response_type": "code",
            "scope": "openid",
        }
    )
    return f"{base}?{query}"
