"""Bidirectional retrieval module for similarity computation."""

from typing import Tuple

import numpy as np


def compute_similarity_matrix(
    source_embeds: np.ndarray, target_embeds: np.ndarray
) -> np.ndarray:
    """Compute cosine similarity matrix between source and target embeddings.

    Args:
        source_embeds: Source embeddings with shape (n_source, embed_dim).
        target_embeds: Target embeddings with shape (n_target, embed_dim).

    Returns:
        Similarity matrix with shape (n_source, n_target).
    """
    # Embeddings are already normalized, so dot product = cosine similarity
    return np.dot(source_embeds, target_embeds.T)


def bidirectional_retrieval(
    source_embeds: np.ndarray, target_embeds: np.ndarray
) -> Tuple[np.ndarray, np.ndarray]:
    """Perform bidirectional retrieval between source and target embeddings.

    Args:
        source_embeds: Source embeddings with shape (n_source, embed_dim).
        target_embeds: Target embeddings with shape (n_target, embed_dim).

    Returns:
        Tuple of (forward_matrix, backward_matrix):
        - forward_matrix: Similarity from source to target (n_source, n_target)
        - backward_matrix: Similarity from target to source (n_target, n_source)
    """
    # Forward pass: source queries -> target passages
    forward_matrix = compute_similarity_matrix(source_embeds, target_embeds)

    # Backward pass: target queries -> source passages
    backward_matrix = compute_similarity_matrix(target_embeds, source_embeds)

    return forward_matrix, backward_matrix
