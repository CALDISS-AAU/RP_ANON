# Externals
from pathlib import Path
import subprocess

# Functions


def searchable_pdf(
    input_path: Path, output_dir: Path, file_suffix: str, language: str = "dan"
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)

    output_name = f"{input_path.stem}{file_suffix}{input_path.suffix}"
    output_path = output_dir / output_name
    """
    Function for turning scanned image pdf's into searchable pdf's.

    parameters:
    input_file : .pdf
    output_file: .pdf
    """

    command = [
        "ocrmypdf",
        str(input_path),
        str(output_dir),
        "--language",
        language,
        "--deskew",
        "--rotate-pages",
        "--skip-text",
    ]

    subprocess.run(command, check=True, capture_output=True, text=True)
    return output_path
