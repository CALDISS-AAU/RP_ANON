# Externals
from pathlib import Path
import subprocess

# Functions


def searchable_pdf(
    input_path: Path, output_dir: Path, file_suffix: str, language: str = "dan"
) -> Path:
    """
    Function for turning scanned image pdf's into searchable pdf's.

    parameters:
    input_file : .pdf
    output_file: .pdf
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    output_name = f"{input_path.stem}{file_suffix}{input_path.suffix}"
    output_path = output_dir / output_name
    
    
    command = [
        "ocrmypdf",
        str(input_path),
        str(output_path),
        "--language",
        language,
        "--deskew",
        "--rotate-pages",
        "--skip-text",
    ]
    try:
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
        )
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print("Return code:", e.returncode)
        print("STDOUT:")
        print(e.stdout)
        print("STDERR:")
        print(e.stderr)
        raise

    subprocess.run(command, check=True, capture_output=True, text=True)
    return output_path
