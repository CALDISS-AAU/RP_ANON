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

from pathlib import Path
import tempfile

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
    input_path,
    output_dir,
    barn_navn,
    foraeldre_1,
    foraeldre_2,
    patterns,
    categories =None,
	language='dan',
	whole_word=False
):
    if categories is None:
        categories = ["cpr", "case-num", "case-id", "address"]
    
    arguments = [
        patterns,
        categories,
        barn_navn,
		foraeldre_1,
        foraeldre_2,
    ]
    if not any(arguments):

        raise ValueError(
            "[ERROR] No redaction or replacement values were provided."
        )

    src = Path(input_path)
    if not src.exists():
        sys.exit(f"[ERROR] Not found: {src}")

    pdfs = sorted(src.glob("*.pdf")) if src.is_dir() else [src]
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    compiled_patterns = _build_patterns(
        raw_patterns=patterns or [],
        categories=categories or [],
        whole_word=whole_word,
        barn_navn=barn_navn or [],
        foraeldre_1=foraeldre_1 or [],
        foraeldre_2=foraeldre_2 or [],
    )

    print(f"Patterns  : {[label for label, _, _ in compiled_patterns]}")
    print(f"Files     : {len(pdfs)}\n")
    print("NOTE: Verify all output files before distributing.\n")

    for pdf_path in pdfs:
        with tempfile.TemporaryDirectory() as temp_dir:

            ocr_path = searchable_pdf(
                input_path=pdf_path,
                output_dir=Path(temp_dir),
                language=language,
            )

            out_path = out_dir / f"{pdf_path.stem}_redacted.pdf"

            result = _redact_pdf(
                config=config,
                pdf_path=ocr_path,
                out_path=out_path,
                patterns=compiled_patterns,
            )

        if result["error"]:
            print(f"  ✗ {pdf_path.name:50s} ERROR — {result['error']}")
        else:
            print(
                f"  ✓ {pdf_path.name:50s} {result['redactions']:>4} redaction(s)  →  {out_path.name}"
            )

    print(f"Output dir    : {out_dir.resolve()}")

if __name__ == "__main__":
    try:
        main()
 
    except Exception as exc:
        print(
            "\n"
            "========================================\n"
            "PROGRAM STOPPED WITH AN ERROR\n"
            "========================================\n"
            f"{type(exc).__name__}: {exc}\n",
            flush=True,
        )
 
        traceback.print_exc()
 
        sys.exit(1)
