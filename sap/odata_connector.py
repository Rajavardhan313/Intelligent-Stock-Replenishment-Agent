import os
import time
import requests
from urllib.parse import urljoin
from dotenv import load_dotenv

load_dotenv()

ODATA_BASE = os.getenv("ODATA_BASE_URL")     # e.g. https://your-sap-host/sap/opu/odata/sap/
ODATA_USER = os.getenv("ODATA_USER")
ODATA_PASS = os.getenv("ODATA_PASS")
ODATA_TOKEN = os.getenv("ODATA_BEARER_TOKEN")  # if using token-based auth
REQUEST_TIMEOUT = int(os.getenv("ODATA_TIMEOUT", "30"))
MAX_RETRIES = int(os.getenv("ODATA_MAX_RETRIES", "3"))
RETRY_DELAY = float(os.getenv("ODATA_RETRY_DELAY", "2.0"))

def _get_auth():
    if ODATA_TOKEN:
        return {"Authorization": f"Bearer {ODATA_TOKEN}"}
    if ODATA_USER and ODATA_PASS:
        # requests will use tuple auth; headers remain None for basic auth
        return (ODATA_USER, ODATA_PASS)
    return None

def fetch_odata_entity(entity_path: str, params: dict = None, headers: dict = None):
    """
    Fetch OData entity set with pagination support.
    entity_path: e.g. 'ZINVENTORY_SRV/InventorySet' or 'API_MATERIAL/Inventory'
    params: dict of OData query params ($select, $filter, $top, $orderby)
    returns: list of JSON records
    """
    if not ODATA_BASE:
        raise ValueError("ODATA_BASE_URL is not configured in .env")

    url = urljoin(ODATA_BASE, entity_path)
    results = []

    # support either Basic auth (tuple) or bearer token header
    auth = None
    req_headers = {}
    if ODATA_TOKEN:
        req_headers["Authorization"] = f"Bearer {ODATA_TOKEN}"
    elif ODATA_USER and ODATA_PASS:
        auth = (ODATA_USER, ODATA_PASS)

    if headers:
        req_headers.update(headers)

    attempt = 0
    while url:
        attempt += 1
        for r in range(MAX_RETRIES):
            try:
                resp = requests.get(url, params=params, headers=req_headers, auth=auth, timeout=REQUEST_TIMEOUT)
                resp.raise_for_status()
                break
            except requests.RequestException as exc:
                last_exc = exc
                time.sleep(RETRY_DELAY)
        else:
            # retries exhausted
            raise last_exc

        body = resp.json()

        # OData V2 usually has 'd' wrapper with 'results'; V4 returns 'value' list
        if isinstance(body, dict):
            if "d" in body:
                # v2 style
                inner = body["d"]
                if isinstance(inner, dict) and "results" in inner:
                    results.extend(inner["results"])
                elif isinstance(inner, list):
                    results.extend(inner)
                else:
                    # single record
                    results.append(inner)
            elif "value" in body:
                results.extend(body["value"])
            else:
                # fallback: entire body as single record
                results.append(body)
        else:
            # if it's a list already
            if isinstance(body, list):
                results.extend(body)
            else:
                results.append(body)

        # pagination check for next link (v4: @odata.nextLink, v2: d.__next)
        next_link = None
        if isinstance(body, dict):
            next_link = body.get("@odata.nextLink") or (body.get("d") and body["d"].get("__next"))
        url = next_link

        # For subsequent requests, params should be None because nextLink contains everything
        params = None

    return results
