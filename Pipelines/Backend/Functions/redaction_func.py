"""
pdf_redactor.py
Permanently redact text matching patterns from PDF files.

Dependencies: pymupdf
Install:      pip install pymupdf

Usage:
    python pdf_redactor.py --input document.pdf --patterns "John Smith" "ACC-\d+"
    python pdf_redactor.py --input document.pdf --categories email phone
    python pdf_redactor.py --input ./pdfs --patterns "CONFIDENTIAL-\d+" --categories email

Built-in categories (--categories):
    email     Email addresses
    phone     Phone numbers (various formats)
    cpr       DK Social Security numbers
    credit    Credit card numbers
    postcode  UK postcodes
    date      Common date formats
    case-id   case identifcation found in material
    case-num  unique casenumber found in material
    address   standard Danish address schema

NOTE: Always verify redaction output before distributing.
      Test on a copy before processing originals.
"""

import os
import re
import sys
from pathlib import Path
from dataclasses import dataclass

import pymupdf

# ── CONFIG ────────────────────────────────────────────────────────────────────
INPUT_PATH = "input.pdf"
OUTPUT_DIR = "./redacted"
PATTERNS = []  # List of regex patterns or exact strings
CATEGORIES = []  # Built-in pattern categories
REDACT_COLOR = (0, 0, 0)  # RGB fill color (black)
TEXT_COLOR = (1, 1, 1)
WHOLE_WORD = False  # Match whole words only for exact string patterns
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class RedactionConfig:
    output_dir: Path = Path("Pipelines/Backend/Data/output/redacted")
    redact_color: tuple[float, float, float] = (0, 0, 0)
    text_color: tuple[float, float, float] = (1, 1, 1)
    fontname: str = "helv"
    fontsize: int = 6


BUILTIN_PATTERNS = {
    "email": r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}",
    "phone": r"(\+?\d[\d\s\-().]{6,}\d)",
    "cpr": r"\b\d{6}-\d{4}",
    "credit": r"\b(?:\d[ -]?){13,16}\b",
    "postcode": r"\b[A-Z]{1,2}\d[A-Z\d]?\s?\d[A-Z]{2}\b",
    "date": r"\b(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}|\d{4}[\/\-]\d{2}[\/\-]\d{2})\b",
    "case-id": r"([a-zA-Z0-9]{3}\s\d.\.\d.\.[a-zA-Z0-9]{5})",
    "case-num": r"Sagsnr[.,]?\s*:\s*([^\r\n]+)",
    "address": r"\b[A-ZÆØÅ][a-zæøåA-ZÆØÅ0-9\s.-]+?\s+\d+[A-Za-z]?(?:,\s*(?:st|kl|\d+)\.?(?:\s*(?:tv|th|mf|\d+))?)?,\s*\d{4}\s+[A-ZÆØÅ][a-zæøåA-ZÆØÅ\s.-]+\b\s",
}

def configure_tesseract_path():
    if getattr(sys, "frozen", False):
        app_dir = Path(sys.executable).parent
    else:
        app_dir = Path(__file__).resolve().parent

    tesseract_dir = app_dir / "tools" / "tesseract"

    os.environ["PATH"] = (
        str(tesseract_dir)
        + os.pathsep
        + os.environ.get("PATH", "")
    )

    os.environ["TESSDATA_PREFIX"] = str(
        tesseract_dir / "tessdata"
    )

def _build_patterns(
    raw_patterns: list[str],
    categories: list[str],
    whole_word: bool,
    barn_navn: list[str],
    foraeldre_1: list[str],
    foraeldre_2: list[str],
) -> list[tuple[str, re.Pattern]]:
    compiled = []

    for cat in categories:
        if cat not in BUILTIN_PATTERNS:
            print(
                f"  [WARN] Unknown category: '{cat}'. Available: {list(BUILTIN_PATTERNS)}"
            )
            continue
        compiled.append(
            (f"[{cat}]", re.compile(BUILTIN_PATTERNS[cat], re.IGNORECASE), None)
        )

    for pat in raw_patterns:
        try:
            # Check if it's a valid regex; if not, escape it as a literal
            re.compile(pat)
            if whole_word:
                pat = rf"\b{re.escape(pat)}\b"
            compiled.append((pat, re.compile(pat, re.IGNORECASE), None))
        except re.error:
            escaped = re.escape(pat)
            compiled.append((pat, re.compile(escaped, re.IGNORECASE)))

    for value in barn_navn:
        compiled.append(
            (
                value,
                re.compile(re.escape(value), re.IGNORECASE),
                "[barnet]",
            )
        )

    for value in foraeldre_1:
        compiled.append(
            (value, re.compile(re.escape(value), re.IGNORECASE), "[forældre-1]")
        )

    for value in foraeldre_2:
        compiled.append(
            (value, re.compile(re.escape(value), re.IGNORECASE), "[forældre-2]")
        )

    return compiled


def _redact_pdf(
    config: RedactionConfig,
    pdf_path: Path,
    patterns: list[tuple[str, re.Pattern]],
    out_path: Path,
) -> dict:
    result = {
        "file": pdf_path.name,
        "pages": 0,
        "redactions": 0,
        "error": "",
    }

    try:
        with fitz.open(pdf_path) as doc:
            result["pages"] = len(doc)

            for page in doc:
                page_text = page.get_text()
                page_redact = 0

                for label, pattern, replacement in patterns:
                    matched_values = {
                        match.group(2)
                        if match.lastindex and match.lastindex >= 2
                        else match.group()
                        for match in pattern.finditer(page_text)
                    }

                    for matched_text in matched_values:
                        # Search for all instances of the matched text on the page
                        areas = page.search_for(matched_text, quads=False)

                        for rect in areas:
                            if replacement is None:
                                page.add_redact_annot(
                                    rect,
                                    fill=config.redact_color,
                                    align=fitz.TEXT_ALIGN_CENTER,
                                )
                            else:
                                page.add_redact_annot(
                                    rect,
                                    text=replacement,
                                    fill=config.redact_color,
                                    text_color=config.text_color,
                                    fontname=config.fontname,
                                    fontsize=config.fontsize,
                                    align=fitz.TEXT_ALIGN_CENTER,
                                )

                            page_redact += 1

                if page_redact > 0:
                    page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)
                    result["redactions"] += page_redact

            out_path.parent.mkdir(parents=True, exist_ok=True)
            doc.save(out_path, garbage=4, deflate=True, clean=True)
            doc.close()

    except Exception as e:
        result["error"] = str(e)

    return result
