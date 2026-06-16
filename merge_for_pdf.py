#!/usr/bin/env python3
"""Merge all TOC-listed notebooks into a single notebook for PDF export."""

from __future__ import annotations

import copy
import hashlib
import json
import re
import shutil
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Iterable, Optional
from urllib.parse import urlparse

import yaml

ROOT = Path(__file__).resolve().parent
TOC_PATH = ROOT / "_toc.yml"
OUTPUT_NOTEBOOK = ROOT / "pdf" / "CMSC320TextBook.ipynb"
ASSETS_DIR = ROOT / "pdf" / "pdf_assets"

IMAGE_OMITTED = "_[Image omitted in PDF — see the online textbook]_"
# Characters that break nbconvert's Pandoc → LaTeX image pipeline.
LATEX_UNSAFE_URL_RE = re.compile(r"[*#%&{}~^\\]")
SUPPORTED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".pdf"}

_image_cache: dict[str, Optional[str]] = {}


def resolve_source(rel: str) -> Optional[Path]:
    """Resolve a TOC entry to an existing .ipynb or .md file."""
    path = ROOT / rel
    if path.is_file():
        return path
    for suffix in (".ipynb", ".md"):
        candidate = path.with_suffix(suffix)
        if candidate.is_file():
            return candidate
    return None


