"""
Enhanced AImakerspace library with metadata filtering and multiple distance metrics.

This enhanced version adds:
- Metadata support for document categorization
- Multiple distance metrics (cosine, euclidean, dot product)
- Improved filtering capabilities
"""

__version__ = "2.0.0"

from aimakerspace.text_utils import TextFileLoader, CharacterTextSplitter
from aimakerspace.vectordatabase import VectorDatabase
from aimakerspace.distance_metrics import (
    cosine_similarity,
    euclidean_distance,
    dot_product_similarity,
    AVAILABLE_METRICS
)

__all__ = [
    "TextFileLoader",
    "CharacterTextSplitter",
    "VectorDatabase",
    "cosine_similarity",
    "euclidean_distance",
    "dot_product_similarity",
    "AVAILABLE_METRICS"
]
