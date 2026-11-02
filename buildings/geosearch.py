"""Adapter for NYC Planning's public GeoSearch API."""

import json
import ssl
from dataclasses import dataclass
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import urlopen

import truststore

BASE_URL = "https://geosearch.planninglabs.nyc/v2"
SEARCH_ENDPOINT = "search"
AUTOCOMPLETE_ENDPOINT = "autocomplete"
REQUEST_TIMEOUT_SECONDS = 5
RESULT_LIMIT = 10
SERVICE_ERROR_MESSAGE = (
    "Address search is temporarily unavailable. Please try again shortly."
)

# GeoSearch response field names.
FEATURES_FIELD = "features"
PROPERTIES_FIELD = "properties"
LABEL_FIELD = "label"
ADDRESS_FIELD = "name"
BOROUGH_FIELD = "borough"
LOCALITY_FIELD = "locality"
ZIP_CODE_FIELD = "postalcode"
PROVIDER_ID_FIELD = "gid"
ADDENDUM_FIELD = "addendum"
PAD_FIELD = "pad"
BUILDING_ID_FIELD = "bin"


class ThirdPartyServiceError(Exception):
    """An expected failure communicating with an external service."""


@dataclass(frozen=True)
class AddressResult:
    label: str
    address: str
    borough: str
    zip_code: str
    provider_id: str = ""
    building_id: str = ""


def search_addresses(query, *, autocomplete=False):
    """Return NYC address matches, translating expected provider failures."""
    query = query.strip()
    if not query:
        return []

    endpoint = AUTOCOMPLETE_ENDPOINT if autocomplete else SEARCH_ENDPOINT
    
    try:
        payload = _request_addresses(query, endpoint)
        features = _require_mapping(payload)[FEATURES_FIELD]
        
        if not isinstance(features, list):
            raise ValueError("Expected a list of address features")
        return [_parse_address(feature) for feature in features]
    except (URLError, OSError, KeyError, TypeError, ValueError) as exc:
        raise ThirdPartyServiceError(SERVICE_ERROR_MESSAGE) from exc


def _request_addresses(query, endpoint):
    """Fetch JSON using verified HTTPS and a bounded timeout."""
    parameters = urlencode({"text": query, "size": RESULT_LIMIT})
    url = f"{BASE_URL}/{endpoint}?{parameters}"
    with urlopen(
        url,
        timeout=REQUEST_TIMEOUT_SECONDS,
        context=truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT),
    ) as response:
        return json.load(response)


def _parse_address(feature):
    """Convert a provider feature to our application address type."""
    props = _require_mapping(_require_mapping(feature)[PROPERTIES_FIELD])
    pad = _require_mapping(_require_mapping(props.get(ADDENDUM_FIELD, {})).get(PAD_FIELD, {}))
    fields = {
        "label": props[LABEL_FIELD],
        "address": props.get(ADDRESS_FIELD) or props[LABEL_FIELD],
        "borough": props.get(BOROUGH_FIELD) or props.get(LOCALITY_FIELD) or "",
        "zip_code": props.get(ZIP_CODE_FIELD) or "",
        "provider_id": props.get(PROVIDER_ID_FIELD, ""),
        "building_id": pad.get(BUILDING_ID_FIELD, ""),
    }
    if not all(isinstance(value, str) for value in fields.values()):
        raise ValueError("Invalid address fields")
    return AddressResult(**fields)


def _require_mapping(value):
    if not isinstance(value, dict):
        raise ValueError("Expected an object in the address response")
    return value
