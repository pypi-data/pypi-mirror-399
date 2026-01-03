"""
Kit Search Tool

Search kits by keywords with relevance scoring.
"""

import re
from dataclasses import dataclass, field
from typing import Optional

from ..storage.local import LocalKitStorage


# Search weights for different fields
WEIGHTS = {
    "problems_solved": 3.0,
    "when_to_use": 2.5,
    "tags": 2.0,
    "summary": 1.5,
    "name": 1.0,
}

# Common stop words to ignore
STOP_WORDS = {"how", "to", "a", "the", "for", "with", "and", "or", "in", "is", "it", "my", "i", "want", "need"}


@dataclass
class SearchResult:
    """Search result for a kit."""
    kit_id: str
    name: str
    group: str
    summary: str
    score: float
    matched_on: list[str] = field(default_factory=list)


def extract_terms(query: str) -> list[str]:
    """Extract search terms from query."""
    words = re.findall(r"\w+", query.lower())
    return [w for w in words if w not in STOP_WORDS and len(w) > 2]


def calculate_score(kit: dict, terms: list[str]) -> tuple[float, list[str]]:
    """
    Calculate relevance score for a kit.

    Args:
        kit: Kit dictionary
        terms: Search terms

    Returns:
        Tuple of (score, matched_fields)
    """
    score = 0.0
    matched = []

    for term in terms:
        # Check problems_solved
        for p in kit.get("problems_solved", []):
            if term in p.lower():
                score += WEIGHTS["problems_solved"]
                if "problems_solved" not in matched:
                    matched.append("problems_solved")

        # Check when_to_use
        for w in kit.get("when_to_use", []):
            if term in w.lower():
                score += WEIGHTS["when_to_use"]
                if "when_to_use" not in matched:
                    matched.append("when_to_use")

        # Check tags
        if term in [t.lower() for t in kit.get("tags", [])]:
            score += WEIGHTS["tags"]
            if "tags" not in matched:
                matched.append("tags")

        # Check summary
        if term in kit.get("summary", "").lower():
            score += WEIGHTS["summary"]
            if "summary" not in matched:
                matched.append("summary")

        # Check name
        if term in kit.get("name", "").lower():
            score += WEIGHTS["name"]
            if "name" not in matched:
                matched.append("name")

        # Check id
        if term in kit.get("id", "").lower():
            score += WEIGHTS["name"]
            if "id" not in matched:
                matched.append("id")

    return score, matched


def search_kits(
    store: LocalKitStorage,
    query: str,
    group: Optional[str] = None,
    limit: int = 5,
) -> list[SearchResult]:
    """
    Search for kits matching the query.

    Args:
        store: Kit storage backend
        query: Search query string
        group: Optional group filter
        limit: Maximum results to return

    Returns:
        List of SearchResult sorted by relevance
    """
    terms = extract_terms(query)

    if not terms:
        return []

    results = []

    for kit in store.list_kits(group=group):
        score, matched = calculate_score(kit, terms)

        if score > 0:
            results.append(SearchResult(
                kit_id=kit.get("id", ""),
                name=kit.get("name", ""),
                group=kit.get("group", ""),
                summary=kit.get("summary", ""),
                score=score,
                matched_on=matched,
            ))

    # Sort by score descending
    results.sort(key=lambda x: x.score, reverse=True)

    return results[:limit]
