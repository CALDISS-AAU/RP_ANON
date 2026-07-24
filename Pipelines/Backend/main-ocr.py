"""This is the main script of the ANON-project.
This script is reserved for calling and combining pipelines from the
Pipelines/ folders.
For a description of the overall functionality of the individual
pipelines, please consult their respective Pipelines/README.md.

To run this script, please use this command in the terminal,
from the project root:
    uv run python -m main
"""

## IMPORTS ##
from pathlib import Path
import argparse

# Pipeline mains
from Pipelines.Backend.Functions.ocr_func import searchable_pdf
## _______ ##


## MAIN FUNCTION ##
def main():
    parser = argparse.ArgumentParser(description="OCR treament of documents")
    parser.add_argument("--input", required=True, type=Path, help="Path to input pdf")
    parser.add_argument(
        "--output-dir", required=True, type=Path, help="Path to output file"
    )
    parser.add_argument("--language", default="dan", help="Language of input file")
    parser.add_argument(
        "--suffix", default="_ocr", help="Standard suffix for output file"
    )

    args = parser.parse_args()

    searchable_pdf(
        input_path=args.input,
        output_dir=args.output_dir,
        file_suffix=args.suffix,
        language=args.language,
    )


## _____________ ##

## CALL OF MAIN FUNCTION ##
if __name__ == "__main__":
    main()
