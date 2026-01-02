import sqlite3
import json
import random
from typing import List, Dict, Optional, Any, Tuple
from pathlib import Path
from .utils import get_data_path
from .models import Word, Etymology

# Optional imports for semantic search
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

def levenstein_dist(s1: str, s2: str) -> int:
    """
    Calculates the Levenshtein distance between two strings.
    Optimized for short strings (like words).
    """
    if len(s1) < len(s2):
        return levenstein_dist(s2, s1)
    if len(s2) == 0:
        return len(s1)
    
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]

class Shobdo:
    """
    Main class for interacting with the Shobdo Bengali Dictionary (SQLite Backend).
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize the Shobdo dictionary.
        
        Args:
            db_path: Optional path to dictionary.db. If None, uses packaged data.
        """
        if db_path:
            self.db_path = Path(db_path)
        else:
            self.db_path = get_data_path("dictionary.db")
            
        self._conn = None
        
        # Lazy-loaded semantic search data
        self._embeddings = None
        self._word_index = None
        self._encoder = None

    def _get_conn(self) -> sqlite3.Connection:
        """Get or create a thread-local database connection."""
        if self._conn is None:
            # check_same_thread=False allows sharing connection across threads for read-only
            self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self._conn.row_factory = sqlite3.Row
            # Register specific functions for fuzzy search
            self._conn.create_function("levenshtein", 2, levenstein_dist)
        return self._conn

    def _load_embeddings(self):
        """Lazy load embeddings and word index for semantic search."""
        if self._embeddings is not None:
            return
        
        if not HAS_NUMPY:
            raise ImportError("numpy is required for semantic search. Install with: pip install numpy")
        
        embeddings_path = get_data_path("embeddings.npy")
        word_index_path = get_data_path("word_index.json")
        
        if not embeddings_path.exists():
            raise FileNotFoundError(f"Embeddings not found at {embeddings_path}. Run scripts/generate_embeddings.py first.")
        
        self._embeddings = np.load(embeddings_path)
        with open(word_index_path, "r", encoding="utf-8") as f:
            self._word_index = json.load(f)

    def _get_encoder(self):
        """Lazy load the sentence transformer encoder."""
        if self._encoder is not None:
            return self._encoder
        
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            raise ImportError("sentence-transformers is required for semantic search. Install with: pip install sentence-transformers")
        
        # Try local model first, then fallback to HuggingFace
        local_model_path = Path("paraphrase-multilingual-MiniLM-L12-v2")
        if local_model_path.exists():
            self._encoder = SentenceTransformer(str(local_model_path))
        else:
            self._encoder = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
        
        return self._encoder

    def _row_to_word(self, row: sqlite3.Row) -> Word:
        """Convert a database row to a Word object."""
        etymology_data = json.loads(row["etymology"]) if row["etymology"] else None
        etymology = Etymology(**etymology_data) if etymology_data else None
        
        return Word(
            word=row["word"],
            pronunciation=row["pronunciation"],
            etymology=etymology,
            part_of_speech=row["part_of_speech"],
            meanings=json.loads(row["meanings"]),
            english_translation=row["english_translation"],
            examples=json.loads(row["examples"])
        )

    def search(self, word: str) -> Optional[Word]:
        """
        Search for an exact word match in the dictionary.
        """
        conn = self._get_conn()
        cursor = conn.execute("SELECT * FROM words WHERE word = ?", (word,))
        row = cursor.fetchone()
        if row:
            return self._row_to_word(row)
        return None
    
    def search_fuzzy(self, query: str, max_distance: int = 2) -> List[Word]:
        """
        Search for words with similar spelling (typo tolerance).
        Uses Levenshtein distance.
        
        Args:
            query: The word to search for.
            max_distance: Max edit distance errors allowed (default 2).
        
        Returns:
            List of matching words sorted by similarity.
        """
        conn = self._get_conn()
        cursor = conn.execute(
            """
            SELECT * FROM words 
            WHERE levenshtein(word, ?) <= ? 
            ORDER BY levenshtein(word, ?) ASC 
            LIMIT 50
            """, 
            (query, max_distance, query)
        )
        return [self._row_to_word(row) for row in cursor.fetchall()]

    def search_semantic(self, query: str, top_k: int = 10) -> List[Tuple[Word, float]]:
        """
        Semantic search using neural embeddings.
        Finds words that are conceptually similar to the query,
        even if they don't share exact keywords.
        
        Args:
            query: Natural language query (e.g., "words related to happiness")
            top_k: Number of results to return (default 10)
        
        Returns:
            List of (Word, similarity_score) tuples, sorted by similarity.
        
        Requires:
            - numpy
            - sentence-transformers (for encoding queries)
            - Pre-generated embeddings (run scripts/generate_embeddings.py)
        """
        self._load_embeddings()
        encoder = self._get_encoder()
        
        # Encode the query
        query_embedding = encoder.encode(query, convert_to_numpy=True)
        
        # Compute cosine similarity
        # embeddings are already normalized by sentence-transformers
        similarities = np.dot(self._embeddings, query_embedding)
        
        # Get top-k indices
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            word_info = self._word_index[str(idx)]
            word_id = word_info["id"]
            similarity = float(similarities[idx])
            
            # Fetch full word from DB
            conn = self._get_conn()
            cursor = conn.execute("SELECT * FROM words WHERE id = ?", (word_id,))
            row = cursor.fetchone()
            if row:
                results.append((self._row_to_word(row), similarity))
        
        return results

    def find_similar(self, word: str, top_k: int = 10, include_self: bool = False) -> List[Tuple[Word, float]]:
        """
        Find words with similar meanings (synonyms) using vector similarity.
        
        Unlike search_semantic which takes any text query, this method
        takes a Bengali word that exists in the dictionary and finds
        other words with similar meanings based on pre-computed embeddings.
        
        Args:
            word: A Bengali word to find synonyms for
            top_k: Number of similar words to return (default 10)
            include_self: Whether to include the input word in results (default False)
        
        Returns:
            List of (Word, similarity_score) tuples, sorted by similarity.
        
        Example:
            >>> d.find_similar("আনন্দ")
            [(Word(word='সুখ', ...), 0.89), (Word(word='হর্ষ', ...), 0.85), ...]
        """
        self._load_embeddings()
        
        # Find the word's index in our embeddings
        word_idx = None
        for idx_str, info in self._word_index.items():
            if info["word"] == word:
                word_idx = int(idx_str)
                break
        
        if word_idx is None:
            # Word not found in dictionary, fall back to encoding it
            encoder = self._get_encoder()
            word_embedding = encoder.encode(word, convert_to_numpy=True)
        else:
            # Use pre-computed embedding (faster, no model needed)
            word_embedding = self._embeddings[word_idx]
        
        # Compute similarities
        similarities = np.dot(self._embeddings, word_embedding)
        
        # Get top-k+1 indices (in case we need to exclude self)
        fetch_count = top_k + 1 if not include_self else top_k
        top_indices = np.argsort(similarities)[::-1][:fetch_count]
        
        results = []
        for idx in top_indices:
            # Skip the input word if include_self is False
            if not include_self and idx == word_idx:
                continue
            
            word_info = self._word_index[str(idx)]
            word_id = word_info["id"]
            similarity = float(similarities[idx])
            
            # Fetch full word from DB
            conn = self._get_conn()
            cursor = conn.execute("SELECT * FROM words WHERE id = ?", (word_id,))
            row = cursor.fetchone()
            if row:
                results.append((self._row_to_word(row), similarity))
            
            if len(results) >= top_k:
                break
        
        return results

    def lookup(self, query: str) -> List[Word]:
        """
        Search for words containing the query string (partial match).
        """
        conn = self._get_conn()
        # LIKE query for partial match
        cursor = conn.execute("SELECT * FROM words WHERE word LIKE ? LIMIT 50", (f"%{query}%",))
        return [self._row_to_word(row) for row in cursor.fetchall()]

    def search_english(self, query: str) -> List[Word]:
        """
        Search for words by their English translation.
        """
        conn = self._get_conn()
        cursor = conn.execute("SELECT * FROM words WHERE english_translation LIKE ? LIMIT 50", (f"%{query}%",))
        return [self._row_to_word(row) for row in cursor.fetchall()]

    def get_random(self) -> Word:
        """
        Get a random word from the dictionary.
        """
        conn = self._get_conn()
        # Fast random selection for SQLite
        cursor = conn.execute("SELECT * FROM words ORDER BY RANDOM() LIMIT 1")
        row = cursor.fetchone()
        if row:
            return self._row_to_word(row)
        raise ValueError("Dictionary is empty")

    def stats(self) -> Dict[str, Any]:
        """
        Get statistics about the dictionary.
        """
        conn = self._get_conn()
        cursor = conn.execute("SELECT COUNT(*) as count FROM words")
        count = cursor.fetchone()["count"]
        
        # Check if semantic search is available
        embeddings_path = get_data_path("embeddings.npy")
        has_semantic = embeddings_path.exists()
        
        return {
            "total_words": count,
            "backend": "sqlite",
            "semantic_search": has_semantic
        }
    
    def close(self):
        """Close the database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None
