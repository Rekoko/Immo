import json
import time
import hashlib
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

import requests


@dataclass(frozen=True)
class ThinkImmoQuery:
    """High-level query inputs -> translated into query params."""
    active: bool = True
    type: str = "APARTMENTBUY"                 # e.g. APARTMENTBUY, HOUSEBUY, ...
    sort_by: str = "publishDate,desc"          # note: pattern seen on website
    offset: int = 0
    size: int = 20
    gross_return_and: bool = False
    allow_unknown: bool = False
    favorite: bool = False
    excluded_fields: bool = True

    geo_search_query: str = "Landshut"
    geo_search_type: str = "town"              # town|city|state
    region: str = "Bayern"

    average_aggregation: str = (
        "buyingPrice;pricePerSqm;squareMeter;constructionYear;rentPrice;rentPricePerSqm;runningTime"
    )
    terms_aggregation: str = "platforms.name.keyword,60"


class ThinkImmoClient:
    """
    Minimal client for https://api.thinkimmo.com/immo

    Features:
      - Header injection per request (pass `headers=...`)
      - Proper encoding of geoSearches (JSON inside query param)
      - TTL cache (in-memory) to avoid hammering the endpoint
      - Optional ETag revalidation (If-None-Match) when cached
      - Exponential backoff for 429 + transient 5xx
    """

    def __init__(
        self,
        base_url: str = "https://api.thinkimmo.com",
        *,
        ttl_seconds: int = 60,
        max_retries: int = 6,
        base_delay: float = 0.75,
        timeout_seconds: float = 30.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.ttl_seconds = ttl_seconds
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.timeout_seconds = timeout_seconds

        self._session = requests.Session()

        # cache_key -> (expires_at, data, etag)
        self._cache: Dict[str, Tuple[float, Any, Optional[str]]] = {}

    @staticmethod
    def _canonical_key(url: str, params: Dict[str, str]) -> str:
        canonical = json.dumps(
            {"url": url, "params": params},
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
        return hashlib.sha256(canonical).hexdigest()

    @staticmethod
    def _build_params(q: ThinkImmoQuery) -> Dict[str, str]:
        geo_searches = [{
            "geoSearchQuery": q.geo_search_query,
            "geoSearchType": q.geo_search_type,
            "region": q.region,
        }]
        return {
            "active": str(q.active).lower(),
            "type": q.type,
            "sortBy": q.sort_by,
            "from": str(q.offset),
            "size": str(q.size),
            "grossReturnAnd": str(q.gross_return_and).lower(),
            "allowUnknown": str(q.allow_unknown).lower(),
            "favorite": str(q.favorite).lower(),
            "excludedFields": str(q.excluded_fields).lower(),
            # JSON array embedded into a query param, like the website does:
            "geoSearches": json.dumps(geo_searches, separators=(",", ":"), ensure_ascii=False),
            "averageAggregation": q.average_aggregation,
            "termsAggregation": q.terms_aggregation,
        }

    def get_immo(
        self,
        query: ThinkImmoQuery,
        *,
        headers: Optional[Dict[str, str]] = None,
        use_cache: bool = True,
        use_etag: bool = True,
    ) -> Any:
        """
        Fetch listings from /immo.

        headers:
          pass any request headers you want to include (e.g. tracing, app headers).
          Example: {"vercel": "...", "rId": "..."}  (if you choose to use them)

        Returns parsed JSON (dict).
        """
        url = f"{self.base_url}/immo"
        params = self._build_params(query)
        key = self._canonical_key(url, params)

        now = time.time()
        if use_cache and key in self._cache:
            expires_at, cached_data, cached_etag = self._cache[key]
            if now < expires_at and not use_etag:
                return cached_data

        # default headers (caller can override)
        req_headers: Dict[str, str] = {"Accept": "application/json"}
        if headers:
            req_headers.update(headers)

        # If we have cached ETag, ask the server if anything changed
        cached_etag: Optional[str] = None
        if use_cache and key in self._cache:
            _, cached_data, cached_etag = self._cache[key]
            if use_etag and cached_etag:
                req_headers["If-None-Match"] = cached_etag

        last_exc: Optional[Exception] = None

        for attempt in range(self.max_retries + 1):
            try:
                resp = self._session.get(
                    url,
                    params=params,
                    headers=req_headers,
                    timeout=self.timeout_seconds,
                )

                # 304 -> not modified, return cached content
                if resp.status_code == 304 and use_cache and key in self._cache:
                    expires_at, cached_data, _ = self._cache[key]
                    # extend TTL since we revalidated successfully
                    self._cache[key] = (time.time() + self.ttl_seconds, cached_data, cached_etag)
                    return cached_data

                # backoff on rate limit / transient server errors
                if resp.status_code == 429 or (500 <= resp.status_code < 600):
                    if attempt == self.max_retries:
                        resp.raise_for_status()

                    retry_after = resp.headers.get("Retry-After")
                    delay = float(retry_after) if retry_after else (self.base_delay * (2 ** attempt))
                    time.sleep(min(delay, 30.0))
                    continue

                resp.raise_for_status()

                data = resp.json()
                etag = resp.headers.get("ETag")
                if use_cache:
                    self._cache[key] = (time.time() + self.ttl_seconds, data, etag)
                return data

            except (requests.RequestException, ValueError) as e:
                last_exc = e
                if attempt == self.max_retries:
                    raise
                time.sleep(min(self.base_delay * (2 ** attempt), 30.0))

        raise last_exc or RuntimeError("Request failed unexpectedly.")


if __name__ == "__main__":
    client = ThinkImmoClient(ttl_seconds=60)

    q = ThinkImmoQuery(
        geo_search_query="Landshut",
        geo_search_type="town",
        region="Bayern",
        size=20,
        offset=0,
        type="APARTMENTBUY",
        sort_by="publishDate,desc",
    )

    # Pass headers if you want; empty headers also works if the API allows it for your case.
    # Example:
    # custom_headers = {"vercel": "<token>", "rId": "<uuid>"}
    custom_headers = {}

    result = client.get_immo(q, headers=custom_headers)
    print(json.dumps(result, indent=2, ensure_ascii=False))
