"""Extract and validate arguments from the frontend."""

## IMPORTS ##
from argparse import Namespace
from pathlib import Path
## _______ ##


## HELPER FUNCTIONS ##
def _validate_input_path(input_path: str) -> Path:
    """Validate that the selected input file is a PDF."""

    path = Path(input_path)

    if not path.is_file():
        raise ValueError(
            "Den valgte input fil findes ikke. "
            "Gå tilbage og vælg en ny fil"
        )

    if path.suffix.lower() != ".pdf":
        raise ValueError(
            "Den valgte input fil er ikke en PDF. "
            "Gå tilbage og vælg en ny fil"
        )

    return path
## ________________ ##


## MAIN FUNCTIONALITY ##
def extract_and_validate(args: Namespace):
    """Extract and validate values supplied through the GUI."""

    input_path = _validate_input_path(args.input_path)

    # More validation will follow...

    return input_path

    pass