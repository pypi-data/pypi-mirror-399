"""Unit tests for competitive selection algorithm."""

import numpy as np
import pytest

from scale_align.selection import (
    AlignmentMatch,
    aggregate_passes,
    competitive_select,
    merge_overlapping_matches,
)


class TestCompetitiveSelect:
    """Tests for competitive_select function."""

    def test_champion_above_threshold(self):
        """Test that champion score above threshold returns match."""
        # Shape: 2 sources, 3 targets
        similarity_matrix = np.array([
            [0.9, 0.7, 0.3],  # Champion is 0.9 at index 0
            [0.4, 0.8, 0.5],  # Champion is 0.8 at index 1
        ])

        matches = competitive_select(
            similarity_matrix, threshold=0.7, margin=0.05, is_forward=True
        )

        assert len(matches) == 2
        # First source: champion 0.9. Margin threshold = 0.85. Only index 0 qualifies
        assert matches[0].source_indices == [0]
        assert matches[0].target_indices == [0]
        assert matches[0].score == pytest.approx(0.9)

        # Second source: champion 0.8. Margin threshold = 0.75. Only index 1 qualifies
        assert matches[1].source_indices == [1]
        assert matches[1].target_indices == [1]
        assert matches[1].score == pytest.approx(0.8)

    def test_champion_below_threshold_creates_gap(self):
        """Test that scores below threshold create no-match entries."""
        similarity_matrix = np.array([
            [0.5, 0.4, 0.3],  # All below threshold
        ])

        matches = competitive_select(
            similarity_matrix, threshold=0.7, margin=0.05, is_forward=True
        )

        assert len(matches) == 1
        assert matches[0].source_indices == [0]
        assert matches[0].target_indices == []  # No match (gap)
        assert matches[0].score == 0.0

    def test_margin_includes_multiple_candidates(self):
        """Test that candidates within margin are included."""
        similarity_matrix = np.array([
            [0.90, 0.88, 0.85, 0.70],  # Champion 0.90, margin includes 0.88 and 0.85
        ])

        matches = competitive_select(
            similarity_matrix, threshold=0.7, margin=0.05, is_forward=True
        )

        assert len(matches) == 1
        assert matches[0].source_indices == [0]
        # 0.90 - 0.05 = 0.85, so indices 0, 1, 2 qualify
        assert matches[0].target_indices == [0, 1, 2]
        assert matches[0].score == pytest.approx(0.90)

    def test_backward_pass_swaps_source_target(self):
        """Test backward pass correctly assigns indices."""
        similarity_matrix = np.array([
            [0.9, 0.7],
        ])

        matches = competitive_select(
            similarity_matrix, threshold=0.7, margin=0.05, is_forward=False
        )

        assert len(matches) == 1
        # In backward pass, rows are targets
        assert matches[0].source_indices == [0]  # Candidates from columns
        assert matches[0].target_indices == [0]  # Row index


class TestAggregatePasses:
    """Tests for aggregate_passes function."""

    def test_union_of_matches(self):
        """Test that forward and backward matches are unioned."""
        forward = [
            AlignmentMatch([0], [0, 1], 0.9),
            AlignmentMatch([1], [], 0.0),
        ]
        backward = [
            AlignmentMatch([2], [0], 0.85),
            AlignmentMatch([0], [1], 0.88),  # Overlapping with forward
        ]

        result = aggregate_passes(forward, backward)

        # Should have 3 unique matches (dedup the [0]->[0,1])
        assert len(result) >= 3

    def test_keeps_higher_score_for_duplicates(self):
        """Test that duplicates keep the higher score."""
        forward = [AlignmentMatch([0], [1], 0.8)]
        backward = [AlignmentMatch([0], [1], 0.9)]

        result = aggregate_passes(forward, backward)

        assert len(result) == 1
        assert result[0].score == pytest.approx(0.9)


class TestMergeOverlappingMatches:
    """Tests for merge_overlapping_matches function."""

    def test_merges_shared_source(self):
        """Test matches with shared source are merged."""
        matches = [
            AlignmentMatch([0], [1], 0.9),
            AlignmentMatch([0], [2], 0.85),
        ]

        result = merge_overlapping_matches(matches)

        assert len(result) == 1
        assert set(result[0].source_indices) == {0}
        assert set(result[0].target_indices) == {1, 2}
        assert result[0].score == pytest.approx(0.9)

    def test_merges_shared_target(self):
        """Test matches with shared target are merged."""
        matches = [
            AlignmentMatch([0], [1], 0.9),
            AlignmentMatch([2], [1], 0.85),
        ]

        result = merge_overlapping_matches(matches)

        assert len(result) == 1
        assert set(result[0].source_indices) == {0, 2}
        assert set(result[0].target_indices) == {1}

    def test_keeps_separate_non_overlapping(self):
        """Test non-overlapping matches stay separate."""
        matches = [
            AlignmentMatch([0], [1], 0.9),
            AlignmentMatch([2], [3], 0.85),
        ]

        result = merge_overlapping_matches(matches)

        assert len(result) == 2
