"""Main orchestrator for the SCALE alignment pipeline."""

import os
from pathlib import Path
from typing import List, Optional, Tuple

from .embeddings import E5Embedder
from .io import (
    get_output_filename,
    load_classification,
    load_correspondence,
    write_alignment,
)
from .retrieval import bidirectional_retrieval
from .selection import (
    AlignmentMatch,
    aggregate_passes,
    competitive_select,
    merge_overlapping_matches,
)


class ScaleAligner:
    """Main class for alignment between classification systems."""

    def __init__(
        self,
        source_dir: str,
        target_dir: str,
        output_dir: str,
        threshold: float = 0.7,
        margin: float = 0.05,
        device: Optional[str] = None,
        batch_size: int = 32,
        model_name: Optional[str] = None,
    ):
        """Initialize the SCALE aligner.

        Args:
            source_dir: Directory containing source classification files.
            target_dir: Directory containing target classification files.
            output_dir: Directory for output alignment files.
            threshold: Minimum similarity score for matches. Defaults to 0.7.
            margin: Margin from champion score for candidates. Defaults to 0.05.
            device: Device for model ('cuda', 'cpu', 'auto'). Defaults to auto.
            batch_size: Batch size for embedding. Defaults to 32.
            model_name: Override model name. Defaults to e5-large-instruct.
        """
        self.source_dir = Path(source_dir)
        self.target_dir = Path(target_dir)
        self.output_dir = Path(output_dir)
        self.threshold = threshold
        self.margin = margin

        # Validate directories
        if not self.source_dir.exists():
            raise FileNotFoundError(f"Source directory not found: {source_dir}")
        if not self.target_dir.exists():
            raise FileNotFoundError(f"Target directory not found: {target_dir}")

        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize embedder (lazy loading)
        self._embedder: Optional[E5Embedder] = None
        self._device = device
        self._batch_size = batch_size
        self._model_name = model_name

    @property
    def embedder(self) -> E5Embedder:
        """Lazy-load the embedder model."""
        if self._embedder is None:
            self._embedder = E5Embedder(
                model_name=self._model_name,
                device=self._device,
                batch_size=self._batch_size,
            )
        return self._embedder

    def _get_source_file(self, code: str) -> Path:
        """Get path to source classification file."""
        return self.source_dir / f"{code}.txt"

    def _get_target_file(self, code: str) -> Path:
        """Get path to target classification file."""
        return self.target_dir / f"{code}.txt"

    def align_pair(
        self, source_code: str, target_code: str
    ) -> List[AlignmentMatch]:
        """Align a single source-target code pair.

        Args:
            source_code: Source classification code.
            target_code: Target classification code.

        Returns:
            List of AlignmentMatch objects.
        """
        # Load sentences
        source_file = self._get_source_file(source_code)
        target_file = self._get_target_file(target_code)

        source_sentences = load_classification(str(source_file))
        target_sentences = load_classification(str(target_file))

        if not source_sentences or not target_sentences:
            return []

        # Encode sentences
        # Forward: source as query, target as passage
        source_query_embeds = self.embedder.encode_queries(source_sentences)
        target_passage_embeds = self.embedder.encode_passages(target_sentences)

        # Backward: target as query, source as passage
        target_query_embeds = self.embedder.encode_queries(target_sentences)
        source_passage_embeds = self.embedder.encode_passages(source_sentences)

        # Compute bidirectional similarity
        from .retrieval import compute_similarity_matrix

        # Forward: source queries vs target passages
        forward_matrix = compute_similarity_matrix(
            source_query_embeds, target_passage_embeds
        )

        # Backward: target queries vs source passages
        backward_matrix = compute_similarity_matrix(
            target_query_embeds, source_passage_embeds
        )

        # Apply competitive selection
        forward_matches = competitive_select(
            forward_matrix,
            threshold=self.threshold,
            margin=self.margin,
            is_forward=True,
        )

        backward_matches = competitive_select(
            backward_matrix,
            threshold=self.threshold,
            margin=self.margin,
            is_forward=False,
        )

        # Aggregate and merge
        aggregated = aggregate_passes(forward_matches, backward_matches)
        merged = merge_overlapping_matches(aggregated)

        return merged

    def run(self, correspondence_path: str, verbose: bool = True) -> int:
        """Run alignment for all pairs in the correspondence file.

        Args:
            correspondence_path: Path to correspondence JSON file.
            verbose: Whether to print progress. Defaults to True.

        Returns:
            Number of pairs processed.
        """
        correspondence = load_correspondence(correspondence_path)

        if verbose:
            print(f"Loaded {len(correspondence)} correspondence pairs")

        processed = 0
        for source_code, target_code in correspondence:
            try:
                if verbose:
                    print(f"Processing: {source_code} <-> {target_code}")

                alignments = self.align_pair(source_code, target_code)

                # Write output
                output_file = get_output_filename(source_code, target_code)
                output_path = self.output_dir / output_file
                write_alignment(str(output_path), alignments)

                processed += 1

            except FileNotFoundError as e:
                if verbose:
                    print(f"  Skipping: {e}")
            except Exception as e:
                if verbose:
                    print(f"  Error: {e}")

        if verbose:
            print(f"Completed: {processed}/{len(correspondence)} pairs")

        return processed