def load_notebook(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def url_unsafe_for_latex(url: str) -> bool:
    return bool(LATEX_UNSAFE_URL_RE.search(url))


def image_url_unsupported(url: str) -> bool:
    if url_unsafe_for_latex(url):
        return True
    return bool(re.search(r"\.(?:gif|webp)(?:\?|$)", url, re.IGNORECASE))


def reset_pdf_assets() -> None:
    _image_cache.clear()
    if ASSETS_DIR.exists():
        shutil.rmtree(ASSETS_DIR)
    ASSETS_DIR.mkdir(parents=True)


def _asset_name(source_key: str, suffix: str) -> str:
    digest = hashlib.sha256(source_key.encode()).hexdigest()[:20]
    return f"{digest}{suffix}"


def _store_image(source_key: str, data: bytes, suffix: str) -> str:
    name = _asset_name(source_key, suffix)
    dest = ASSETS_DIR / name
    if not dest.exists():
        dest.write_bytes(data)
    rel = f"pdf_assets/{name}"
    _image_cache[source_key] = rel
    return rel


def _copy_local_image(path: Path) -> Optional[str]:
    key = str(path.resolve())
    if key in _image_cache:
        return _image_cache[key]

    suffix = path.suffix.lower()
    if suffix not in SUPPORTED_IMAGE_EXTENSIONS:
        _image_cache[key] = None
        return None

    try:
        return _store_image(key, path.read_bytes(), suffix)
    except OSError as exc:
        print(f"Warning: could not copy image {path}: {exc}", file=sys.stderr)
        _image_cache[key] = None
        return None


def _download_remote_image(url: str) -> Optional[str]:
    if url in _image_cache:
        return _image_cache[url]

    if image_url_unsupported(url):
        _image_cache[url] = None
        return None

    suffix = Path(urlparse(url).path).suffix.lower()
    if suffix and suffix not in SUPPORTED_IMAGE_EXTENSIONS:
        _image_cache[url] = None
        return None
    if not suffix:
        suffix = ".png"

    try:
        request = urllib.request.Request(
            url,
            headers={"User-Agent": "CMSC320TextBook-PDF/1.0"},
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            return _store_image(url, response.read(), suffix)
    except (OSError, urllib.error.URLError, ValueError) as exc:
        print(f"Warning: could not download image {url}: {exc}", file=sys.stderr)
        _image_cache[url] = None
        return None


def resolve_image_for_pdf(url: str, notebook_path: Optional[Path] = None) -> Optional[str]:
    """Return a notebook-relative asset path, or None to omit the image."""
    if url.startswith(("http://", "https://")):
        return _download_remote_image(url)

    if notebook_path is None:
        return None

    local_path = (notebook_path.parent / url).resolve()
    if not local_path.is_file():
        return None
    return _copy_local_image(local_path)


def sanitize_markdown_for_pdf(text: str, notebook_path: Optional[Path] = None) -> str:
    """Fix markdown patterns that break nbconvert's Pandoc/LaTeX pipeline."""
    # Horizontal rules: Pandoc treats standalone --- as YAML metadata delimiters.
    sanitized_lines = []
    for line in text.splitlines(keepends=True):
        if line.strip() == "---":
            sanitized_lines.append("***\n" if line.endswith("\n") else "***")
        else:
            sanitized_lines.append(line)
    text = "".join(sanitized_lines)

    # HTML tables often break Pandoc when merged into one large notebook export.
    text = re.sub(
        r"<table\b[^>]*>.*?</table>",
        "\n\n_[Table omitted in PDF — see the online textbook]_\n\n",
        text,
        flags=re.DOTALL | re.IGNORECASE,
    )

    # Strip layout wrappers; keep inner content.
    text = re.sub(r"</?center>", "", text, flags=re.IGNORECASE)
    text = re.sub(r"</?div[^>]*>", "", text, flags=re.IGNORECASE)

    # Jupyter Book / MyST directives are not supported in nbconvert PDF.
    text = re.sub(r"```\{[^`]+\}```", "", text, flags=re.DOTALL)
    text = re.sub(r"^\{[^}\n]+\}\s*$", "", text, flags=re.MULTILINE)

    # Embedded widgets/forms do not render in static PDF.
    text = re.sub(
        r"<iframe\b[^>]*>.*?</iframe>",
        "\n\n_[Interactive content omitted in PDF]_\n\n",
        text,
        flags=re.DOTALL | re.IGNORECASE,
    )

    # Resolve images before inline-math normalization ($ appears in some CDN URLs).
    def replace_html_image(match: re.Match[str]) -> str:
        tag = match.group(0)
        src_match = re.search(r"""src=["']([^"']+)["']""", tag, re.IGNORECASE)
        if not src_match:
            return tag
        alt_match = re.search(r"""alt=["']([^"']*)["']""", tag, re.IGNORECASE)
        alt = alt_match.group(1) if alt_match else "image"
        local = resolve_image_for_pdf(src_match.group(1), notebook_path)
        if local is None:
            return f"\n\n{IMAGE_OMITTED}\n\n"
        return f"![{alt}]({local})"

    text = re.sub(r"<img\b[^>]*>", replace_html_image, text, flags=re.IGNORECASE)

    def replace_markdown_image(match: re.Match[str]) -> str:
        alt, url = match.group(1), match.group(2)
        local = resolve_image_for_pdf(url, notebook_path)
        if local is None:
            return f"\n\n{IMAGE_OMITTED}\n\n"
        return f"![{alt}]({local})"

    text = re.sub(
        r"!\[([^\]]*)\]\(([^)]+)\)",
        replace_markdown_image,
        text,
    )

    # Single-$ blocks that contain LaTeX environments must use display math.
    text = re.sub(
        r"\$\s*(\\begin\{[^}]+\}.*?\\end\{[^}]+\})\s*\$",
        r"$$\1$$",
        text,
        flags=re.DOTALL,
    )

    # Pandoc treats `$ x $` as text, not inline math; normalize inline delimiters only.
    display_math_blocks: list[str] = []

    def protect_display_math(match: re.Match[str]) -> str:
        display_math_blocks.append(match.group(0))
        return f"@@DISPLAYMATH{len(display_math_blocks) - 1}@@"

    text = re.sub(
        r"\$\$.*?\$\$",
        protect_display_math,
        text,
        flags=re.DOTALL,
    )
    text = re.sub(
        r"\$([^$]+)\$",
        lambda match: (
            f"$${match.group(1).strip()}$$"
            if "\\begin{" in match.group(1)
            else f"${match.group(1).strip()}$"
        ),
        text,
    )
    for index, block in enumerate(display_math_blocks):
        text = text.replace(f"@@DISPLAYMATH{index}@@", block)

    return text


def markdown_cell(text: str, notebook_path: Optional[Path] = None) -> dict[str, Any]:
    text = sanitize_markdown_for_pdf(text, notebook_path)
    if text and not text.endswith("\n"):
        text += "\n"
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": text.splitlines(keepends=True),
    }


def md_file_to_cells(path: Path) -> list[dict[str, Any]]:
    return [markdown_cell(path.read_text(encoding="utf-8"), path)]


def should_include_cell(cell: dict[str, Any]) -> bool:
    tags = cell.get("metadata", {}).get("tags", [])
    return "remove-cell" not in tags


def notebook_cells(path: Path) -> Iterable[dict[str, Any]]:
    nb = load_notebook(path)
    for cell in nb.get("cells", []):
        if not should_include_cell(cell):
            continue
        cell = copy.deepcopy(cell)
        if cell.get("cell_type") == "markdown":
            src = cell.get("source", [])
            text = src if isinstance(src, str) else "".join(src)
            cell["source"] = markdown_cell(text, path)["source"]
        yield cell


def iter_toc_entries() -> Iterable[tuple[str, Path]]:
    with TOC_PATH.open(encoding="utf-8") as f:
        toc = yaml.safe_load(f)

    for part in toc.get("parts", []):
        caption = part.get("caption") or ""
        for entry in part.get("chapters", []):
            rel = entry.get("file")
            if not rel:
                continue
            path = resolve_source(rel)
            if path is None:
                print(f"Warning: skipping missing TOC entry: {rel}", file=sys.stderr)
                continue
            yield caption, path


def build_merged_notebook() -> dict[str, Any]:
    merged_cells: list[dict[str, Any]] = []
    base_metadata: dict[str, Any] = {}
    nbformat_minor = 0

    merged_cells.append(
        markdown_cell(
            "# CMSC320 Textbook\n\n"
            "Dr. Fardina Alam and Gavin Hung\n\n"
            "_Generated from the Jupyter Book table of contents (`_toc.yml`)._\n"
        )
    )

    current_part: Optional[str] = None
    notebook_count = 0
    md_count = 0

    for caption, path in iter_toc_entries():
        if caption and caption != current_part:
            merged_cells.append(markdown_cell(f"# {caption}\n"))
            current_part = caption

        if path.suffix == ".ipynb":
            nb = load_notebook(path)
            if not base_metadata:
                base_metadata = copy.deepcopy(nb.get("metadata", {}))
                nbformat_minor = max(nb.get("nbformat_minor", 0), nbformat_minor)
            merged_cells.extend(notebook_cells(path))
            notebook_count += 1
        elif path.suffix == ".md":
            merged_cells.append(
                markdown_cell(f"## {path.stem.replace('_', ' ')}\n")
            )
            merged_cells.extend(md_file_to_cells(path))
            md_count += 1

    has_cell_ids = any("id" in cell for cell in merged_cells)
    if has_cell_ids:
        nbformat_minor = max(nbformat_minor, 5)

    return {
        "cells": merged_cells,
        "metadata": base_metadata
        or {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {"name": "python"},
        },
        "nbformat": 4,
        "nbformat_minor": nbformat_minor,
    }


def main() -> None:
    OUTPUT_NOTEBOOK.parent.mkdir(parents=True, exist_ok=True)
    reset_pdf_assets()
    merged = build_merged_notebook()
    OUTPUT_NOTEBOOK.write_text(
        json.dumps(merged, indent=1, ensure_ascii=False), encoding="utf-8"
    )
    print(
        f"Wrote {OUTPUT_NOTEBOOK} "
        f"({len(merged['cells'])} cells from _toc.yml)"
    )


if __name__ == "__main__":
    main()
