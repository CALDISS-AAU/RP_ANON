# Backend README
PDF OCR and Redaction Tools for the CALDISS RP_ANON project.

This project contains two small command-line tools for working with PDF documents:

OCR: turns scanned PDFs into searchable PDFs.

Redaction: permanently removes text that matches selected patterns, such as email addresses, phone numbers, CPR numbers, case numbers, or custom values.

The tools can be used separately or as two steps in the same workflow. For scanned documents, run OCR first so the redaction tool can search the document text reliably.

Important: Automated redaction is not a substitute for a manual review. Always inspect the finished PDF before sharing or distributing it.

Project structure:
.
├── Output
├── Pipelines
│   ├── Backend
│   │   ├── Data
│   │   │   ├── ocr_scanned # Output folder for OCR
│   │   │   └── output
│   │   │       └── redacted # Output folder for redactor
│   │   ├── Functions
│   │   │   ├── ocr_func.py # OCR implementation
│   │   │   ├── pdf_redactor.py # Original script forked from Github - please advise this script for original purpose and functionality inspiration
│   │   │   └── redaction_func.py # Pattern matching and PDF redaction logic
│   │   ├── Logs
│   │   ├── Tests
│   │   ├── __pycache__
│   │   │   └── main_pdf_redactor.cpython-312.pyc
│   │   ├── backend_README.md
│   │   ├── main-ocr.py # Command-line entry point for OCR
│   │   └── main_pdf_redactor.py # Command-line entry point for redaction
├── README.md
├── Shared_Functions
│   ├── Pipeline_Functions
│   │   ├── pipeline_generator.py
│   │   └── wipe_pipeline_data.py
│   ├── __init__.py
│   └── logger_functionality.py
├── __pycache__
│   └── main.cpython-312.pyc
├── pyproject.toml
└── uv.lock

In the wider project, the function modules are imported from:

Pipelines/Backend/Functions/

If you move the scripts, update the imports or preserve this package structure.

## Requirements

Python 3.10 or newer

OCRmyPDF for OCR processing

PyMuPDF for PDF redaction

The required OCR language data, such as Danish (dan)

Install the Python dependency with:

pip install pymupdf

OCRmyPDF may require additional system packages depending on your operating system. Confirm that it is available by running:

ocrmypdf --version

If the project uses uv, dependencies can instead be installed and commands run through the existing uv environment.

OCR: make a scanned PDF searchable

The OCR command passes the document to OCRmyPDF with deskewing, automatic page rotation, and detection of pages that already contain text.

### Basic usage
```bash
python main-ocr.py \
  --input path/to/document.pdf \
  --output-dir path/to/output
```

The default output suffix is _ocr, so a file named document.pdf becomes:

path/to/output/document_ocr.pdf

## OCR options

Argument

Purpose

--input PATH

Source PDF. Required.

--output-dir DIR

Output directory. Required.

--language CODE

OCR language; defaults to dan.

--suffix TEXT

Output filename suffix; defaults to _ocr.

### Examples

Process a Danish document:
```bash
python main-ocr.py \
  --input documents/scanned-letter.pdf \
  --output-dir documents/ocr
```

Process an English document:
```bash
python main-ocr.py \
  --input documents/scanned-letter.pdf \
  --output-dir documents/ocr \
  --language eng
```

Use a custom filename suffix:

```bash
python main-ocr.py \
  --input documents/scanned-letter.pdf \
  --output-dir documents/ocr \
  --suffix _searchable
```
## Redaction: permanently remove matching text

The redaction tool searches the text layer of a PDF and adds permanent redaction annotations over every match. It can process one PDF or every PDF in a directory.

By default, redacted files are written to:

Pipelines/Backend/Data/output/redacted

Each output file receives the suffix _redacted.

Basic usage

Redact an exact name or a regular expression:
```bash
python main_pdf_redactor.py \
  --input document.pdf \
  --patterns "John Smith" "ACC-\\d+"
```

Use built-in categories:
```bash
python main_pdf_redactor.py \
  --input document.pdf \
  --categories email phone
```

Combine custom patterns and built-in categories:

```bash
python main_pdf_redactor.py \
  --input ./documents \
  --patterns "CONFIDENTIAL-\\d+" \
  --categories email cpr
```

### Redaction options

--input PATH

PDF file or directory of PDFs.

