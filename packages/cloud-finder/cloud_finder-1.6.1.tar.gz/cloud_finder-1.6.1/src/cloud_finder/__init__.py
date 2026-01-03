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
    # Presets
    MatchPreset,
    PRESETS,
    get_preset,
    # Token map (v1.5+)
    TokenMatch,
    KeywordMapResult,
    find_keyword_map,
)

__version__ = "1.6.1"
__all__ = [
    "find_topics",
    "find_topics_batch",
    "find_best_topic",
    "TopicMatch",
    "TopicFinder",
    "BatchResult",
    "analyze_relevance",
    "normalize_query",
    # Word-level presets (re-exported from vibe-finder)
    "PRESETS",
    "get_preset",
    # Cloud-level presets (v1.5+)
    "CloudPreset",
    "CLOUD_PRESETS",
    "get_cloud_preset",
    # Dynamic help (v1.5+)
    "list_cloud_presets",
    "list_word_presets",
    # Token map (v1.6+ - re-exported from vibe-finder)
    "TokenMatch",
    "KeywordMapResult",
    "find_keyword_map",
]


# Type alias: phrase string OR pre-split keyword list
Query = Union[str, List[str]]


# =============================================================================
# CLOUD-LEVEL PRESETS (v1.5+)
# =============================================================================

@dataclass
class CloudPreset:
    """
    Cloud-level preset configuration.

    Combines word-matching settings (from vibe-finder) with cloud-level
    parameters that control how matched words should cluster together.

    Two-layer matching:
    1. Word-level: How strictly to match individual words (via word_preset)
    2. Cloud-level: How keywords should cluster/distribute in text
    """
    name: str
    description: str

    # Word-level: which vibe-finder preset to use
    word_preset: str  # "exact", "strict", "ocr", "morphological", "relaxed"

    # Cloud-level parameters
    window_size: int = 400          # Search window in chars
    min_density: float = 0.5        # Min keywords per 100 chars (0 = no filter)
    max_spread_ratio: float = 1.0   # Max spread as ratio of window (0-1, 1 = window-wide allowed)
    sequence_bonus: float = 0.0     # Bonus for words in correct order (0-1)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "word_preset": self.word_preset,
            "window_size": self.window_size,
            "min_density": self.min_density,
            "max_spread_ratio": self.max_spread_ratio,
            "sequence_bonus": self.sequence_bonus,
        }


# Predefined cloud presets for common use cases
CLOUD_PRESETS: Dict[str, CloudPreset] = {
    "exact_phrase": CloudPreset(
        name="exact_phrase",
        description="Exact phrase matching. Words must be close together in order.",
        word_preset="strict",
        window_size=200,
        min_density=2.0,        # High density required
        max_spread_ratio=0.3,   # Tight cluster (30% of window max)
        sequence_bonus=0.3,     # Bonus for correct order
    ),
    "topic_search": CloudPreset(
        name="topic_search",
        description="Default topic detection. OCR-tolerant, moderate clustering.",
        word_preset="ocr",
        window_size=400,
        min_density=0.5,        # Moderate density
        max_spread_ratio=0.8,   # Allow wider spread
        sequence_bonus=0.0,     # Order doesn't matter
    ),
    "scattered": CloudPreset(
        name="scattered",
        description="Find scattered keywords. High recall, accepts wide distribution.",
        word_preset="relaxed",
        window_size=600,
        min_density=0.3,        # Low density OK
        max_spread_ratio=1.0,   # Full window spread allowed
        sequence_bonus=0.0,     # Order irrelevant
    ),
    "morphological_topic": CloudPreset(
        name="morphological_topic",
        description="For Russian/Polish morphology. Word forms with moderate clustering.",
        word_preset="morphological",
        window_size=400,
        min_density=0.5,
        max_spread_ratio=0.7,
        sequence_bonus=0.1,     # Slight order preference
    ),
}


