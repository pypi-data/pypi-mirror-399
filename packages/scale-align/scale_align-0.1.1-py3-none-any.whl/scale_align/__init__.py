"""SCALE: Standard Classification Alignment & Local Enrichment."""

from .aligner import ScaleAligner
from .embeddings import E5Embedder
from .retrieval import compute_similarity_matrix, bidirectional_retrieval
from .selection import competitive_select, aggregate_passes

__version__ = "0.1.0"

__all__ = [
    "ScaleAligner",
    "E5Embedder",
    "compute_similarity_matrix",
    "bidirectional_retrieval",
    "competitive_select",
    "aggregate_passes",
]
