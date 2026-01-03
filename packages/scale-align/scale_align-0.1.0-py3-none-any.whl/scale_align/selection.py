"""Competitive selection algorithm for alignment matching."""

from dataclasses import dataclass
from typing import Dict, List, Set, Tuple

import numpy as np


@dataclass
class AlignmentMatch:
    """Represents an alignment match between source and target indices."""

    source_indices: List[int]
    target_indices: List[int]
    score: float

    def __hash__(self):
        return hash((tuple(self.source_indices), tuple(self.target_indices)))

    def __eq__(self, other):
        if not isinstance(other, AlignmentMatch):
            return False
        return (
            self.source_indices == other.source_indices
            and self.target_indices == other.target_indices
        )


def competitive_select(
    similarity_matrix: np.ndarray,
    threshold: float = 0.7,
    margin: float = 0.05,
    is_forward: bool = True,
) -> List[AlignmentMatch]:
    """Apply competitive selection to similarity matrix.

    For each row (source), finds the champion (highest score) and keeps
    candidates within the margin of the champion score.

    Args:
        similarity_matrix: Similarity scores with shape (n_source, n_target).
        threshold: Minimum score for a valid match. Defaults to 0.7.
        margin: Margin from champion score to include candidates. Defaults to 0.05.
        is_forward: If True, rows are sources. If False, rows are targets.

    Returns:
        List of AlignmentMatch objects representing valid alignments.
    """
    matches = []
    n_rows, n_cols = similarity_matrix.shape

    for row_idx in range(n_rows):
        row_scores = similarity_matrix[row_idx]

        # Find champion (max score)
        champion_score = np.max(row_scores)

        # Absolute filter: skip if champion is below threshold
        if champion_score < threshold:
            # Create a "no match" entry for gap detection
            if is_forward:
                matches.append(
                    AlignmentMatch(
                        source_indices=[row_idx],
                        target_indices=[],
                        score=0.0,
                    )
                )
            else:
                matches.append(
                    AlignmentMatch(
                        source_indices=[],
                        target_indices=[row_idx],
                        score=0.0,
                    )
                )
            continue

        # Relative margin: keep candidates within margin of champion
        margin_threshold = champion_score - margin
        candidate_indices = np.where(row_scores >= margin_threshold)[0].tolist()

        if is_forward:
            matches.append(
                AlignmentMatch(
                    source_indices=[row_idx],
                    target_indices=candidate_indices,
                    score=float(champion_score),
                )
            )
        else:
            matches.append(
                AlignmentMatch(
                    source_indices=candidate_indices,
                    target_indices=[row_idx],
                    score=float(champion_score),
                )
            )

    return matches


def aggregate_passes(
    forward_matches: List[AlignmentMatch],
    backward_matches: List[AlignmentMatch],
) -> List[AlignmentMatch]:
    """Aggregate forward and backward matches using union strategy.

    Args:
        forward_matches: Matches from source->target pass.
        backward_matches: Matches from target->source pass.

    Returns:
        Unified list of AlignmentMatch objects.
    """
    # Build a dict keyed by (source_tuple, target_tuple) to deduplicate
    # and keep the higher score when duplicates exist
    match_dict: Dict[Tuple[Tuple[int, ...], Tuple[int, ...]], AlignmentMatch] = {}

    for match in forward_matches + backward_matches:
        key = (tuple(sorted(match.source_indices)), tuple(sorted(match.target_indices)))

        if key not in match_dict or match.score > match_dict[key].score:
            match_dict[key] = AlignmentMatch(
                source_indices=sorted(match.source_indices),
                target_indices=sorted(match.target_indices),
                score=match.score,
            )

    # Sort by source indices, then target indices
    result = sorted(
        match_dict.values(),
        key=lambda m: (m.source_indices or [-1], m.target_indices or [-1]),
    )

    return result


def merge_overlapping_matches(matches: List[AlignmentMatch]) -> List[AlignmentMatch]:
    """Merge matches that share source or target indices.

    This handles many-to-one and one-to-many relationships by combining
    overlapping matches into single entries.

    Args:
        matches: List of alignment matches.

    Returns:
        List with overlapping matches merged.
    """
    if not matches:
        return []

    # Build graph of connected matches
    source_to_matches: Dict[int, List[int]] = {}
    target_to_matches: Dict[int, List[int]] = {}

    for i, match in enumerate(matches):
        for src in match.source_indices:
            source_to_matches.setdefault(src, []).append(i)
        for tgt in match.target_indices:
            target_to_matches.setdefault(tgt, []).append(i)

    # Find connected components using union-find
    visited: Set[int] = set()
    merged: List[AlignmentMatch] = []

    def collect_component(start_idx: int) -> Tuple[Set[int], Set[int], float]:
        """Collect all source/target indices in connected component."""
        sources: Set[int] = set()
        targets: Set[int] = set()
        max_score = 0.0
        stack = [start_idx]

        while stack:
            idx = stack.pop()
            if idx in visited:
                continue
            visited.add(idx)

            match = matches[idx]
            sources.update(match.source_indices)
            targets.update(match.target_indices)
            max_score = max(max_score, match.score)

            # Find connected matches via shared sources
            for src in match.source_indices:
                for connected_idx in source_to_matches.get(src, []):
                    if connected_idx not in visited:
                        stack.append(connected_idx)

            # Find connected matches via shared targets
            for tgt in match.target_indices:
                for connected_idx in target_to_matches.get(tgt, []):
                    if connected_idx not in visited:
                        stack.append(connected_idx)

        return sources, targets, max_score

    for i in range(len(matches)):
        if i not in visited:
            sources, targets, score = collect_component(i)
            merged.append(
                AlignmentMatch(
                    source_indices=sorted(sources),
                    target_indices=sorted(targets),
                    score=score,
                )
            )

    # Sort by source indices
    merged.sort(key=lambda m: (m.source_indices or [-1], m.target_indices or [-1]))

    return merged