def get_cloud_preset(
    name: str = "topic_search",
    *,
    word_preset: Optional[str] = None,
    window_size: Optional[int] = None,
    min_density: Optional[float] = None,
    max_spread_ratio: Optional[float] = None,
    sequence_bonus: Optional[float] = None,
) -> CloudPreset:
    """
    Get a cloud preset with optional parameter overrides.

    Args:
        name: Preset name ("exact_phrase", "topic_search", "scattered", "morphological_topic")
        word_preset: Override the vibe-finder preset for word matching
        window_size: Override window size
        min_density: Override minimum density filter
        max_spread_ratio: Override max spread ratio
        sequence_bonus: Override sequence bonus

    Returns:
        CloudPreset with applied overrides

    Examples:
        # Use preset as-is
        preset = get_cloud_preset("exact_phrase")

        # Override window size
        preset = get_cloud_preset("topic_search", window_size=600)

        # Change word matching to be stricter
        preset = get_cloud_preset("scattered", word_preset="strict")
    """
    if name not in CLOUD_PRESETS:
        available = ", ".join(sorted(CLOUD_PRESETS.keys()))
        raise ValueError(f"Unknown cloud preset '{name}'. Available: {available}")

    base = CLOUD_PRESETS[name]

    return CloudPreset(
        name=base.name if not any([word_preset, window_size, min_density, max_spread_ratio, sequence_bonus]) else f"{base.name}*",
        description=base.description,
        word_preset=word_preset or base.word_preset,
        window_size=window_size if window_size is not None else base.window_size,
        min_density=min_density if min_density is not None else base.min_density,
        max_spread_ratio=max_spread_ratio if max_spread_ratio is not None else base.max_spread_ratio,
        sequence_bonus=sequence_bonus if sequence_bonus is not None else base.sequence_bonus,
    )


def list_cloud_presets() -> str:
    """
    Get formatted help text for all cloud presets.

    Returns dynamically generated text from CLOUD_PRESETS dict.
    When a new preset is added, this help updates automatically.

    Example:
        print(list_cloud_presets())
    """
    lines = ["Cloud Presets (use cloud_preset='name'):", ""]
    for name, p in CLOUD_PRESETS.items():
        lines.append(f"  {name}")
        lines.append(f"    {p.description}")
        lines.append(f"    word_preset={p.word_preset}, window={p.window_size}, "
                    f"density>={p.min_density}, spread<={p.max_spread_ratio:.0%}, "
                    f"seq_bonus={p.sequence_bonus}")
        lines.append("")
    return "\n".join(lines)


