"""
Cloud Finder - Keyword concentration and topic hotspot detection in documents.

A focused wrapper around vibe-finder for finding keyword clouds/hotspots.
Use this when you need to:
- Find where keywords cluster together in text
- Detect topic regions in documents
- Analyze keyword density and distribution
- Score document relevance by keyword concentration

Example:
    from cloud_finder import find_topics, TopicMatch

    # Quick one-liner
    topics = find_topics(
        document,
        keywords=["налоговая", "оптимизация", "НДС"],
        min_relevance=0.3
    )

    for topic in topics:
        print(f"Topic at {topic.position}: relevance={topic.relevance:.0%}")
        print(f"  Keywords: {topic.found_keywords}")
        print(f"  Clustering: {topic.clustering}x concentrated")
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Union
import time

# Import from vibe-finder (the core engine)
from vibe_finder import (
    CloudFinder as _CloudFinder,
    HotspotMatch as _HotspotMatch,
    DistributionStats as _DistributionStats,
    jaro_winkler_similarity,
    tokenize_text,
)

__version__ = "1.2.0"
__all__ = [
    "find_topics",
    "find_topics_batch",
    "find_best_topic",
    "TopicMatch",
    "TopicFinder",
    "BatchResult",
    "analyze_relevance",
    "normalize_query",
]


# Type alias: phrase string OR pre-split keyword list
Query = Union[str, List[str]]


def normalize_query(query: Query, min_length: int = 2) -> List[str]:
    """
    Normalize query to keyword list. Accepts phrase or pre-split keywords.

    Examples:
        normalize_query("Как стать предпринимателем?")
        # -> ["как", "стать", "предпринимателем"]

        normalize_query(["КАК", "СТАТЬ", "предпринимателем"])
        # -> ["как", "стать", "предпринимателем"]
    """
    if isinstance(query, str):
        tokens = tokenize_text(query)
        return [t["word"].lower() for t in tokens if len(t["word"]) >= min_length]
    else:
        return [kw.lower().strip() for kw in query if len(kw.strip()) >= min_length]


def _calculate_concentration(span: int, n_found: int, n_searched: int) -> float:
    """
    Calculate normalized concentration score (0-1).

    Document-size INDEPENDENT - based purely on keyword density within span.

    Formula:
        concentration = 0.6 × density_score + 0.4 × coverage

        where:
            density_per_100 = (n_found / span) × 100
            density_score = 1 - 1/(1 + density_per_100)
            coverage = n_found / n_searched

    Interpretation:
        ≥0.80 = excellent
        ≥0.65 = good
        ≥0.50 = moderate
        ≥0.35 = weak
        <0.35 = poor
    """
    if n_found < 1:
        return 0.0

    if n_found == 1 or span <= 0:
        coverage = n_found / n_searched if n_searched > 0 else 0
        return 0.5 + 0.5 * coverage

    # Density: keywords per 100 chars
    density_per_100 = (n_found / span) * 100

    # Normalize density to 0-1
    density_score = 1 - (1 / (1 + density_per_100))

    # Coverage
    coverage = n_found / n_searched if n_searched > 0 else 1

    # Final score: 60% density, 40% coverage
    return 0.6 * density_score + 0.4 * coverage


@dataclass
class TopicMatch:
    """
    A topic region found in the document.

    Simplified view of keyword concentration with focus on relevance scoring.
    """
    # Core position info
    position: int           # Center position in document
    start: int              # Start offset
    end: int                # End offset

    # Relevance scoring (0-1, higher = more relevant)
    relevance: float        # Overall topic relevance score
    keyword_coverage: float # Percentage of keywords found (0-1)

    # Keywords info
    found_keywords: List[str]   # Keywords that were found
    missing_keywords: List[str] # Keywords not found

    # Distribution analysis (v1.1+)
    concentration: float    # Normalized 0-1 score (document-size independent)
    density: float          # Keywords per 100 chars
    spread: float           # Standard deviation of keyword positions

    # Legacy (kept for backwards compatibility)
    clustering: float       # Raw clustering ratio (document-size dependent, use concentration instead)

    # Text
    preview: str            # Text preview of the region

    def to_dict(self) -> Dict[str, Any]:
        return {
            "position": self.position,
            "start": self.start,
            "end": self.end,
            "relevance": self.relevance,
            "keyword_coverage": self.keyword_coverage,
            "found_keywords": self.found_keywords,
            "missing_keywords": self.missing_keywords,
            "concentration": self.concentration,
            "density": self.density,
            "spread": self.spread,
            "clustering": self.clustering,
            "preview": self.preview,
        }

    @property
    def is_highly_relevant(self) -> bool:
        """True if this is a highly relevant topic region."""
        return self.concentration >= 0.65 and self.keyword_coverage >= 0.5

    @property
    def concentration_label(self) -> str:
        """Human-readable concentration interpretation."""
        if self.concentration >= 0.80:
            return "excellent"
        elif self.concentration >= 0.65:
            return "good"
        elif self.concentration >= 0.50:
            return "moderate"
        elif self.concentration >= 0.35:
            return "weak"
        else:
            return "poor"

    @property
    def interpretation(self) -> str:
        """Human-readable relevance interpretation."""
        if self.relevance >= 0.7:
            return "highly_relevant"
        elif self.relevance >= 0.5:
            return "relevant"
        elif self.relevance >= 0.3:
            return "somewhat_relevant"
        else:
            return "weakly_relevant"


class TopicFinder:
    """
    Find topic regions in documents based on keyword concentration.

    Wrapper around vibe-finder's CloudFinder with simplified API.

    Example:
        finder = TopicFinder(document)
        topics = finder.find("налоговая", "оптимизация", "НДС")

        # Or with options
        topics = finder.find(
            "налоговая", "оптимизация", "НДС",
            min_relevance=0.4,
            fuzzy=True
        )
    """

    def __init__(
        self,
        text: str,
        fuzzy_threshold: float = 0.85,
        window_size: int = 400,
    ):
        """
        Initialize TopicFinder.

        Args:
            text: Document text to analyze
            fuzzy_threshold: Similarity threshold for fuzzy matching (0-1)
            window_size: Default search window size in chars
        """
        self.text = text
        self.fuzzy_threshold = fuzzy_threshold
        self.window_size = window_size
        self._finder = _CloudFinder(text, fuzzy_threshold=fuzzy_threshold)

    def find(
        self,
        *keywords: str,
        min_relevance: float = 0.2,
        min_coverage: float = 0.3,
        max_results: int = 10,
        window_size: Optional[int] = None,
    ) -> List[TopicMatch]:
        """
        Find topic regions containing the given keywords.

        Args:
            *keywords: Keywords to search for (variadic)
            min_relevance: Minimum relevance score (0-1)
            min_coverage: Minimum keyword coverage (0-1)
            max_results: Maximum topics to return
            window_size: Search window size (uses default if None)

        Returns:
            List of TopicMatch sorted by relevance (highest first)

        Example:
            topics = finder.find("налоговая", "оптимизация", "НДС")
            topics = finder.find("tax", "optimization", min_relevance=0.5)
        """
        kw_list = list(keywords)
        if not kw_list:
            return []

        hotspots = self._finder.find_hotspots(
            keywords=kw_list,
            min_score=min_relevance,
            min_coverage=min_coverage,
            window_size=window_size or self.window_size,
            max_results=max_results,
        )

        return [self._convert_hotspot(h, len(kw_list)) for h in hotspots]

    def find_best(
        self,
        *keywords: str,
        min_coverage: float = 0.3,
    ) -> Optional[TopicMatch]:
        """
        Find the single best topic region for given keywords.

        Args:
            *keywords: Keywords to search for
            min_coverage: Minimum keyword coverage

        Returns:
            Best TopicMatch or None if not found
        """
        topics = self.find(
            *keywords,
            min_relevance=0.0,
            min_coverage=min_coverage,
            max_results=1,
        )
        return topics[0] if topics else None

    def _convert_hotspot(self, h: _HotspotMatch, n_searched: int) -> TopicMatch:
        """Convert internal HotspotMatch to TopicMatch."""
        span = h.end_offset - h.start_offset
        n_found = len(h.keywords_found)

        # Calculate normalized concentration (document-size independent)
        concentration = _calculate_concentration(span, n_found, n_searched)

        return TopicMatch(
            position=h.center_offset,
            start=h.start_offset,
            end=h.end_offset,
            relevance=h.score,
            keyword_coverage=h.coverage,
            found_keywords=h.keywords_found,
            missing_keywords=h.keywords_missing,
            concentration=round(concentration, 3),
            density=h.distribution.density,
            spread=h.distribution.std_deviation,
            clustering=h.distribution.clustering_ratio,
            preview=h.text_preview,
        )

    def find_batch(
        self,
        queries: List[Query],
        *,
        min_relevance: float = 0.2,
        min_coverage: float = 0.3,
        max_results: int = 10,
        window_size: Optional[int] = None,
        **kwargs,
    ) -> List[List[TopicMatch]]:
        """
        Find topics for multiple queries at once (reuses text index).

        Args:
            queries: List of queries (phrase strings or keyword lists)
            min_relevance: Minimum relevance score
            min_coverage: Minimum keyword coverage
            max_results: Max results per query
            window_size: Search window size
            **kwargs: Reserved for future parameters

        Returns:
            List of results, one per query (same order as input)

        Example:
            results = finder.find_batch([
                "куда двигаться бизнесу",
                ["налоговая", "оптимизация"],
                "технологии 2024",
            ])
            # results[0] = topics for first query
            # results[1] = topics for second query
            # etc.
        """
        results = []
        ws = window_size or self.window_size

        for query in queries:
            keywords = normalize_query(query)
            if not keywords:
                results.append([])
                continue

            hotspots = self._finder.find_hotspots(
                keywords=keywords,
                min_score=min_relevance,
                min_coverage=min_coverage,
                window_size=ws,
                max_results=max_results,
            )
            results.append([self._convert_hotspot(h, len(keywords)) for h in hotspots])

        return results


@dataclass
class BatchResult:
    """Result from batch topic search with timing info."""
    results: List[List[TopicMatch]]  # Results per query (same order as input)
    queries: List[List[str]]         # Normalized keywords per query
    elapsed_ms: float                # Total processing time in ms
    text_len: int                    # Document length

    def __len__(self) -> int:
        return len(self.results)

    def __getitem__(self, idx: int) -> List[TopicMatch]:
        return self.results[idx]

    def __iter__(self):
        return iter(self.results)


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def find_topics(
    text: str,
    keywords: Query,
    *,
    min_relevance: float = 0.2,
    min_coverage: float = 0.3,
    window_size: int = 400,
    fuzzy: bool = True,
    **kwargs,
) -> List[TopicMatch]:
    """
    Find topic regions in text where keywords concentrate.

    Args:
        text: Document text
        keywords: Phrase string OR list of keywords
        min_relevance: Minimum relevance score (0-1)
        min_coverage: Minimum keyword coverage (0-1)
        window_size: Search window size in chars
        fuzzy: Enable fuzzy matching for typos/OCR errors
        **kwargs: Reserved for future parameters

    Returns:
        List of TopicMatch sorted by relevance

    Example:
        # Both work the same:
        find_topics(doc, "куда двигаться бизнесу")
        find_topics(doc, ["куда", "двигаться", "бизнесу"])
    """
    kw_list = normalize_query(keywords)
    if not kw_list:
        return []

    threshold = 0.85 if fuzzy else 0.99
    finder = TopicFinder(text, fuzzy_threshold=threshold, window_size=window_size)
    return finder.find(*kw_list, min_relevance=min_relevance, min_coverage=min_coverage)


def find_topics_batch(
    text: str,
    queries: List[Query],
    *,
    min_relevance: float = 0.2,
    min_coverage: float = 0.3,
    max_results: int = 10,
    window_size: int = 400,
    fuzzy: bool = True,
    **kwargs,
) -> BatchResult:
    """
    Find topics for multiple queries at once (saves text preparation time).

    Args:
        text: Document text
        queries: List of queries (phrase strings or keyword lists)
        min_relevance: Minimum relevance score
        min_coverage: Minimum keyword coverage
        max_results: Max results per query
        window_size: Search window size
        fuzzy: Enable fuzzy matching
        **kwargs: Reserved for future parameters

    Returns:
        BatchResult with results per query (same order as input)

    Example:
        batch = find_topics_batch(document, [
            "куда двигаться бизнесу",           # phrase
            ["налоговая", "оптимизация", "НДС"], # pre-split
            "технологии развитие 2024",          # phrase
        ])

        for i, topics in enumerate(batch):
            print(f"Query {i}: {len(topics)} topics found")

        # Access by index
        first_query_topics = batch[0]
    """
    threshold = 0.85 if fuzzy else 0.99

    # Normalize all queries upfront
    normalized = [normalize_query(q) for q in queries]

    start = time.perf_counter()
    finder = TopicFinder(text, fuzzy_threshold=threshold, window_size=window_size)
    results = finder.find_batch(
        queries,
        min_relevance=min_relevance,
        min_coverage=min_coverage,
        max_results=max_results,
        window_size=window_size,
    )
    elapsed = (time.perf_counter() - start) * 1000

    return BatchResult(
        results=results,
        queries=normalized,
        elapsed_ms=round(elapsed, 2),
        text_len=len(text),
    )


def find_best_topic(
    text: str,
    keywords: Query,
    *,
    min_coverage: float = 0.3,
    fuzzy: bool = True,
    **kwargs,
) -> Optional[TopicMatch]:
    """
    Find the single best topic region for given keywords.

    Args:
        text: Document text
        keywords: Phrase string OR list of keywords
        min_coverage: Minimum keyword coverage
        fuzzy: Enable fuzzy matching
        **kwargs: Reserved for future parameters

    Returns:
        Best TopicMatch or None
    """
    topics = find_topics(
        text, keywords,
        min_relevance=0.0,
        min_coverage=min_coverage,
        fuzzy=fuzzy,
    )
    return topics[0] if topics else None


def analyze_relevance(
    text: str,
    keywords: Query,
    *,
    fuzzy: bool = True,
    **kwargs,
) -> Dict[str, Any]:
    """
    Analyze document relevance to a set of keywords.

    Args:
        text: Document text
        keywords: Phrase string OR list of keywords
        fuzzy: Enable fuzzy matching
        **kwargs: Reserved for future parameters

    Returns:
        Dict with relevance analysis:
        - is_relevant: bool
        - max_relevance: float (best topic score)
        - topic_count: int (number of topic regions)
        - best_coverage: float (best keyword coverage)
        - best_topic: TopicMatch or None

    Example:
        # Both work:
        analyze_relevance(doc, "налоговая оптимизация")
        analyze_relevance(doc, ["налоговая", "оптимизация"])
    """
    topics = find_topics(text, keywords, min_relevance=0.1, fuzzy=fuzzy)

    if not topics:
        return {
            "is_relevant": False,
            "max_relevance": 0.0,
            "topic_count": 0,
            "best_coverage": 0.0,
            "best_topic": None,
        }

    best = topics[0]
    return {
        "is_relevant": best.relevance >= 0.3,
        "max_relevance": best.relevance,
        "topic_count": len(topics),
        "best_coverage": best.keyword_coverage,
        "best_topic": best,
    }
