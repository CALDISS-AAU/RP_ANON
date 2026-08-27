# Anon Repository
#### CALDISS PDF Anonymisation Tool

A desktop application for automatically identifying and anonymising sensitive information in PDF documents.

The application is developed as part of the **CALDISS ANON project** and is designed primarily for Danish case documents. It combines a graphical user interface with OCR and PDF redaction to provide a single workflow for processing both digitally generated and scanned PDFs.

> **Important:** Automated anonymisation should always be followed by manual verification. OCR and pattern matching can miss information or produce false positives. **Never distribute an anonymised document without reviewing the output first.**

---

## Table of Contents

- [Overview](#overview)
- [How It Works](#how-it-works)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [Using the GUI](#using-the-gui)
- [Anonymisation and Redaction](#anonymisation-and-redaction)
- [OCR](#ocr)
- [Project Structure](#project-structure)
- [Architecture](#architecture)
- [Command-Line Tools](#command-line-tools)
- [Pipeline Utilities](#pipeline-utilities)
- [Building the Windows Application](#building-the-windows-application)
- [Development](#development)
- [Safety and Limitations](#safety-and-limitations)
- [Troubleshooting](#troubleshooting)

---

## Overview

The application takes a PDF document, makes its text searchable using OCR when necessary, identifies sensitive information, and permanently redacts matching text.

The primary application flow is:

```text
PDF
 │
 ▼
Graphical user interface
 │
 │  File paths + identifiers to anonymise
 ▼
Input validation
 │
 ▼
OCR
 │
 │  Searchable PDF
 ▼
Pattern construction
 │
 ▼
PDF text matching
 │
 ▼
Permanent redaction
 │
 ▼
*_redacted.pdf
 │
 ▼
Manual verification
```

The GUI is intended to make the anonymisation workflow accessible without requiring users to construct regular expressions or work directly with command-line tools.

The backend can also be used independently by developers.

---

## How it Works

The top-level entry point is `main.py`.

When the application starts, it:

1. Configures the Tesseract environment.
2. Opens the graphical frontend.
3. Collects and validates the user's input.
4. Passes the validated values to the backend.
5. OCR-processes the selected PDF.
6. Builds the required redaction patterns.
7. Searches the PDF text for matches.
8. Applies permanent PDF redactions.
9. Writes a new `_redacted.pdf` file to the selected output directory.

The original PDF is not intentionally modified by this workflow.

### Main application flow

```text
main.py
 │
 ├── configure_tesseract_path()
 │
 ├── Pipelines.Frontend.frontend_main
 │      │
 │      ├── build_GUI()
 │      ├── parse user input
 │      ├── extract_and_validate()
 │      └── confirm validation warnings
 │
 └── Pipelines.Backend.backend_main
        │
        ├── searchable_pdf()
        │      └── OCRmyPDF + Tesseract
        │
        ├── _build_patterns()
        │
        └── _redact_pdf()
               └── PyMuPDF
```

---

## Features

### Graphical interface

The application provides a Danish-language GUI built with **Gooey** and **wxPython**.

Users can:

- select a PDF using a file browser;
- select an existing output directory;
- enter variants of the child's name;
- enter variants of one or two parents' names;
- enter additional values that should be anonymised;
- review warnings for values that do not follow the expected format before processing.

### OCR

PDFs are processed through **OCRmyPDF** using **Tesseract**.

OCR processing enables the backend to search text in scanned or image-based PDFs and includes:

- Danish OCR by default;
- deskewing;
- automatic page rotation;
- preservation of pages that already contain searchable text.

### Permanent PDF redaction

Redactions are applied using **PyMuPDF**.

The backend:

1. extracts page text;
2. matches configured regular expressions;
3. locates matching text on the PDF page;
4. creates redaction annotations;
5. applies those annotations;
6. saves a cleaned and compressed output PDF.

This is actual PDF redaction rather than simply drawing a visual rectangle over the original text.

### Named-person replacement

Names entered through the GUI receive role-specific replacement labels:

| GUI field | Replacement |
| --- | --- |
| Child | `[barnet]` |
| Parent 1 | `[forældre-1]` |
| Parent 2 | `[forældre-2]` |

This makes it possible to retain some semantic information about the people referenced in a document while removing their identifying names.

### Additional identifiers

The GUI also accepts additional semicolon-separated identifiers.

These can be used for information such as:

- other people's names;
- schools;
- organisations;
- dates or identifiers;
- other case-specific sensitive values.

### Built-in pattern categories

The backend defines reusable pattern categories for:

| Category | Intended match |
| --- | --- |
| `email` | Email addresses |
| `phone` | Phone numbers |
| `cpr` | Danish CPR numbers |
| `credit` | Credit card-like numbers |
| `postcode` | UK-style postcodes |
| `date` | Common numeric date formats |
| `case-id` | Project-specific case identifiers |
| `case-num` | Values associated with `Sagsnr` |
| `address` | Danish-style addresses |

The integrated application currently defaults to:

```text
cpr
case-num
case-id
address
```

Additional patterns supplied through the GUI are added to these defaults.

---

## Requirements

### Python

The project configuration requires:

```text
Python >= 3.12
```

### Python dependencies

The project's `pyproject.toml` defines the following dependencies:

```text
gooey >= 1.0.8.1
ocrmypdf >= 17.10.0
pymupdf >= 1.28.2
pytesseract >= 0.3.13
six >= 1.17.0
ruff >= 0.15.22
tesseract >= 0.1.3
```

### System dependencies

OCR additionally depends on **Tesseract OCR** and the appropriate language data.

For Danish documents, the `dan` Tesseract language must be available.

On Debian/Ubuntu-based Linux systems this can typically be installed with:

```bash
sudo apt update
sudo apt install tesseract-ocr
sudo apt install tesseract-ocr-dan
```

Verify the installation with:

```bash
tesseract --version
tesseract --list-langs
```

`dan` should appear in the language list.

OCRmyPDF may require additional system dependencies depending on the operating system and installation method.

---

## Installation

The repository is designed to work with [`uv`](https://docs.astral.sh/uv/).

### 1. Clone the repository

```bash
git clone <repository-url>
cd <repository-directory>
```

### 2. Install `uv`

Follow the installation instructions for your operating system, or install it through Python where appropriate:

```bash
python -m pip install uv
```

### 3. Install project dependencies

From the repository root:

```bash
uv sync
```

### 4. Install the project in editable mode

Editable installation is useful during development and makes the repository's utility commands available:

```bash
uv pip install -e .
```

Alternatively, when working with a conventional virtual environment:

```bash
pip install -e .
```

This registers:

```text
create-pipeline
clear-pipeline
```

as command-line tools.

---

## Running the Application

Run the complete GUI application from the **repository root**:

```bash
uv run python -m main
```

Running from the project root is recommended because the project uses package imports such as:

```python
from Pipelines.Frontend.frontend_main import main as run_frontend
from Pipelines.Backend.backend_main import main as run_backend
```

The application will open the graphical interface.

---

## Using the GUI

The GUI is titled:

> **PDF-anonymiseringsværktøj**

and is intended for anonymisation of Danish case documents.

### 1. Select an input PDF

Under **Input**, select the PDF that should be anonymised.

The frontend validates that:

- the path exists;
- the selected path is a file;
- the filename has a `.pdf` extension.

### 2. Select the output directory

Under **Output**, select an existing directory in which the anonymised PDF should be stored.

The frontend verifies that the selected location exists and is a directory.

### 3. Enter names

Names are entered as semicolon-separated lists.

For example:

```text
Anna; Anna Hansen; Anna M. Hansen; A. M. Hansen
```

Provide **all variants that may occur in the source document**.

The GUI contains fields for:

- `Barnets navn`
- `Forældre 1's navn`
- `Forældre 2's navn`

The child and first-parent fields are required. The second-parent field is optional.

### 4. Enter additional sensitive values

The **Andet der skal anonymiseres** field can contain additional values, also separated by semicolons.

For example:

```text
Eksempelskolen; Eksempel Kommune; ABC-12345
```

### 5. Review warnings

The frontend checks whether supplied names and additional values follow expected formats.

Unexpected input does not necessarily mean the value is invalid. Instead, the application presents a warning dialog.

You can then choose either:

- **Fortsæt** — continue with the supplied values; or
- **Gå tilbage** — return and correct the input.

### 6. Process the document

After validation, the values are passed to the backend.

The resulting file is written as:

```text
<original_filename>_redacted.pdf
```

For example:

```text
case-document.pdf
```

becomes:

```text
case-document_redacted.pdf
```

### 7. Verify the result

This step is mandatory for safe use.

Open the resulting PDF and inspect the entire document before sharing it.

See [Safety and Limitations](#safety-and-limitations) for details.

---

## Anonymisation and Redaction

### Pattern construction

The central pattern-building logic lives in:

```text
Pipelines/Backend/Functions/redaction_func.py
```

`_build_patterns()` combines:

- built-in pattern categories;
- custom patterns;
- child-name variants;
- parent-name variants.

Matching is performed using Python regular expressions with `re.IGNORECASE`.

Name replacements supplied through the dedicated child/parent fields are escaped with `re.escape()` before compilation. This means these values are treated as literal strings rather than arbitrary regular expressions.

### Custom patterns

Values supplied as raw patterns can be interpreted as regular expressions.

For example:

```text
CASE-[0-9]{6}
```

could match:

```text!
CASE-123456
```

Be careful when introducing broad regular expressions.

For example:

```regex
\d+
```

matches almost every sequence of digits and would likely redact substantially more information than intended.

### Applying redactions

For each PDF page, the backend:

```text
Extract text
    ↓
Run each regular expression
    ↓
Collect matching strings
    ↓
Locate each string using PyMuPDF page.search_for()
    ↓
Add redaction annotations
    ↓
Apply redactions
```

The resulting document is saved using PyMuPDF with garbage collection, compression, and document cleanup enabled.

---

## OCR

OCR functionality is implemented in:

```text
Pipelines/Backend/Functions/ocr_func.py
```

The core function is:

```python
searchable_pdf(input_path, output_dir, language="dan")
```

Internally, OCRmyPDF is configured approximately as follows:

```python
ocrmypdf.ocr(
    input_path,
    output_path,
    language=[language],
    deskew=True,
    rotate_pages=True,
    skip_text=True,
    ocr_engine="tesseract",
)
```

### Why OCR is required

The redaction backend operates on extracted PDF text.

A scanned document may contain nothing more than page images. Visually, it contains text, but the PDF itself may have no searchable text layer.

OCR creates that text layer so the redaction system can find sensitive values.

### Temporary OCR output

In the integrated backend, OCR output is generated inside a temporary directory:

```text
Original PDF
    ↓
TemporaryDirectory
    ↓
OCR PDF
    ↓
Redaction
    ↓
Final output
```

The temporary directory is automatically removed after each document has been processed.

---

## Project Structure

The repository follows a pipeline-oriented structure:

```text
.
├── README.md
├── main.py
├── pyproject.toml
├── Output/
│   └── .gitkeep
│
├── Pipelines/
│   ├── Backend/
│   │   ├── backend_main.py
│   │   ├── backend_README.md
│   │   ├── main-ocr.py
│   │   ├── main_pdf_redactor.py
│   │   ├── run_redactor.sh
│   │   │
│   │   ├── Data/
│   │   ├── Functions/
│   │   │   ├── ocr_func.py
│   │   │   ├── pdf_redactor.py
│   │   │   └── redaction_func.py
│   │   ├── Logs/
│   │   └── Tests/
│   │
│   ├── Frontend/
│   │   ├── frontend_main.py
│   │   ├── frontend_README.md
│   │   │
│   │   ├── Data/
│   │   ├── Functions/
│   │   │   ├── build_GUI.py
│   │   │   ├── example_functions_script.py
│   │   │   └── extract_and_validate.py
│   │   ├── Logs/
│   │   └── Tests/
│   │
│   └── Example_Pipeline/
│       ├── example_pipeline_main.py
│       ├── example_pipeline_README.md
│       ├── Data/
│       ├── Functions/
│       ├── Logs/
│       └── Tests/
│
├── Shared_Functions/
│   ├── __init__.py
│   ├── logger_functionality.py
│   └── Pipeline_Functions/
│       ├── pipeline_generator.py
│       └── wipe_pipeline_data.py
│
└── .github/
    └── workflows/
        └── build-app.yml
```

### Directory responsibilities

#### `Pipelines/Frontend/`

Contains the graphical interface and input-validation logic.

Important files:

- `frontend_main.py` — starts the Gooey frontend and handles warning dialogs;
- `Functions/build_GUI.py` — defines GUI fields and groups;
- `Functions/extract_and_validate.py` — normalises and validates user input.

#### `Pipelines/Backend/`

Contains OCR and PDF-redaction functionality.

Important files:

- `backend_main.py` — coordinates OCR and redaction;
- `Functions/ocr_func.py` — creates searchable PDFs;
- `Functions/redaction_func.py` — defines patterns and applies redactions;
- `main_pdf_redactor.py` — standalone redaction CLI.

#### `Shared_Functions/`

Contains functionality intended for reuse across pipelines.

Currently this includes:

- logging utilities;
- pipeline generation;
- pipeline data/log cleanup.

#### `Pipelines/Example_Pipeline/`

A template/example showing the expected pipeline organisation and logging approach.

---

## Architecture

The application separates frontend concerns from document-processing logic.

### Frontend

```text
Pipelines/Frontend/
```

Responsibilities:

- displaying the GUI;
- collecting paths and identifiers;
- validating input;
- presenting warnings;
- returning normalised backend arguments.

The frontend does **not** perform OCR or modify PDFs directly.

### Backend

```text
Pipelines/Backend/
```

Responsibilities:

- OCR processing;
- constructing patterns;
- searching PDF text;
- applying redactions;
- saving final documents.

### Shared functionality

```text
Shared_Functions/
```

contains functionality that is not specific to either frontend or backend.
Otherwise functionality that goes across pipelines and used in different contexts. Currently none exists in this repo.

This separation makes it possible to reuse backend functionality from other interfaces or pipelines without depending on the GUI.

---

## Command-Line Tools

The repository contains lower-level scripts that can be useful during development and debugging.

### Standalone PDF redactor

The redaction CLI is located at:

```text
Pipelines/Backend/main_pdf_redactor.py
```

Example:

```bash
uv run python -m Pipelines.Backend.main_pdf_redactor \
    --input document.pdf \
    --patterns "John Smith" "ACC-\d+"
```

Using built-in categories:

```bash
uv run python -m Pipelines.Backend.main_pdf_redactor \
    --input document.pdf \
    --categories email phone cpr
```

Processing a directory:

```bash
uv run python -m Pipelines.Backend.main_pdf_redactor \
    --input ./documents \
    --output-dir ./redacted \
    --categories email phone cpr
```

Available options in the standalone redactor include:

```text
--input
--output-dir
--patterns
--categories
--replacement
--whole-word
--barn-navn
--foraeldre-1
--foraeldre-2
```

> **Development note:** The standalone scripts and the integrated backend have evolved separately. Treat `main.py` together with `backend_main.py` as the primary application path, and verify standalone CLI behaviour against the current backend implementation before relying on it in production workflows.

---

## Pipeline Utilities

The repository contains utilities for maintaining the pipeline-based project structure.

They are registered through `pyproject.toml` as:

```text
create-pipeline
clear-pipeline
```

Install the repository in editable mode before using them:

```bash
uv pip install -e .
```

### Creating a pipeline

Run:

```bash
create-pipeline <pipeline name>
```

For example:

```bash
create-pipeline data cleaning
```

This creates:

```text
Pipelines/
└── Data_Cleaning/
    ├── Data/
    │   └── .gitkeep
    ├── Functions/
    │   ├── .gitkeep
    │   └── example_functions_script.py
    ├── Logs/
    │   └── .gitkeep
    ├── Tests/
    │   └── .gitkeep
    ├── data_cleaning_main.py
    └── data_cleaning_README.md
```

Pipeline names are normalised automatically.

For example:

```text
data cleaning
```

becomes:

```text
Data_Cleaning
```

for the directory and:

```text
data_cleaning
```

for filenames.

The generator locates the repository root by searching upward from the current working directory for `pyproject.toml`. As a result, it can be invoked from subdirectories within the project after installation.

#### Optional modelling directory

The generator supports an optional `model` folder group:

```bash
create-pipeline my pipeline --include model
```

This additionally creates:

```text
Modelling/
```

### Clearing pipeline data

Generated pipeline data and logs can be removed with:

```bash
clear-pipeline <pipeline name>
```

For example:

```bash
clear-pipeline data cleaning
```

The command clears:

```text
Pipelines/Data_Cleaning/Data/
Pipelines/Data_Cleaning/Logs/
```

while preserving:

- the directories themselves;
- their `.gitkeep` files.

This is useful for resetting generated intermediate files and logs without modifying pipeline source code.

> **Warning:** `clear-pipeline` deletes files and subdirectories inside the selected pipeline's `Data` and `Logs` directories. Verify the pipeline name before running it.

---

## Logging

Reusable logging functionality is provided by:

```text
Shared_Functions/logger_functionality.py
```

### `setup_logger()`

Creates a file logger for a pipeline step.

The function:

- creates the parent log directory when necessary;
- removes existing handlers from the named logger;
- supports overwriting or appending;
- writes simple message-only log entries.

Example:

```python
logger = setup_logger(
    output_dir_log="./Pipelines/My_Pipeline/Logs/step_1.log",
    logger_name="my_pipeline.step_1",
)
```

### `rebuild_pipeline_log()`

Combines multiple step logs into a single pipeline log.

For example:

```python
rebuild_pipeline_log(
    step_log_paths=[
        "./Pipelines/My_Pipeline/Logs/step_1.log",
        "./Pipelines/My_Pipeline/Logs/step_2.log",
    ],
    output_dir_log="./Pipelines/My_Pipeline/Logs/full_pipeline.log",
)
```

The combined log is rebuilt in the supplied order each time the function runs.

---

## Building the Windows Application

The repository contains a GitHub Actions workflow:

```text
.github/workflows/build-app.yml
```

The workflow is manually triggered with:

```yaml
workflow_dispatch:
```

and builds the application on:

```text
windows-latest
```

### Build process

The workflow:

1. checks out the repository;
2. installs Python 3.12;
3. installs `uv`;
4. synchronises project dependencies;
5. installs Tesseract OCR;
6. downloads Danish Tesseract language data;
7. installs PyInstaller;
8. builds the application;
9. bundles the Tesseract installation;
10. verifies that the application can be imported;
11. uploads the resulting application as a GitHub Actions artifact.

### PyInstaller output

The application is built as:

```text
CALDISS_Anonymiserings_program
```

using PyInstaller's `--onedir` and `--windowed` modes.

The output therefore contains an application directory rather than a single executable.

Conceptually:

```text
dist/
└── CALDISS_Anonymiserings_program/
    ├── CALDISS_Anonymiserings_program.exe
    ├── ...
    └── tools/
        └── tesseract/
            ├── tesseract.exe
            └── tessdata/
                └── dan.traineddata
```

The complete directory should be kept together when distributing the Windows build.

### Bundled Tesseract

The build workflow copies the Windows Tesseract installation into:

```text
tools/tesseract/
```

inside the application directory.

At runtime, `configure_tesseract_path()` detects a frozen application and adds this bundled Tesseract directory to `PATH`. It also configures `TESSDATA_PREFIX`.

This allows the packaged application to locate the OCR engine and Danish language data without relying solely on a separate user-configured Tesseract installation.

---

## Development

### Adding a built-in redaction category

Built-in categories are defined in:

```text
Pipelines/Backend/Functions/redaction_func.py
```

inside:

```python
BUILTIN_PATTERNS = {
    ...
}
```

Add a new key and regular expression to make another pattern category available to backend pattern construction.

For example:

```python
BUILTIN_PATTERNS = {
    ...
    "my-category": r"...",
}
```

When changing patterns, test them against both:

- documents that **should** match;
- documents that **should not** match.

Broad patterns are particularly dangerous in a redaction application because false positives permanently remove document content from the generated output.

### Adding frontend fields

GUI construction lives in:

```text
Pipelines/Frontend/Functions/build_GUI.py
```

Reusable helpers include:

```python
_add_browse_field(...)
_add_text_field(...)
```

If a new field needs backend processing, also update:

```text
Pipelines/Frontend/Functions/extract_and_validate.py
```

and the receiving arguments in:

```text
Pipelines/Backend/backend_main.py
```

### Input validation

Frontend validation currently covers:

- existence and type of the input PDF;
- existence of the output directory;
- required name fields;
- expected formatting of names;
- expected characters in additional identifiers.

Name validation understands ordinary capitalised name components, initials such as:

```text
B.
```

and hyphenated names such as:

```text
Anne-Sofie
```

Values outside the expected format generate warnings so that users can explicitly decide whether to proceed.

### Formatting and linting

`ruff` is included in the project dependencies.

It can be run with:

```bash
uv run ruff check .
```

Where appropriate, automatically fixable issues can be handled with:

```bash
uv run ruff check . --fix
```

---

## Safety and Limitations

This software handles document anonymisation, where false negatives can expose sensitive information. Automated output must therefore be treated as requiring verification.

### OCR is not perfect

Scanned PDFs depend on OCR accuracy.

OCR can misread:

- characters;
- names;
- numbers;
- punctuation;
- text with poor contrast;
- handwriting;
- rotated or damaged text;
- unusual fonts.

If OCR produces the wrong text, a correct redaction pattern may never see the sensitive value.

### PDF text structure can affect matching

Text that appears continuous visually may be represented internally as separate fragments.

For example, a name that visually appears as:

```text
Anna Hansen
```

might be split across lines or PDF text objects.

A regular expression expecting a single continuous string may therefore fail to match it.

### Patterns cannot cover every format

Built-in patterns represent expected formats, not every possible representation of sensitive information.

Documents may contain:

- unexpected punctuation;
- unusual whitespace;
- OCR mistakes;
- alternative number formats;
- abbreviations;
- spelling variations;
- names not entered by the user.

### Name variants must be comprehensive

Users should enter all known representations of each relevant name. Always test out the optimal way of typing out the desired patterns for names.

For example:

```text
Anna Marie Hansen
Anna Hansen
Anna M. Hansen
A. M. Hansen
Frk. Hansen
```

A name variant that is not represented by an entered value or another configured pattern may remain in the document.

### Pattern matching can over-redact

Regular expressions that are too broad may match legitimate document content.

Test new or unusual patterns on copied documents before using them on larger batches.

### A successful run is not proof of anonymisation

A successful program exit means the processing pipeline completed. It does **not** prove that every sensitive value was identified.

### Required verification workflow

Before distributing any processed document:

1. Open the generated `_redacted.pdf`.
2. Inspect every page visually.
3. Check that expected identifiers were removed or replaced.
4. Search the output PDF for the original sensitive values.
5. Look specifically for OCR errors and unusual formatting.
6. Confirm that non-sensitive information has not been incorrectly removed.
7. Share only the manually verified output.

Keep source documents unchanged and perform processing on copies whenever possible.

---

## Troubleshooting

### `tesseract` is not found

Check:

```bash
tesseract --version
```

If the command fails, install Tesseract or ensure its installation directory is available through `PATH`.

For packaged Windows builds, confirm that the application's `tools/tesseract/` directory exists and contains the Tesseract executable.

---

### Danish OCR is unavailable

Check installed languages:

```bash
tesseract --list-langs
```

The output should include:

```text
dan
```

On Debian/Ubuntu:

```bash
sudo apt install tesseract-ocr-dan
```

---

### OCRmyPDF is unavailable

Check:

```bash
uv run ocrmypdf --version
```

If it is missing, ensure project dependencies have been installed:

```bash
uv sync
```

OCRmyPDF can also depend on system-level software, so consult its platform-specific installation requirements if Python dependency installation succeeds but OCR still fails.

---

### No text is being anonymised

Check that:

- the PDF contains searchable text or OCR succeeds;
- all relevant name variants were supplied;
- the pattern matches the text as OCR extracted it;
- punctuation and whitespace are represented as expected;
- the relevant built-in category is enabled.

Inspecting the OCR-produced text is useful when a value appears visually correct but is not matched.

---

### Too much text is anonymised

A pattern is probably too broad.

Use:

- a more specific literal value;
- a narrower regular expression;
- a single copied PDF for testing.

Do not run an untested broad pattern across a collection of documents.

---

### The GUI rejects a path

The input path must:

- exist;
- point to a file;
- have a `.pdf` extension.

The output path must:

- already exist;
- be a directory.

---

### The GUI warns about a name

The name validator expects conventional capitalisation and supported name structures.

A warning does not automatically prevent processing. If the value is intentional, the user can choose **Fortsæt**.

If it is a typo or formatting mistake, choose **Gå tilbage** and correct it.

---

### Imports fail when running an individual file

Run modules from the repository root rather than changing into a pipeline directory.

For the complete application:

```bash
uv run python -m main
```

For a package module, prefer:

```bash
uv run python -m Pipelines.<Pipeline>.<module>
```

This keeps the repository root on Python's import path and preserves package imports.

---

## Development Status

The repository contains both the integrated GUI workflow and earlier or lower-level command-line tooling.

The primary application path is:

```text
main.py
    ↓
Frontend
    ↓
Validation
    ↓
Backend
    ↓
OCR
    ↓
Redaction
```

Some standalone scripts and pipeline README files reflect earlier development stages and may not expose exactly the same function signatures or behaviour as the integrated application.

When extending the project, use the implementation called by `main.py` as the authoritative reference and keep standalone tooling synchronised where it remains necessary.

---

## Responsible Use

PDF anonymisation is a high-consequence document-processing task.

This application should be considered an **anonymisation aid**, not an automatic guarantee that a document is safe to disclose.

The recommended operating principle is:

> **Automate detection and redaction; manually verify the result.**

Always retain an unchanged source document, review every generated output, and only distribute files that have passed manual verification.
