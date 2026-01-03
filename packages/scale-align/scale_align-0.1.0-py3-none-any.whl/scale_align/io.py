"""File I/O utilities for classification and correspondence data."""

import json
import os
from pathlib import Path
from typing import List, Tuple

from .selection import AlignmentMatch


def load_classification(file_path: str) -> List[str]:
    """Load classification sentences from a text file.

    Args:
        file_path: Path to the classification file.

    Returns:
        List of sentences (one per line).
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Classification file not found: {file_path}")

    with open(path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    return lines


def load_correspondence(json_path: str) -> List[Tuple[str, str]]:
    """Load correspondence mapping from JSON file.

    Args:
        json_path: Path to the JSON correspondence file.

    Returns:
        List of (source_code, target_code) tuples.
    """
    path = Path(json_path)
    if not path.exists():
        raise FileNotFoundError(f"Correspondence file not found: {json_path}")

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Expected format: [["A","A"],["A0111","A01.11"],...]
    if not isinstance(data, list):
        raise ValueError("Correspondence JSON must be a list")

    correspondence = []
    for item in data:
        if not isinstance(item, list) or len(item) != 2:
            raise ValueError(f"Invalid correspondence item: {item}")
        correspondence.append((str(item[0]), str(item[1])))

    return correspondence


def format_indices(indices: List[int]) -> str:
    """Format a list of indices as a string.

    Args:
        indices: List of integer indices.

    Returns:
        Formatted string like "[0]", "[1,2]", or "[]".
    """
    if not indices:
        return "[]"
    return "[" + ",".join(str(i) for i in indices) + "]"


def format_alignment(match: AlignmentMatch) -> str:
    """Format an alignment match as an output line.

    Args:
        match: AlignmentMatch to format.

    Returns:
        Formatted string like "[0]:[0,1]:0.87439287".
    """
    src_str = format_indices(match.source_indices)
    tgt_str = format_indices(match.target_indices)
    return f"{src_str}:{tgt_str}:{match.score}"


def write_alignment(
    output_path: str,
    alignments: List[AlignmentMatch],
) -> None:
    """Write alignments to output file.

    Args:
        output_path: Path to the output file.
        alignments: List of AlignmentMatch objects to write.
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        for match in alignments:
            f.write(format_alignment(match) + "\n")


def get_output_filename(source_code: str, target_code: str) -> str:
    """Generate output filename from source and target codes.

    Args:
        source_code: Source classification code.
        target_code: Target classification code.

    Returns:
        Filename like "A0111_A01.11.txt".
    """
    # Sanitize codes for filename (replace invalid chars)
    safe_source = source_code.replace("/", "_").replace("\\", "_")
    safe_target = target_code.replace("/", "_").replace("\\", "_")
    return f"{safe_source}_{safe_target}.txt"
