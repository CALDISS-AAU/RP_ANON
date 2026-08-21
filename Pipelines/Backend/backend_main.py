"""
backend_main.py
Automaticaclly ocr scan pdf files & Permanently redact text matching patterns from PDF files.

Dependencies: pymupdf, tesseract-ocr, tesseract-ocr-da
Install:      sudo apt update
              sudo apt install tesseract-ocr
              sudo apt install tesseract-ocr-dan
Install:      pip install pymupdf
              pip install ocrmypdf

Usage:
    python backend_main.py --input document.pdf --patterns "John Smith" "ACC-\d+"
    python backend_main.py --input document.pdf --categories email phone
    python backend_main.py --input ./pdfs --patterns "CONFIDENTIAL-\d+" --categories email

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
import sys
from pathlib import Path

# Internal
from Pipelines.Backend.Functions.ocr_func import searchable_pdf
from Pipelines.Backend.Functions.redaction_func import (
    _build_patterns,
    _redact_pdf,
    BUILTIN_PATTERNS,
    RedactionConfig,
)

config = RedactionConfig()


def main(
    pdf_path,
    output_dir,
    barn_navn,
    foraeldre_1,
    foraeldre_2,
    patterns,
    categories = ['cpr', 'case-num', 'case-id', 'address']
):
    parser = argparse.ArgumentParser(
        description="Permanently redact text from PDF files."
    )
    parser.add_argument("--input", required=True, help="PDF file or folder of PDFs")
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

    parser.add_argument("--language", default="dan", help="Language of input file")

    args = parser.parse_args()

    arguments = [
        args.patterns,
        args.categories,
        args.barn_navn,
        args.foraeldre_1,
        args.foraeldre_2,
    ]
    if not any(arguments):
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
        raw_patterns=args.patterns or [],
        categories=args.categories or [],
        whole_word=args.whole_word,
        barn_navn=args.barn_navn or [],
        foraeldre_1=args.foraeldre_1 or [],
        foraeldre_2=args.foraeldre_2 or [],
    )

    print(f"Patterns  : {[label for label, _, _ in patterns]}")
    print(f"Files     : {len(pdfs)}\n")
    print("NOTE: Verify all output files before distributing.\n")

    for pdf_path in pdfs:
        ocr_path = searchable_pdf(
            input_path=pdf_path,
            language=args.language,
        )

        out_path = out_dir / f"{pdf_path.stem}_redacted.pdf"

        result = _redact_pdf(
            config=config,
            pdf_path=ocr_path,
            out_path=out_path,
            patterns=patterns,
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
