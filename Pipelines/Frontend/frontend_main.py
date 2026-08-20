"""Main script for the Frontend pipeline.

To run this script, use the following command from the project root:
    uv run python -m Pipelines.Frontend.frontend_main
"""

## IMPORTS ##
from gooey import Gooey, GooeyParser

# Internal
from Pipelines.Frontend.Functions.build_GUI import build_GUI
from Pipelines.Frontend.Functions.extract_and_validate import extract_and_validate
## _______ ##


## MAIN FUNCTION ##
@Gooey(
    program_name="PDF-anonymiseringsværktøj",
    program_description=(
        "Dette er et værktøj til anonymisering af danske sagsakter i PDF format."
    ),
    required_cols=1,
    optional_cols=1,
    encoding="utf-8",
)
def main() -> dict:
    """Run the frontend and return validated arguments for the backend."""

    parser = GooeyParser()

    build_GUI(parser)

    args = parser.parse_args()

    print("Programmet er startet", flush=True)

    try:
        backend_args, warnings = extract_and_validate(args)

    except Exception as exc:
        raise RuntimeError(
            f"Fejl under validering af input: {exc}"
        ) from exc

    if warnings:
        print(
            "\nFølgende input afviger fra det forventede format:",
            flush=True,
        )

        for warning in warnings:
            print(
                f"- {warning}",
                flush=True,
            )

        print(
            "\nKontrollér venligst, at oplysningerne er korrekte.",
            flush=True,
        )

    print(
        "\nInput er valideret.",
        flush=True,
    )

    return backend_args


## CALL OF MAIN FUNCTION ##
if __name__ == "__main__":
    try:
        main()

    except Exception as exc:
        import traceback

        print(
            "\n"
            "========================================\n"
            "PROGRAMMET STOPPEDE MED EN FEJL\n"
            "========================================\n"
            f"{type(exc).__name__}: {exc}\n",
            flush=True,
        )

        traceback.print_exc()

        raise