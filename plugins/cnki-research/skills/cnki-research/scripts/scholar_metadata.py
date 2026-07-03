#!/usr/bin/env python3
"""Retrieve scholarly metadata from OpenAlex or Crossref using stdlib only."""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any


USER_AGENT = "cnki-research-codex-skill/1.0"
DOI_RE = re.compile(r"^10\.\d{4,9}/[-._;()/:A-Z0-9]+$", re.IGNORECASE)


def request_json(url: str) -> dict[str, Any]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        raise SystemExit(f"HTTP {exc.code}: {exc.reason}") from exc
    except urllib.error.URLError as exc:
        raise SystemExit(f"Network error: {exc.reason}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit("The metadata service returned invalid JSON.") from exc


def normalize_doi(value: str) -> str:
    doi = value.strip()
    for prefix in ("https://doi.org/", "http://doi.org/", "doi:"):
        if doi.lower().startswith(prefix):
            doi = doi[len(prefix) :]
            break
    if not DOI_RE.fullmatch(doi):
        raise SystemExit("Invalid DOI syntax.")
    return doi


def openalex_search(args: argparse.Namespace) -> dict[str, Any]:
    filters: list[str] = []
    if args.from_year or args.to_year:
        start = args.from_year or 1000
        end = args.to_year or 9999
        if start > end:
            raise SystemExit("--from-year cannot be later than --to-year.")
        filters.append(f"from_publication_date:{start}-01-01")
        filters.append(f"to_publication_date:{end}-12-31")
    params = {"search": args.query, "per-page": args.limit}
    if filters:
        params["filter"] = ",".join(filters)
    if args.sort == "cited":
        params["sort"] = "cited_by_count:desc"
    url = "https://api.openalex.org/works?" + urllib.parse.urlencode(params)
    payload = request_json(url)
    return {
        "source": "OpenAlex",
        "query": args.query,
        "count": len(payload.get("results", [])),
        "results": [simplify_openalex(item) for item in payload.get("results", [])],
    }


def crossref_search(args: argparse.Namespace) -> dict[str, Any]:
    params: dict[str, Any] = {"query": args.query, "rows": args.limit}
    filters: list[str] = []
    if args.from_year:
        filters.append(f"from-pub-date:{args.from_year}-01-01")
    if args.to_year:
        filters.append(f"until-pub-date:{args.to_year}-12-31")
    if filters:
        params["filter"] = ",".join(filters)
    if args.sort == "cited":
        params.update({"sort": "is-referenced-by-count", "order": "desc"})
    url = "https://api.crossref.org/works?" + urllib.parse.urlencode(params)
    items = request_json(url).get("message", {}).get("items", [])
    return {
        "source": "Crossref",
        "query": args.query,
        "count": len(items),
        "results": [simplify_crossref(item) for item in items],
    }


def simplify_openalex(item: dict[str, Any]) -> dict[str, Any]:
    location = item.get("primary_location") or {}
    source = location.get("source") or {}
    return {
        "title": item.get("title"),
        "authors": [
            (entry.get("author") or {}).get("display_name")
            for entry in item.get("authorships", [])
            if (entry.get("author") or {}).get("display_name")
        ],
        "publication_year": item.get("publication_year"),
        "publication_date": item.get("publication_date"),
        "source_title": source.get("display_name"),
        "doi": item.get("doi"),
        "type": item.get("type"),
        "cited_by_count": item.get("cited_by_count"),
        "landing_page_url": location.get("landing_page_url"),
        "pdf_url": location.get("pdf_url"),
        "is_open_access": (item.get("open_access") or {}).get("is_oa"),
        "open_access_url": (item.get("open_access") or {}).get("oa_url"),
        "openalex_id": item.get("id"),
    }


def first(value: Any) -> Any:
    return value[0] if isinstance(value, list) and value else None


def crossref_year(item: dict[str, Any]) -> int | None:
    for key in ("published-print", "published-online", "published", "issued"):
        parts = (item.get(key) or {}).get("date-parts") or []
        if parts and parts[0]:
            return parts[0][0]
    return None


def simplify_crossref(item: dict[str, Any]) -> dict[str, Any]:
    authors = []
    for author in item.get("author", []):
        name = " ".join(part for part in (author.get("given"), author.get("family")) if part)
        if name:
            authors.append(name)
    return {
        "title": first(item.get("title")),
        "authors": authors,
        "publication_year": crossref_year(item),
        "source_title": first(item.get("container-title")),
        "volume": item.get("volume"),
        "issue": item.get("issue"),
        "pages": item.get("page"),
        "publisher": item.get("publisher"),
        "doi": item.get("DOI"),
        "type": item.get("type"),
        "cited_by_count": item.get("is-referenced-by-count"),
        "landing_page_url": item.get("URL"),
    }


def lookup_doi(doi: str, source: str) -> dict[str, Any]:
    normalized = normalize_doi(doi)
    if source == "openalex":
        encoded = urllib.parse.quote("https://doi.org/" + normalized, safe="")
        data = request_json(f"https://api.openalex.org/works/{encoded}")
        return {"source": "OpenAlex", "result": simplify_openalex(data)}
    encoded = urllib.parse.quote(normalized, safe="")
    data = request_json(f"https://api.crossref.org/works/{encoded}").get("message", {})
    return {"source": "Crossref", "result": simplify_crossref(data)}


def author_text(authors: list[str]) -> str:
    if not authors:
        return "[author unavailable]"
    return ", ".join(authors)


def citation(record: dict[str, Any], style: str) -> str:
    authors = author_text(record.get("authors") or [])
    year = record.get("publication_year") or "n.d."
    title = record.get("title") or "[title unavailable]"
    journal = record.get("source_title") or "[source unavailable]"
    doi = record.get("doi") or ""
    doi = doi if str(doi).startswith("http") else (f"https://doi.org/{doi}" if doi else "")
    if style == "apa":
        return f"{authors} ({year}). {title}. {journal}. {doi}".rstrip()
    if style == "gbt7714":
        volume = record.get("volume") or ""
        issue = record.get("issue") or ""
        pages = record.get("pages") or ""
        vol_issue = volume + (f"({issue})" if issue else "")
        tail = ": ".join(part for part in (vol_issue, pages) if part)
        base = f"{authors}. {title}[J]. {journal}, {year}"
        return base + (f", {tail}" if tail else "") + (f". {doi}" if doi else ".")
    key_family = re.sub(r"\W+", "", (record.get("authors") or ["ref"])[0].split()[-1])
    key = f"{key_family}{year}"
    fields = {
        "author": " and ".join(record.get("authors") or []),
        "title": title,
        "journal": journal,
        "year": year,
        "volume": record.get("volume"),
        "number": record.get("issue"),
        "pages": record.get("pages"),
        "doi": str(record.get("doi") or "").removeprefix("https://doi.org/"),
    }
    lines = [f"@article{{{key},"]
    lines.extend(f"  {name} = {{{value}}}," for name, value in fields.items() if value)
    lines.append("}")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    search = subparsers.add_parser("search")
    search.add_argument("query")
    search.add_argument("--source", choices=("openalex", "crossref"), default="openalex")
    search.add_argument("--limit", type=int, choices=range(1, 101), default=10)
    search.add_argument("--from-year", type=int, choices=range(1000, 10000))
    search.add_argument("--to-year", type=int, choices=range(1000, 10000))
    search.add_argument("--sort", choices=("relevance", "cited"), default="relevance")
    doi = subparsers.add_parser("doi")
    doi.add_argument("doi")
    doi.add_argument("--source", choices=("openalex", "crossref"), default="crossref")
    cite = subparsers.add_parser("cite")
    cite.add_argument("doi")
    cite.add_argument("--source", choices=("openalex", "crossref"), default="crossref")
    cite.add_argument("--style", choices=("apa", "bibtex", "gbt7714"), default="apa")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.command == "search":
        result = openalex_search(args) if args.source == "openalex" else crossref_search(args)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return
    result = lookup_doi(args.doi, args.source)
    if args.command == "doi":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(citation(result["result"], args.style))


if __name__ == "__main__":
    main()
