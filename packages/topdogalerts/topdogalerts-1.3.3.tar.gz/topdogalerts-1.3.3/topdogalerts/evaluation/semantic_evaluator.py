# topdogalerts/evaluation/semantic_evaluator.py
"""
Semantic embedding evaluator for topdogalerts.

Uses sentence-transformers to compute semantic similarity between
event content and trigger keywords for news-style matching.

Note: numpy and sentence-transformers are lazily imported to avoid
requiring these dependencies for listeners that don't use semantic evaluation.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from functools import lru_cache
from typing import Any, List, Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np

logger = logging.getLogger(__name__)

# Lazy-loaded instances
_model = None
_np = None
_MODEL_NAME = "all-MiniLM-L6-v2"


class SemanticEvaluationError(Exception):
    """Error during semantic evaluation."""
    pass


def _get_numpy():
    """Lazy-load numpy."""
    global _np
    if _np is None:
        try:
            import numpy
            _np = numpy
        except ImportError as e:
            raise SemanticEvaluationError(
                "numpy package not installed. "
                "Install with: pip install numpy"
            ) from e
    return _np


def _get_model():
    """Lazy-load the sentence-transformers model."""
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            logger.info(f"Loading sentence-transformers model: {_MODEL_NAME}")
            _model = SentenceTransformer(_MODEL_NAME)
            logger.info(f"Model loaded successfully")
        except ImportError as e:
            raise SemanticEvaluationError(
                "sentence-transformers package not installed. "
                "Install with: pip install sentence-transformers"
            ) from e
        except Exception as e:
            raise SemanticEvaluationError(
                f"Failed to load model {_MODEL_NAME}: {e}"
            ) from e
    return _model


def encode_text(text: str) -> Any:
    """
    Encode text into a normalized embedding vector.

    Args:
        text: The text to encode.

    Returns:
        A normalized numpy array (384 dimensions for all-MiniLM-L6-v2).
        With normalized embeddings, dot product = cosine similarity.
    """
    model = _get_model()
    embedding = model.encode(text, normalize_embeddings=True)
    return embedding


@lru_cache(maxsize=1024)
def _encode_keyword(keyword: str) -> Tuple[float, ...]:
    """
    Encode a single keyword/phrase with caching.

    Returns a tuple (hashable) for caching purposes.
    """
    embedding = encode_text(keyword.strip())
    return tuple(embedding.tolist())


def compute_max_similarity(
    content_embedding: Any,
    keywords_csv: str,
) -> Tuple[float, Optional[str]]:
    """
    Compute the maximum similarity between content and any keyword.

    Args:
        content_embedding: Normalized embedding of the content (numpy array).
        keywords_csv: Comma-separated keywords/phrases.

    Returns:
        Tuple of (max_similarity, best_matching_keyword):
        - max_similarity: Maximum cosine similarity (0.0 to 1.0) across all keywords.
        - best_matching_keyword: The keyword that produced the highest similarity.
    """
    if not keywords_csv or not keywords_csv.strip():
        return 0.0, None

    keywords = [k.strip() for k in keywords_csv.split(",") if k.strip()]
    if not keywords:
        return 0.0, None

    np = _get_numpy()
    max_similarity = 0.0
    best_keyword: Optional[str] = None

    for keyword in keywords:
        # Get cached keyword embedding (as tuple)
        keyword_embedding_tuple = _encode_keyword(keyword)
        keyword_embedding = np.array(keyword_embedding_tuple)

        # Dot product of normalized vectors = cosine similarity
        similarity = float(np.dot(content_embedding, keyword_embedding))
        logger.debug(f"Keyword '{keyword}' similarity: {similarity:.4f}")

        if similarity > max_similarity:
            max_similarity = similarity
            best_keyword = keyword

    return max_similarity, best_keyword


@dataclass
class SemanticMatchResult:
    """Result of a semantic trigger evaluation."""
    triggered: bool
    similarity: float
    threshold_percent: float
    best_keyword: Optional[str]


def evaluate_semantic_trigger(
    content_embedding: Any,
    keywords_csv: str,
    threshold_percent: float,
) -> SemanticMatchResult:
    """
    Evaluate if content matches keywords above threshold.

    Args:
        content_embedding: Normalized embedding of the content.
        keywords_csv: Comma-separated keywords/phrases to match.
        threshold_percent: Similarity threshold as percentage (0-100).
                          e.g., 70 means require >= 0.70 cosine similarity.

    Returns:
        SemanticMatchResult with triggered status, similarity score,
        threshold, and best matching keyword.
    """
    threshold = threshold_percent / 100.0
    logger.debug(f"Evaluating trigger with keywords: '{keywords_csv}' (threshold: {threshold_percent}%)")
    max_similarity, best_keyword = compute_max_similarity(content_embedding, keywords_csv)
    triggered = max_similarity >= threshold
    logger.debug(f"Max similarity: {max_similarity:.4f}, threshold: {threshold:.4f}, triggered: {triggered}")
    return SemanticMatchResult(
        triggered=triggered,
        similarity=max_similarity,
        threshold_percent=threshold_percent,
        best_keyword=best_keyword,
    )


def clear_keyword_cache() -> None:
    """Clear the keyword embedding cache."""
    _encode_keyword.cache_clear()
    logger.debug("Keyword embedding cache cleared")
