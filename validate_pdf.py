#!/usr/bin/env python3
"""Validate the merged textbook PDF produced by merge.sh."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent
PDF_PATH = ROOT / "pdf" / "CMSC320TextBook.pdf"
NOTEBOOK_PATH = ROOT / "pdf" / "CMSC320TextBook.ipynb"
TOC_PATH = ROOT / "_toc.yml"

# Stable strings that should appear when the full book is present.
REQUIRED_ANCHORS = [
    "CMSC320 Textbook",
    "About the Book",
    "Preface",
    "Chapter 1 - Intro to Data Science",
    "Chapter 20 - NLPs",
    "Introduction: What is Natural Language Processing?",
    "Chapter 22",
    "Recommender Systems",
    "Knowledge Check",
    "Summary of the Chapter",
    "Gradient Descent: Pseudocode",
]


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(1)


def pdf_text() -> str:
    if not PDF_PATH.is_file():
        fail(f"Missing PDF: {PDF_PATH}. Run ./merge.sh first.")
    try:
        return subprocess.check_output(["pdftotext", str(PDF_PATH), "-"], text=True)
    except FileNotFoundError:
        fail("pdftotext not found. Install poppler (e.g. brew install poppler).")
    except subprocess.CalledProcessError as exc:
        fail(f"pdftotext failed: {exc}")


def validate_pdf_bytes() -> None:
    data = PDF_PATH.read_bytes()
    if not data.startswith(b"%PDF"):
        fail("Invalid PDF header.")
    if b"%%EOF" not in data[-2048:]:
        fail("PDF is missing an EOF marker.")


def validate_metadata(text: str) -> int:
    try:
        pages = int(
            subprocess.check_output(
                ["pdfinfo", str(PDF_PATH)], text=True, stderr=subprocess.DEVNULL
            ).split("Pages:")[1].splitlines()[0].strip()
        )
    except (FileNotFoundError, IndexError, ValueError):
        pages = text.count("\f") or text.count("\x0c")
    if pages < 100:
        fail(f"Expected a full textbook PDF, got only {pages} pages.")
    return pages


def validate_anchors(text: str) -> None:
    missing = [anchor for anchor in REQUIRED_ANCHORS if anchor not in text]
    if missing:
        fail("Missing expected content:\n  - " + "\n  - ".join(missing))


def validate_merge_outputs(pages: int) -> None:
    if not NOTEBOOK_PATH.is_file():
        fail(f"Missing merged notebook: {NOTEBOOK_PATH}")

    nb = json.loads(NOTEBOOK_PATH.read_text(encoding="utf-8"))
    cell_count = len(nb.get("cells", []))
    if cell_count < 300:
        fail(f"Merged notebook looks incomplete ({cell_count} cells).")

    toc = yaml.safe_load(TOC_PATH.read_text(encoding="utf-8"))
    toc_entries = sum(
        1
        for part in toc.get("parts", [])
        for entry in part.get("chapters", [])
        if entry.get("file")
    )
    if toc_entries < 100:
        fail(f"_toc.yml looks incomplete ({toc_entries} entries).")

    assets = list((ROOT / "pdf" / "pdf_assets").glob("*"))
    print(f"PDF pages: {pages}")
    print(f"Merged notebook cells: {cell_count}")
    print(f"TOC entries: {toc_entries}")
    print(f"Cached PDF images: {len(assets)}")
    print("Anchor checks: OK")


def main() -> None:
    validate_pdf_bytes()
    text = pdf_text()
    pages = validate_metadata(text)
    validate_anchors(text)
    validate_merge_outputs(pages)
    print(f"Validation passed: {PDF_PATH}")


if __name__ == "__main__":
    main()
