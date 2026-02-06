from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple
from scraper_thinkimmo import ThinkImmoClient, ThinkImmoQuery
# --- keep your ThinkImmoClient + ThinkImmoQuery exactly as-is above ---


@dataclass(frozen=True)
class CitySpec:
    geo_search_query: str
    geo_search_type: str = "town"   # town|city|state (as ThinkImmo uses)
    region: str = "Bayern"          # Bundesland; adjust per city if you want


class ThinkImmoCollector:
    """
    Orchestrates multi-city collection using ThinkImmoClient:
      - iterates over cities
      - paginates with offset/size
      - deduplicates listings by a stable id field (configurable)
    """

    def __init__(
        self,
        client: ThinkImmoClient,
        *,
        headers: Optional[Dict[str, str]] = None,
        items_key: str = "content",     # <-- CHANGE if API uses a different key
        id_key_candidates: Tuple[str, ...] = ("id", "_id", "objectId"),
    ) -> None:
        self.client = client
        self.headers = headers or {}
        self.items_key = items_key
        self.id_key_candidates = id_key_candidates

    def _extract_items(self, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        items = payload.get(self.items_key)
        if isinstance(items, list):
            return items

        # fallback: try common alternatives
        for k in ("items", "results", "data", "listings"):
            v = payload.get(k)
            if isinstance(v, list):
                return v

        raise KeyError(
            f"Could not find items list in payload. Tried '{self.items_key}' and common fallbacks."
        )

    def _extract_id(self, item: Dict[str, Any]) -> Optional[str]:
        for k in self.id_key_candidates:
            if k in item and item[k] is not None:
                return str(item[k])
        return None

    def collect_city(
        self,
        base_query: ThinkImmoQuery,
        city: CitySpec,
        *,
        max_pages: int = 10,
        dedupe: bool = True,
    ) -> Dict[str, Any]:
        """
        Collect listings for one city with pagination.
        Returns: {"city": ..., "pages": n, "items": [...]}.
        """
        all_items: List[Dict[str, Any]] = []
        seen: Set[str] = set()

        page = 0
        offset = base_query.offset

        while page < max_pages:
            q = ThinkImmoQuery(
                active=base_query.active,
                type=base_query.type,
                sort_by=base_query.sort_by,
                offset=offset,
                size=base_query.size,
                gross_return_and=base_query.gross_return_and,
                allow_unknown=base_query.allow_unknown,
                favorite=base_query.favorite,
                excluded_fields=base_query.excluded_fields,
                geo_search_query=city.geo_search_query,
                geo_search_type=city.geo_search_type,
                region=city.region,
                average_aggregation=base_query.average_aggregation,
                terms_aggregation=base_query.terms_aggregation,
            )

            payload = self.client.get_immo(q, headers=self.headers)
            items = self._extract_items(payload)

            if not items:
                break

            if dedupe:
                for it in items:
                    it_id = self._extract_id(it)
                    if it_id is None:
                        # If no id exists, keep it (or skip) — here we keep it.
                        all_items.append(it)
                        continue
                    if it_id not in seen:
                        seen.add(it_id)
                        all_items.append(it)
            else:
                all_items.extend(items)

            # If fewer than requested page size, likely last page
            if len(items) < base_query.size:
                break

            page += 1
            offset += base_query.size

        return {
            "city": city.geo_search_query,
            "region": city.region,
            "pages": page + 1 if all_items else 0,
            "items": all_items,
        }

    def collect_many(
        self,
        base_query: ThinkImmoQuery,
        cities: Iterable[CitySpec],
        *,
        max_pages_per_city: int = 10,
        dedupe: bool = True,
    ) -> Dict[str, Any]:
        """
        Collect for multiple cities.
        Returns: {"total_items": n, "by_city": {...}}.
        """
        by_city: Dict[str, Any] = {}
        total = 0

        for city in cities:
            result = self.collect_city(
                base_query,
                city,
                max_pages=max_pages_per_city,
                dedupe=dedupe,
            )
            by_city[city.geo_search_query] = result
            total += len(result["items"])

        return {"total_items": total, "by_city": by_city}


if __name__ == "__main__":
    client = ThinkImmoClient(ttl_seconds=60)

    # Base query template (pagination handled by collector)
    base_query = ThinkImmoQuery(
        size=20,
        offset=0,
        type="APARTMENTBUY",
        sort_by="publishDate,desc",
        # geo fields will be overridden per city
        geo_search_query="",
        geo_search_type="town",
        region="",
    )

    # 5 German cities (regions are Bundesländer)
    cities = [
        CitySpec("München", "city", "Bayern"),
        CitySpec("Berlin", "city", "Berlin"),
        CitySpec("Hamburg", "city", "Hamburg"),
        CitySpec("Köln", "city", "Nordrhein-Westfalen"),
        CitySpec("Frankfurt am Main", "city", "Hessen"),
    ]

    # If you need custom headers, set them here
    custom_headers = {}

    collector = ThinkImmoCollector(
        client,
        headers=custom_headers,
        items_key="content",  # <-- change after you inspect a sample response
    )

    dataset = collector.collect_many(
        base_query,
        cities,
        max_pages_per_city=5,  # keep small while testing
    )

    print("TOTAL ITEMS:", dataset["total_items"])
    for city_name, r in dataset["by_city"].items():
        print(city_name, "->", len(r["items"]), "items across", r["pages"], "pages")
    import json
    from pathlib import Path

    out_path = Path("thinkimmo_dataset.json")
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)

    print("Saved:", out_path.resolve())
