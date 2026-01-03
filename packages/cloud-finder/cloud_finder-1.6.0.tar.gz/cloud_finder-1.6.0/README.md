# Cloud Finder

Keyword cloud and topic hotspot detection in documents. Find where keywords concentrate to detect topic relevance.

Built on top of [vibe-finder](https://pypi.org/project/vibe-finder/) with a simplified, focused API.

## Use Cases

- **Topic Detection**: Find paragraphs/regions discussing specific topics
- **Document Relevance**: Score documents by keyword concentration
- **Keyword Clustering**: Analyze where keywords cluster together
- **Content Analysis**: Find the most relevant sections in long documents

## Installation

```bash
pip install cloud-finder
```

## Quick Start

```python
from cloud_finder import find_topics, analyze_relevance

# Find topic regions
topics = find_topics(
    document,
    keywords=["налоговая", "оптимизация", "НДС"],
    min_relevance=0.3
)

for topic in topics:
    print(f"Relevance: {topic.relevance:.0%}")
    print(f"Position: {topic.start}:{topic.end}")
    print(f"Keywords found: {topic.found_keywords}")
    print(f"Clustering: {topic.clustering:.1f}x concentrated")
```

## API

### find_topics()

Find all topic regions in a document:

```python
from cloud_finder import find_topics

topics = find_topics(
    text,
    keywords=["keyword1", "keyword2", "keyword3"],
    min_relevance=0.3,   # Minimum score (0-1)
    min_coverage=0.4,    # At least 40% keywords required
    window_size=400,     # Search window in chars
    fuzzy=True           # Enable fuzzy matching for typos
)
```

### find_best_topic()

Find the single best topic region:

```python
from cloud_finder import find_best_topic

best = find_best_topic(document, ["налоговая", "оптимизация"])
if best:
    print(f"Best match at position {best.position}")
```

### analyze_relevance()

Quick relevance check for a document:

```python
from cloud_finder import analyze_relevance

result = analyze_relevance(document, ["tax", "optimization", "deduction"])

if result["is_relevant"]:
    print(f"Document is relevant: {result['max_relevance']:.0%}")
    print(f"Found {result['topic_count']} topic regions")
```

### TopicFinder (OOP API)

```python
from cloud_finder import TopicFinder

finder = TopicFinder(document, fuzzy_threshold=0.85)

# Variadic keyword syntax
topics = finder.find("налоговая", "оптимизация", "НДС")

# Or find best
best = finder.find_best("tax", "optimization", min_coverage=0.5)
```

## TopicMatch Fields

| Field | Type | Description |
|-------|------|-------------|
| `position` | int | Center position of topic region |
| `start` | int | Start offset |
| `end` | int | End offset |
| `relevance` | float | Overall relevance score (0-1) |
| `keyword_coverage` | float | % of keywords found (0-1) |
| `found_keywords` | List[str] | Keywords that were found |
| `missing_keywords` | List[str] | Keywords not found |
| `clustering` | float | Concentration vs even distribution (>1 = clustered) |
| `density` | float | Keywords per 100 chars |
| `spread` | float | Standard deviation of positions |
| `preview` | str | Text preview of region |

## Properties

```python
topic.is_highly_relevant  # True if relevance >= 0.5 and clustering >= 1.5
topic.interpretation      # "highly_relevant", "relevant", "somewhat_relevant", "weakly_relevant"
```

## Fuzzy Matching

Cloud Finder uses Jaro-Winkler similarity for fuzzy matching, which handles:
- OCR errors (налоговая → налоговоя)
- Typos (оптимизация → оптимизацыя)
- Case differences (НДС → ндс)
- Word form variations (налоговая → налоговой)

## License

MIT
