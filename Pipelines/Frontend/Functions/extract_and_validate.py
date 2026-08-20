"""Extract and validate arguments from the frontend."""

## IMPORTS ##
from argparse import Namespace
from pathlib import Path
## _______ ##


## HELPER FUNCTIONS ##
def _validate_input_path(input_path: str) -> Path:
    """Validate that the selected input path exists and is a PDF file."""

    path = Path(input_path)

    if not path.is_file():
        raise ValueError(
            "Den valgte inputfil findes ikke. "
            "Gå tilbage og vælg en ny fil."
        )

    if path.suffix.lower() != ".pdf":
        raise ValueError(
            "Den valgte inputfil er ikke en PDF-fil. "
            "Gå tilbage og vælg en PDF-fil."
        )

    return path


def _validate_output_path(output_path: str) -> Path:
    """Validate that the selected output path exists and is a directory."""

    path = Path(output_path)

    if not path.is_dir():
        raise ValueError(
            "Den valgte outputmappe findes ikke eller er ikke en mappe. "
            "Gå tilbage og vælg en gyldig mappe."
        )

    return path


def _split_semicolon_list(value: str) -> list[str]:
    """Split a semicolon-separated field and remove empty entries."""

    return [
        item.strip()
        for item in value.split(";")
        if item.strip()
    ]


def _is_valid_name_part(part: str) -> bool:
    """Check whether one part of a name has the expected format."""

    # Initial, e.g. "B."
    if (
        len(part) == 2
        and part[0].isalpha()
        and part[0].isupper()
        and part[1] == "."
    ):
        return True

    # Hyphenated name, e.g. "Anne-Sofie"
    if "-" in part:
        sections = part.split("-")

        if any(not section for section in sections):
            return False

        return all(
            _is_valid_name_part(section)
            for section in sections
        )

    # Ordinary name, e.g. "Anna", "Hansen", "Østergaard"
    if not part.isalpha():
        return False

    if not part[0].isupper():
        return False

    return True


def _is_expected_name(name: str) -> bool:
    """Check whether a complete name entry follows the expected format."""

    parts = name.split()

    if not parts:
        return False

    return all(
        _is_valid_name_part(part)
        for part in parts
    )


def _validate_name_list(
    value: str,
    field_name: str,
    required: bool,
) -> tuple[list[str], list[str]]:
    """Parse a name field and collect warnings for suspicious entries."""

    names = _split_semicolon_list(value)

    if required and not names:
        raise ValueError(
            f"Feltet '{field_name}' skal udfyldes."
        )

    warnings = []

    for name in names:
        if not _is_expected_name(name):
            warnings.append(
                f"{field_name}: '{name}'"
            )

    return names, warnings


def _is_expected_addition(value: str) -> bool:
    """Check whether an additional identifier uses expected characters."""

    allowed_special_characters = {
        " ",
        ".",
        "@",
        "#",
        "+",
        "-",
        "_",
    }

    return all(
        character.isalnum()
        or character in allowed_special_characters
        for character in value
    )


def _validate_additions(
    value: str,
) -> tuple[list[str], list[str]]:
    """Parse additions and collect warnings for suspicious entries."""

    additions = _split_semicolon_list(value)

    warnings = []

    for addition in additions:
        if not _is_expected_addition(addition):
            warnings.append(
                f"Andet der skal anonymiseres: '{addition}'"
            )

    return additions, warnings


## MAIN FUNCTIONALITY ##
def extract_and_validate(
    args: Namespace,
) -> tuple[dict, list[str]]:
    """Extract, normalize, and validate values supplied through the GUI."""

    input_path = _validate_input_path(args.input_path)
    output_path = _validate_output_path(args.output_path)

    child_names, child_warnings = _validate_name_list(
        value=args.child_name,
        field_name="Barnets navn",
        required=True,
    )

    parent_1_names, parent_1_warnings = _validate_name_list(
        value=args.parent_1_name,
        field_name="Forælder 1",
        required=True,
    )

    parent_2_names, parent_2_warnings = _validate_name_list(
        value=args.parent_2_name,
        field_name="Forælder 2",
        required=False,
    )

    additions, addition_warnings = _validate_additions(
        args.additions
    )

    warnings = (
        child_warnings
        + parent_1_warnings
        + parent_2_warnings
        + addition_warnings
    )

    backend_args = {
        "input": str(input_path),
        "output-dir": str(output_path),
        "barn-navn": child_names,
        "foraeldre-1": parent_1_names,
        "foraeldre-2": parent_2_names,
        "patterns": additions,
    }

    return backend_args, warnings