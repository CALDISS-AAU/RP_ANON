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

import argparse
import re
import sys
from pathlib import Path
from dataclasses import dataclass

import fitz  # pymupdf

# Internal
from Pipelines.Backend.Functions.redaction_func import (
    _build_patterns,
    _redact_pdf,
    BUILTIN_PATTERNS,
    RedactionConfig,
)

config = RedactionConfig()


def main():
    parser = argparse.ArgumentParser(
        description="Permanently redact text from PDF files."
    )
    parser.add_argument("--input", help="PDF file or folder of PDFs")
    parser.add_argument("--output-dir", default=config.output_dir)

    parser.add_argument(
        "--patterns",
        nargs="*",
        default=[],
        help="Regex patterns or exact strings to redact",
    )
    parser.add_argument(
        "--categories",
        nargs="*",
        default=[],
        choices=list(BUILTIN_PATTERNS.keys()),
        help="Built-in pattern categories",
    )

    parser.add_argument(
        "--replacement",
        default=None,
        help="Text inserted in place of each match. Omit for normal redaction.",
    )

    parser.add_argument(
        "--whole-word",
        action="store_true",
        help="Match whole words only for string patterns",
    )

    parser.add_argument(
        "--barn-navn",
        nargs="*",
        default=[],
        help="Patterns/values that should be replaced with [barnet]",
    )

    parser.add_argument(
        "--foraeldre-1",
        nargs="*",
        default=[],
        help="Patterns/values that should be replaced with [forældre-1]",
    )

    parser.add_argument(
        "--foraeldre-2",
        nargs="*",
        default=[],
        help="Patterns/values that should be replaced with [forældre-2]",
    )

    args = parser.parse_args()

    if not args.patterns and not args.categories:
        sys.exit(
            "[ERROR] Specify at least one --patterns value or --categories option."
        )

    src = Path(args.input)
    if not src.exists():
        sys.exit(f"[ERROR] Not found: {src}")

    pdfs = sorted(src.glob("*.pdf")) if src.is_dir() else [src]
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    patterns = _build_patterns(
        args.patterns or [], args.categories or [], args.whole_word
    )
    print(f"Patterns  : {[label for label, _ in patterns]}")
    print(f"Files     : {len(pdfs)}\n")
    print("NOTE: Verify all output files before distributing.\n")

    for pdf_path in pdfs:
        out_path = out_dir / f"{pdf_path.stem}_redacted.pdf"
        result = _redact_pdf(
            config=config,
            pdf_path=pdf_path,
            out_path=out_path,
            patterns=patterns,
            replacement=args.replacement,
        )

        if result["error"]:
            print(f"  ✗ {pdf_path.name:50s} ERROR — {result['error']}")
        else:
            print(
                f"  ✓ {pdf_path.name:50s} {result['redactions']:>4} redaction(s)  →  {out_path.name}"
            )

    print(f"Output dir    : {out_dir.resolve()}")


if __name__ == "__main__":
    main()
