"""Command-line interface for SCALE aligner."""

import click

from .aligner import ScaleAligner


@click.command()
@click.option(
    "--source-dir",
    "-s",
    required=True,
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    help="Directory containing source classification files.",
)
@click.option(
    "--target-dir",
    "-t",
    required=True,
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    help="Directory containing target classification files.",
)
@click.option(
    "--correspondence",
    "-c",
    required=True,
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
    help="Path to correspondence JSON file.",
)
@click.option(
    "--output-dir",
    "-o",
    required=True,
    type=click.Path(file_okay=False, dir_okay=True),
    help="Directory for output alignment files.",
)
@click.option(
    "--threshold",
    default=0.7,
    type=float,
    help="Minimum similarity score for matches. Default: 0.7",
)
@click.option(
    "--margin",
    default=0.05,
    type=float,
    help="Margin from champion score for candidates. Default: 0.05",
)
@click.option(
    "--batch-size",
    default=32,
    type=int,
    help="Batch size for embedding. Default: 32",
)
@click.option(
    "--device",
    default="auto",
    type=click.Choice(["auto", "cuda", "cpu"]),
    help="Device for model inference. Default: auto",
)
@click.option(
    "--model",
    default=None,
    type=str,
    help="Override model name. Default: intfloat/e5-large-instruct",
)
@click.option(
    "--quiet",
    "-q",
    is_flag=True,
    help="Suppress progress output.",
)
def main(
    source_dir: str,
    target_dir: str,
    correspondence: str,
    output_dir: str,
    threshold: float,
    margin: float,
    batch_size: int,
    device: str,
    model: str,
    quiet: bool,
) -> None:
    """SCALE: Standard Classification Alignment & Local Enrichment.

    Align classifications between source and target systems using
    bidirectional asymmetric retrieval with competitive selection.
    """
    aligner = ScaleAligner(
        source_dir=source_dir,
        target_dir=target_dir,
        output_dir=output_dir,
        threshold=threshold,
        margin=margin,
        device=device if device != "auto" else None,
        batch_size=batch_size,
        model_name=model,
    )

    processed = aligner.run(
        correspondence_path=correspondence,
        verbose=not quiet,
    )

    if not quiet:
        click.echo(f"\nAlignment complete. Output written to: {output_dir}")


if __name__ == "__main__":
    main()