--output-dir DIR

Output directory; defaults to the project's redaction folder.

--patterns VALUE ...

Exact strings or regular expressions to redact.

--categories NAME ...

Built-in pattern groups such as email, phone, or cpr.

--replacement TEXT

Writes visible replacement text; otherwise matches are blacked out.

--whole-word

Limits supplied string patterns to whole-word matches.

Provide at least one --patterns or --categories value.

### Built-in categories

email, phone, cpr, credit, postcode, date, case-id, case-num, and address.

The project-specific patterns cover case identifiers, values following Sagsnr: or Sagsnr., and a basic Danish address format.

These patterns are intentionally broad in some places. They may miss unusual formats or match text that is not sensitive. Review the result carefully.

A basic Danish-style address pattern.
These are also possible to catch with inserting a direct pattern instead of category.

These patterns are intentionally broad in some places. They may miss unusual formats or match text that is not sensitive. Review the result carefully.

### More examples

Redact whole-word occurrences of a name:
```bash
python main_pdf_redactor.py \
  --input document.pdf \
  --patterns "Anna Jensen" \
  --whole-word
```
Replace matches with visible text instead of an empty black box:
```bash
python main_pdf_redactor.py \
  --input document.pdf \
  --categories email \
  --replacement "REDACTED"
```
Process every PDF in a directory and choose the output directory:
```
python main_pdf_redactor.py \
  --input documents/incoming \
  --output-dir documents/redacted \
  --categories email phone cpr
```

#### Recommended workflow

For image-based or scanned PDFs, use the following order:

Run OCR to create a searchable text layer.

Run redaction on the OCR output.

Open the redacted PDF and inspect every page.

Search the finished PDF for the sensitive values you expected to remove.

Share only the verified output file.

Example:
```bash
python main-ocr.py \
  --input documents/source.pdf \
  --output-dir documents/ocr

python main_pdf_redactor.py \
  --input documents/ocr/source_ocr.pdf \
  --output-dir documents/redacted \
  --categories email phone cpr
```
Custom patterns and regular expressions

Values passed to --patterns are interpreted as regular expressions when they are valid regex syntax. This is useful for identifiers that follow a predictable format.

For example:
```
python main_pdf_redactor.py \
  --input document.pdf \
  --patterns "CASE-[0-9]{6}"
```
When entering regular expressions in a shell, quoting the pattern helps prevent the shell from interpreting special characters.

Be careful with broad expressions. A pattern such as \\d+ would match almost every number in a document.

## Safety and limitations

Redaction depends on text extraction. Image-only PDFs should be OCR-processed first.

OCR errors can cause sensitive information to be missed. Please review the results carefully and the patterns you intend to redact.

PDF text may be split into fragments, which can prevent an otherwise correct pattern from matching. Look out for line-splits, spaces and other page formatting in all cases.

Built-in patterns do not cover every possible format.

A successful command does not guarantee that every sensitive value was removed.

Work on copies of source documents and keep originals unchanged.

Never distribute output before carrying out a visual and text-search review.

## Troubleshooting

ocrmypdf is not found

OCRmyPDF is either not installed or not available on your system path. Install it using the method recommended for your operating system, then confirm that ocrmypdf --version works.

The OCR language is unavailable

Install the relevant Tesseract language data or choose an installed language code with --language.

Install:

```bash
sudo apt update
sudo apt install tesseract-ocr-dan
```

Review the available language by:

```bash
tesseract --list-langs
```

No text is redacted

Check that:

the PDF contains searchable text;

the spelling and capitalization are correct;

the regular expression matches the extracted text;

the selected category fits the actual document format.

Pattern matching is case-insensitive, but spacing and punctuation can still affect a match.

Too much text is redacted

Narrow the regular expression, use a more specific exact value, or test the command on a single copied PDF before processing a full directory.

## Development notes

The command-line scripts are deliberately thin:

main-ocr.py parses OCR arguments and calls searchable_pdf().

ocr_func.py builds and runs the OCRmyPDF command.

main_pdf_redactor.py validates command-line input and processes one or more PDFs.

redaction_func.py defines the built-in patterns, compiles custom patterns, and applies permanent redactions with PyMuPDF.

When adding a new built-in redaction category, add its regular expression to BUILTIN_PATTERNS in redaction_func.py. It will then become available automatically through the --categories argument.