![Shobdo Banner](https://raw.githubusercontent.com/InanXR/ProjectShobdo/main/assets/banner.png)

<div align="center">

# শব্দ | Shobdo

**A high-performance Bengali dictionary library for Python**

[![PyPI version](https://badge.fury.io/py/shobdo.svg)](https://badge.fury.io/py/shobdo)
[![Python Versions](https://img.shields.io/pypi/pyversions/shobdo.svg)](https://pypi.org/project/shobdo/)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Code Style: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

45,000+ words • SQLite backend • 384D neural embeddings • Pydantic models

</div>

---

<div align="center">
<img src="assets/features.png" alt="Shobdo Features" width="700"/>
</div>

---

## Overview

Shobdo provides fast, type-safe access to a comprehensive Bengali dictionary. The data is pre-compiled into SQLite and indexed, eliminating the startup cost of loading JSON into memory.

| Metric | JSON Loading | Shobdo |
|--------|--------------|--------|
| Startup time | ~1,200ms | ~6ms |
| Memory footprint | ~180MB | <5MB |
| Return type | `dict` | Pydantic `Word` |

---

## Installation

```bash
pip install shobdo
```

For semantic search (optional):
```bash
pip install shobdo numpy sentence-transformers
```

---

## Quick Start

```python
from shobdo import Shobdo

d = Shobdo()
word = d.search("স্বাধীনতা")

print(word.word)                # স্বাধীনতা
print(word.pronunciation)       # শ্বাধীন্‌তা
print(word.meanings)            # ['স্বাধীন হওয়ার ভাব', ...]
print(word.english_translation) # Independence / Freedom
print(word.part_of_speech)      # বিশেষ্য
```

---

## API Reference

### `search(word: str) -> Optional[Word]`

Exact match lookup.

```python
word = d.search("অ")
# Returns Word object or None
```

---

### `search_fuzzy(query: str, max_distance: int = 2) -> List[Word]`

Levenshtein distance-based fuzzy matching. Useful for handling typos.

```python
# User types "অরিন" instead of "অঋণ"
matches = d.search_fuzzy("অরিন", max_distance=2)

for m in matches:
    print(m.word, m.english_translation)
# অঋণ Debt-free
# অরণ্য Forest
```

---

### `search_english(query: str) -> List[Word]`

Search by English translation (substring match).

```python
words = d.search_english("freedom")

for w in words:
    print(w.word, w.english_translation)
# স্বাধীনতা Independence / Freedom
# মুক্তি Freedom / Release
```

---

### `lookup(query: str) -> List[Word]`

Partial match on Bengali headwords.

```python
words = d.lookup("ঋণ")

for w in words[:5]:
    print(w.word)
# ঋণ
# ঋণগ্রস্ত
# ঋণদাতা
# ঋণপত্র
# অঋণ
```

---

### `get_random() -> Word`

Returns a random word from the dictionary.

```python
word = d.get_random()
print(f"{word.word}: {word.meanings[0]}")
```

---

### `stats() -> Dict`

Returns dictionary statistics.

```python
print(d.stats())
# {'total_words': 45630, 'backend': 'sqlite', 'semantic_search': True}
```

---

## Semantic Search

<div align="center">
<img src="assets/semantic_card.png" alt="Semantic Intelligence" width="400"/>
</div>

Shobdo includes pre-computed 384-dimensional embeddings (via `paraphrase-multilingual-MiniLM-L12-v2`) for all words. This enables meaning-based search.

### `search_semantic(query: str, top_k: int = 10) -> List[Tuple[Word, float]]`

Search by concept. The query is encoded at runtime and compared against all word embeddings.

```python
results = d.search_semantic("happiness and joy", top_k=5)

for word, score in results:
    print(f"{word.word}: {word.english_translation} ({score:.2f})")
# হর্ষোদয়: Rise of joy (19.86)
# আনন্দকন্দ: Root of joy (19.43)
# হর্ষাবিষ্ট: Overwhelmed with joy (19.26)
# সুখানুভব: Feeling of happiness (18.77)
# আনন্দ: Joy / Happiness (18.46)
```

Works cross-lingually (English query → Bengali results).

---

### `find_similar(word: str, top_k: int = 10) -> List[Tuple[Word, float]]`

Find synonyms using pre-computed embeddings. No model inference required at runtime.

```python
synonyms = d.find_similar("আনন্দ", top_k=5)

for word, score in synonyms:
    print(f"{word.word}: {word.english_translation}")
# হর্ষোদয়: Rise of joy
# তোষ: Satisfaction / Pleasure
# আনন্দকন্দ: Root of joy
# হরষিত: Delighted / Joyful
# শর্ম: Happiness / Shelter
```

---

## Data Models

```python
from shobdo.models import Word, Etymology
```

### `Word`

| Field | Type | Description |
|-------|------|-------------|
| `word` | `str` | Bengali headword |
| `pronunciation` | `Optional[str]` | Phonetic pronunciation |
| `part_of_speech` | `Optional[str]` | Grammatical category |
| `meanings` | `List[str]` | List of definitions |
| `english_translation` | `Optional[str]` | English equivalent |
| `examples` | `List[str]` | Usage examples |
| `etymology` | `Optional[Etymology]` | Word origin |

### `Etymology`

| Field | Type | Description |
|-------|------|-------------|
| `source_language` | `Optional[str]` | e.g., সংস্কৃত, আরবি |
| `derivation` | `Optional[str]` | Morphological breakdown |

---

## Architecture

<div align="center">
<img src="assets/architecture.png" alt="Architecture" width="700"/>
</div>

**Build-time artifacts:**
- `dictionary.db` (~15MB) — SQLite database with indexed `word` and `english_translation` columns
- `embeddings.npy` (~67MB) — 45,630 × 384 float32 array
- `word_index.json` (~3MB) — Vector index to database ID mapping

**Runtime:**
- SQLite queries for exact/fuzzy/partial/reverse search
- NumPy dot product for semantic similarity

---

## Development

```bash
git clone https://github.com/InanXR/Shobdo-Library
cd Shobdo-Library
pip install -e ".[dev]"

# Run tests
pytest tests/

# Rebuild database
python scripts/build_db.py

# Regenerate embeddings (~10 min)
python scripts/generate_embeddings.py
```

---

## Requirements

- Python 3.9+
- Core: `pydantic`
- Semantic search: `numpy`, `sentence-transformers`

---

## License

Apache License 2.0

---

## Acknowledgments

Data source: [ProjectShobdo](https://github.com/ProjectShobdo)

---

<div align="center">

**[GitHub](https://github.com/InanXR/Shobdo-Library)** · **[Issues](https://github.com/InanXR/Shobdo-Library/issues)** · **[PyPI](https://pypi.org/project/shobdo/)**

</div>