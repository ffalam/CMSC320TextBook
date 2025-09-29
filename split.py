import argparse
import json
import math
from pathlib import Path


def split_notebook(notebook_path, cells_per_file=5):

    notebook_path = Path(notebook_path)

    if not notebook_path.exists():
        print(f"Error: File '{notebook_path}' not found")
        return

    with open(notebook_path, "r", encoding="utf-8") as f:
        notebook = json.load(f)

    cells = notebook["cells"]
    total_cells = len(cells)

    num_files = math.ceil(total_cells / cells_per_file)

    base_name = notebook_path.stem
    output_dir = notebook_path.parent

    for i in range(num_files):
        start_idx = i * cells_per_file
        end_idx = min((i + 1) * cells_per_file, total_cells)
        cells_subset = cells[start_idx:end_idx]

        new_notebook = {
            "cells": cells_subset,
            "metadata": notebook["metadata"],
            "nbformat": notebook["nbformat"],
            "nbformat_minor": notebook["nbformat_minor"],
        }

        output_filename = output_dir / f"{base_name}_{i}.ipynb"
        with open(output_filename, "w", encoding="utf-8") as f:
            json.dump(new_notebook, f, indent=1)

        print(f"Created {output_filename} with {len(cells_subset)} cells")

    print(f"\nSplit {total_cells} cells into {num_files} files")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Split a Jupyter notebook into multiple files"
    )
    parser.add_argument(
        "notebook", help="Path to the notebook file (e.g., /path/to/Chapter_5.ipynb)"
    )
    parser.add_argument(
        "--cells", type=int, default=10, help="Number of cells per file (default: 5)"
    )

    args = parser.parse_args()

    split_notebook(args.notebook, args.cells)
