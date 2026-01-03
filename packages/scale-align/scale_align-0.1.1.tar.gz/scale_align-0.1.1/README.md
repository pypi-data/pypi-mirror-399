# SCALE: Standard Classification Alignment & Local Enrichment

Automate the audit and enrichment of national classifications (e.g., KBLI) using international standards (e.g., ISIC, NACE), or other national standard classifications.

## Features

- **Bidirectional Asymmetric Retrieval**: Captures hierarchical "entailment" relationships common in classifications
- **Competitive Selection**: Max-score + margin algorithm for controlled mapping while minimizing noise
- **Multilingual E5-Large-Instruct Model**: Instruction-tuned model optimized for asymmetric retrieval tasks

## Installation

```bash
pip install scale-align
```

## Google Colab

Using in Google Colab? Try our [**Colab Notebook**](examples/colab_quickstart.ipynb).

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/mdmahendri/scale-align/blob/main/examples/colab_quickstart.ipynb)


## Quick Start

```bash
scale-align \
    --source-dir /path/to/isic5 \
    --target-dir /path/to/nace21 \
    --correspondence correspondence.json \
    --output-dir ./output
```

## Input Format

### Classification Files
Text files with sentences separated by newlines:
```
/path/to/isic5/A.txt
/path/to/isic5/A0111.txt
```

### Correspondence JSON
```json
[["A","A"],["A0111","A01.11"],["A0112","A01.12"]]
```

## Output Format

Each output file `{source_code}_{target_code}.txt` contains:
```
[0]:[0,1]:0.87439287
[1,2]:[2]:0.92
[3]:[]:0
[4]:[3]:0.9999999
```

- `[source_indices]:[target_indices]:score`
- Empty brackets `[]` indicate no alignment (gap detected)

## CLI Options

| Option | Default | Description |
|--------|---------|-------------|
| `--threshold` | 0.7 | Minimum similarity score |
| `--margin` | 0.05 | Margin from champion score |
| `--batch-size` | 32 | Embedding batch size |
| `--device` | auto | Device (cuda/cpu/auto) |

## License

MIT
