"""Extract and validate arguments from the frontend."""

## IMPORTS ##
from argparse import Namespace
from pathlib import Path
## _______ ##


## HELPER FUNCTIONS ##
def _validate_input_path(input_path: str) -> Path:
    """Validate that the selected input file is a PDF."""

    print(f"1. Modtaget input_path: {input_path}", flush=True)

    path = Path(input_path)

    print(f"2. Path objekt oprettet: {path}", flush=True)

    print("3. Tjekker om filen eksisterer...", flush=True)
    is_file = path.is_file()
    print(f"4. is_file = {is_file}", flush=True)

    if not is_file:
        raise ValueError(
            "Den valgte input fil findes ikke. "
            "Gå tilbage og vælg en ny fil"
        )

    print(f"5. Filendelse: {path.suffix}", flush=True)

    if path.suffix.lower() != ".pdf":
        raise ValueError(
            "Den valgte input fil er ikke en PDF. "
            "Gå tilbage og vælg en ny fil"
        )

    print("6. Inputfil valideret", flush=True)

    return path


## MAIN FUNCTIONALITY ##
def extract_and_validate(args: Namespace):
    """Extract and validate values supplied through the GUI."""

    print("Starter extract_and_validate", flush=True)

    print("7. Læser args.input_path", flush=True)
    raw_input_path = args.input_path
    print(f"8. raw_input_path = {raw_input_path!r}", flush=True)

    input_path = _validate_input_path(raw_input_path)

    print("extract_and_validate færdig", flush=True)

    return input_path