def list_word_presets() -> str:
    """
    Get formatted help text for all word-level presets.

    Returns dynamically generated text from PRESETS dict (from vibe-finder).
    When a new preset is added, this help updates automatically.

    Example:
        print(list_word_presets())
    """
    lines = ["Word Presets (use preset='name'):", ""]
    for name, p in PRESETS.items():
        lines.append(f"  {name}")
        lines.append(f"    {p.description}")
        lines.append(f"    jw_threshold={p.fuzzy_threshold}, max_edit={p.max_edit_ratio:.0%}")
        lines.append("")
    return "\n".join(lines)


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

        # With word-level preset (v1.4 style)
        finder = TopicFinder(document, preset="ocr")

        # With cloud-level preset (v1.5+) - combines word + cloud settings
        finder = TopicFinder(document, cloud_preset="exact_phrase")

        # Override any parameter
        finder = TopicFinder(document, cloud_preset="topic_search", window_size=600)
    """

    def __init__(
        self,
        text: str,
        preset: Optional[str] = None,
        cloud_preset: Optional[str] = None,
        fuzzy_threshold: Optional[float] = None,
        max_edit_ratio: Optional[float] = None,
        window_size: Optional[int] = None,
        min_density: Optional[float] = None,
        max_spread_ratio: Optional[float] = None,
        sequence_bonus: Optional[float] = None,
    ):
        """
        Initialize TopicFinder.

        Args:
            text: Document text to analyze
            preset: Word-level preset ("exact", "strict", "ocr", "morphological", "relaxed")
            cloud_preset: Cloud-level preset ("exact_phrase", "topic_search", "scattered", "morphological_topic")
            fuzzy_threshold: Override Jaro-Winkler threshold
            max_edit_ratio: Override max edit ratio
            window_size: Override search window size in chars
            min_density: Override min keywords per 100 chars (0 = no filter)
            max_spread_ratio: Override max spread as ratio of window (0-1)
            sequence_bonus: Override bonus for words in correct order (0-1)

        Cloud Presets (v1.5+):
            - "exact_phrase": Tight clustering, words in order, strict matching
            - "topic_search": Default - OCR tolerant, moderate clustering
            - "scattered": Wide spread allowed, relaxed matching
            - "morphological_topic": For Russian/Polish word forms

        Word Presets (v1.4 compatible):
            - "exact": Almost exact (jw=0.98, edit=5%)
            - "strict": Default (jw=0.86, edit=15%)
            - "ocr": OCR tolerant (jw=0.84, edit=20%)
            - "morphological": Word forms (jw=0.80, edit=25%)
            - "relaxed": Permissive (jw=0.75, edit=30%)
        """
        self.text = text

        # Resolve cloud preset first (if provided)
        if cloud_preset:
            cp = get_cloud_preset(
                cloud_preset,
                word_preset=preset,
                window_size=window_size,
                min_density=min_density,
                max_spread_ratio=max_spread_ratio,
                sequence_bonus=sequence_bonus,
            )
            word_preset_name = cp.word_preset
            self.window_size = cp.window_size
            self.min_density = cp.min_density
            self.max_spread_ratio = cp.max_spread_ratio
            self.sequence_bonus = cp.sequence_bonus
            self.cloud_preset_name = cp.name
        else:
            word_preset_name = preset or "strict"
            self.window_size = window_size if window_size is not None else 400
            self.min_density = min_density if min_density is not None else 0.0
            self.max_spread_ratio = max_spread_ratio if max_spread_ratio is not None else 1.0
            self.sequence_bonus = sequence_bonus if sequence_bonus is not None else 0.0
            self.cloud_preset_name = None

        # Resolve word-level preset
        p = get_preset(word_preset_name, fuzzy_threshold=fuzzy_threshold, max_edit_ratio=max_edit_ratio)
        self.fuzzy_threshold = p.fuzzy_threshold
        self.max_edit_ratio = p.max_edit_ratio
        self.preset_name = p.name

        # Cap window_size at document length to avoid empty sliding window
        if len(text) < self.window_size:
            self.window_size = max(len(text), 50)  # Minimum 50 chars

        self._finder = _CloudFinder(text, preset=word_preset_name, fuzzy_threshold=fuzzy_threshold, max_edit_ratio=max_edit_ratio)

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

        ws = window_size or self.window_size
        # Cap at text length to avoid empty sliding window
        ws = min(ws, len(self.text)) if len(self.text) > 50 else max(len(self.text), 50)

        hotspots = self._finder.find_hotspots(
            keywords=kw_list,
            min_score=0.0,  # Get all, filter after applying cloud params
            min_coverage=min_coverage,
            window_size=ws,
            max_results=max_results * 3,  # Get more, filter down
        )

        # Convert and apply cloud-level filtering
        topics = []
        for h in hotspots:
            topic = self._convert_hotspot(h, kw_list, ws)
            if topic is None:
                continue  # Filtered by cloud params

            # Apply relevance threshold after sequence bonus
            if topic.relevance >= min_relevance:
                topics.append(topic)

        # Sort by relevance (highest first) and limit
        topics.sort(key=lambda t: t.relevance, reverse=True)
        return topics[:max_results]

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

    def _convert_hotspot(
        self,
        h: _HotspotMatch,
        keywords: List[str],
        window_size: int,
    ) -> Optional[TopicMatch]:
        """
        Convert internal HotspotMatch to TopicMatch with cloud-level filtering.

        Returns None if the hotspot doesn't pass cloud-level filters.
        """
        span = h.end_offset - h.start_offset
        n_found = len(h.keywords_found)
        n_searched = len(keywords)

        # Cloud-level filter 1: min_density
        density = h.distribution.density
        if self.min_density > 0 and density < self.min_density:
            return None

        # Cloud-level filter 2: max_spread_ratio
        spread = h.distribution.std_deviation
        max_allowed_spread = window_size * self.max_spread_ratio
        if spread > max_allowed_spread:
            return None

        # Calculate normalized concentration (document-size independent)
        concentration = _calculate_concentration(span, n_found, n_searched)

        # Calculate base relevance score
        relevance = h.score

        # Apply sequence bonus if keywords appear in order
        if self.sequence_bonus > 0 and n_found >= 2:
            sequence_ratio = self._calculate_sequence_ratio(h, keywords)
            relevance = min(1.0, relevance + self.sequence_bonus * sequence_ratio)

        return TopicMatch(
            position=h.center_offset,
            start=h.start_offset,
            end=h.end_offset,
            relevance=round(relevance, 3),
            keyword_coverage=h.coverage,
            found_keywords=h.keywords_found,
            missing_keywords=h.keywords_missing,
            concentration=round(concentration, 3),
            density=density,
            spread=spread,
            clustering=h.distribution.clustering_ratio,
            preview=h.text_preview,
        )

    def _calculate_sequence_ratio(self, h: _HotspotMatch, keywords: List[str]) -> float:
        """
        Calculate how well found keywords match the expected order.

        Returns 0-1 where 1 means perfect order match.
        """
        found = h.keywords_found
        if len(found) < 2:
            return 0.0

        # Build expected order from original keywords
        kw_lower = [k.lower() for k in keywords]
        found_lower = [f.lower() for f in found]

        # Get positions of found keywords in original order
        positions = []
        for f in found_lower:
            try:
                idx = kw_lower.index(f)
                positions.append(idx)
            except ValueError:
                # Fuzzy match - find closest
                for i, k in enumerate(kw_lower):
                    if jaro_winkler_similarity(f, k) >= self.fuzzy_threshold:
                        positions.append(i)
                        break

        if len(positions) < 2:
            return 0.0

        # Count pairs in correct order
        correct_pairs = 0
        total_pairs = 0
        for i in range(len(positions)):
            for j in range(i + 1, len(positions)):
                total_pairs += 1
                if positions[i] < positions[j]:
                    correct_pairs += 1

        return correct_pairs / total_pairs if total_pairs > 0 else 0.0

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
                min_score=0.0,  # Get all, filter after cloud params
                min_coverage=min_coverage,
                window_size=ws,
                max_results=max_results * 3,
            )

            # Convert and apply cloud-level filtering
            topics = []
            for h in hotspots:
                topic = self._convert_hotspot(h, keywords, ws)
                if topic is not None and topic.relevance >= min_relevance:
                    topics.append(topic)

            # Sort and limit
            topics.sort(key=lambda t: t.relevance, reverse=True)
            results.append(topics[:max_results])

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
    preset: Optional[str] = None,
    cloud_preset: Optional[str] = None,
    min_relevance: float = 0.2,
    min_coverage: float = 0.3,
    window_size: Optional[int] = None,
    fuzzy_threshold: Optional[float] = None,
    max_edit_ratio: Optional[float] = None,
    min_density: Optional[float] = None,
    max_spread_ratio: Optional[float] = None,
    sequence_bonus: Optional[float] = None,
    **kwargs,
) -> List[TopicMatch]:
    """
    Find topic regions in text where keywords concentrate.

    Args:
        text: Document text
        keywords: Phrase string OR list of keywords
        preset: Word-level preset ("exact", "strict", "ocr", "morphological", "relaxed")
        cloud_preset: Cloud-level preset ("exact_phrase", "topic_search", "scattered", "morphological_topic")
        min_relevance: Minimum relevance score (0-1)
        min_coverage: Minimum keyword coverage (0-1)
        window_size: Search window size in chars
        fuzzy_threshold: Override Jaro-Winkler threshold
        max_edit_ratio: Override max edit ratio
        min_density: Override min keywords per 100 chars
        max_spread_ratio: Override max spread ratio (0-1)
        sequence_bonus: Override sequence bonus (0-1)
        **kwargs: Reserved for future parameters

    Returns:
        List of TopicMatch sorted by relevance

    Example:
        # Simple usage
        find_topics(doc, "куда двигаться бизнесу")

        # With cloud preset (v1.5+)
        find_topics(doc, keywords, cloud_preset="exact_phrase")

        # With word preset (v1.4 style)
        find_topics(doc, keywords, preset="ocr")

        # With custom parameters
        find_topics(doc, keywords, fuzzy_threshold=0.90, min_density=1.0)
    """
    kw_list = normalize_query(keywords)
    if not kw_list:
        return []

    finder = TopicFinder(
        text,
        preset=preset,
        cloud_preset=cloud_preset,
        fuzzy_threshold=fuzzy_threshold,
        max_edit_ratio=max_edit_ratio,
        window_size=window_size,
        min_density=min_density,
        max_spread_ratio=max_spread_ratio,
        sequence_bonus=sequence_bonus,
    )
    return finder.find(*kw_list, min_relevance=min_relevance, min_coverage=min_coverage)


def find_topics_batch(
    text: str,
    queries: List[Query],
    *,
    preset: Optional[str] = None,
    cloud_preset: Optional[str] = None,
    min_relevance: float = 0.2,
    min_coverage: float = 0.3,
    max_results: int = 10,
    window_size: Optional[int] = None,
    fuzzy_threshold: Optional[float] = None,
    max_edit_ratio: Optional[float] = None,
    min_density: Optional[float] = None,
    max_spread_ratio: Optional[float] = None,
    sequence_bonus: Optional[float] = None,
    **kwargs,
) -> BatchResult:
    """
    Find topics for multiple queries at once (saves text preparation time).

    Args:
        text: Document text
        queries: List of queries (phrase strings or keyword lists)
        preset: Word-level preset ("exact", "strict", "ocr", "morphological", "relaxed")
        cloud_preset: Cloud-level preset ("exact_phrase", "topic_search", "scattered", "morphological_topic")
        min_relevance: Minimum relevance score
        min_coverage: Minimum keyword coverage
        max_results: Max results per query
        window_size: Search window size
        fuzzy_threshold: Override Jaro-Winkler threshold
        max_edit_ratio: Override max edit ratio
        min_density: Override min keywords per 100 chars
        max_spread_ratio: Override max spread ratio (0-1)
        sequence_bonus: Override sequence bonus (0-1)
        **kwargs: Reserved for future parameters

    Returns:
        BatchResult with results per query (same order as input)

    Example:
        # With cloud preset (v1.5+)
        batch = find_topics_batch(doc, queries, cloud_preset="exact_phrase")

        # With word preset (v1.4 style)
        batch = find_topics_batch(doc, queries, preset="ocr")

        # With custom parameters
        batch = find_topics_batch(doc, queries, fuzzy_threshold=0.90)
    """
    # Normalize all queries upfront
    normalized = [normalize_query(q) for q in queries]

    start = time.perf_counter()
    finder = TopicFinder(
        text,
        preset=preset,
        cloud_preset=cloud_preset,
        fuzzy_threshold=fuzzy_threshold,
        max_edit_ratio=max_edit_ratio,
        window_size=window_size,
        min_density=min_density,
        max_spread_ratio=max_spread_ratio,
        sequence_bonus=sequence_bonus,
    )
    results = finder.find_batch(
        queries,
        min_relevance=min_relevance,
        min_coverage=min_coverage,
        max_results=max_results,
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
    preset: Optional[str] = None,
    cloud_preset: Optional[str] = None,
    min_coverage: float = 0.3,
    fuzzy_threshold: Optional[float] = None,
    max_edit_ratio: Optional[float] = None,
    min_density: Optional[float] = None,
    max_spread_ratio: Optional[float] = None,
    sequence_bonus: Optional[float] = None,
    **kwargs,
) -> Optional[TopicMatch]:
    """
    Find the single best topic region for given keywords.

    Args:
        text: Document text
        keywords: Phrase string OR list of keywords
        preset: Word-level preset ("exact", "strict", "ocr", "morphological", "relaxed")
        cloud_preset: Cloud-level preset ("exact_phrase", "topic_search", "scattered", "morphological_topic")
        min_coverage: Minimum keyword coverage
        fuzzy_threshold: Override Jaro-Winkler threshold
        max_edit_ratio: Override max edit ratio
        min_density: Override min keywords per 100 chars
        max_spread_ratio: Override max spread ratio (0-1)
        sequence_bonus: Override sequence bonus (0-1)
        **kwargs: Reserved for future parameters

    Returns:
        Best TopicMatch or None
    """
    topics = find_topics(
        text, keywords,
        preset=preset,
        cloud_preset=cloud_preset,
        min_relevance=0.0,
        min_coverage=min_coverage,
        fuzzy_threshold=fuzzy_threshold,
        max_edit_ratio=max_edit_ratio,
        min_density=min_density,
        max_spread_ratio=max_spread_ratio,
        sequence_bonus=sequence_bonus,
    )
    return topics[0] if topics else None


def analyze_relevance(
    text: str,
    keywords: Query,
    *,
    preset: Optional[str] = None,
    cloud_preset: Optional[str] = None,
    fuzzy_threshold: Optional[float] = None,
    max_edit_ratio: Optional[float] = None,
    min_density: Optional[float] = None,
    max_spread_ratio: Optional[float] = None,
    sequence_bonus: Optional[float] = None,
    **kwargs,
) -> Dict[str, Any]:
    """
    Analyze document relevance to a set of keywords.

    Args:
        text: Document text
        keywords: Phrase string OR list of keywords
        preset: Word-level preset ("exact", "strict", "ocr", "morphological", "relaxed")
        cloud_preset: Cloud-level preset ("exact_phrase", "topic_search", "scattered", "morphological_topic")
        fuzzy_threshold: Override Jaro-Winkler threshold
        max_edit_ratio: Override max edit ratio
        min_density: Override min keywords per 100 chars
        max_spread_ratio: Override max spread ratio (0-1)
        sequence_bonus: Override sequence bonus (0-1)
        **kwargs: Reserved for future parameters

    Returns:
        Dict with relevance analysis

    Example:
        # With cloud preset (v1.5+)
        analyze_relevance(doc, "налоговая оптимизация", cloud_preset="exact_phrase")

        # With word preset (v1.4 style)
        analyze_relevance(doc, "налоговая оптимизация", preset="ocr")
    """
    topics = find_topics(
        text, keywords,
        preset=preset,
        cloud_preset=cloud_preset,
        min_relevance=0.1,
        fuzzy_threshold=fuzzy_threshold,
        max_edit_ratio=max_edit_ratio,
        min_density=min_density,
        max_spread_ratio=max_spread_ratio,
        sequence_bonus=sequence_bonus,
    )

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
