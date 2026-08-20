"""Main script for the Frontend pipeline.

To run this script, use the following command from the project root:
    uv run python -m Pipelines.Frontend.frontend_main
"""

## IMPORTS ##
import sys
import traceback
import wx
from gooey import Gooey, GooeyParser

# Internal
from Pipelines.Frontend.Functions.build_GUI import build_GUI
from Pipelines.Frontend.Functions.extract_and_validate import extract_and_validate
## _______ ##


## HELPER FUNCTIONS ##
def _confirm_warnings(warnings: list[str]) -> bool:
    """Ask the user whether to continue despite validation warnings."""

    warning_text = "\n".join(
        f"- {warning}"
        for warning in warnings
    )

    message = (
        "Der er indtastet følgende, som ikke var forventet:\n\n"
        f"{warning_text}\n\n"
        "Hvis dette er bevidst, tryk 'Fortsæt'.\n"
        "Ellers tryk 'Gå tilbage' og ret oplysningerne."
    )

    app = wx.GetApp()

    created_app = False

    if app is None:
        app = wx.App(False)
        created_app = True

    dialog = wx.MessageDialog(
        parent=None,
        message=message,
        caption="Kontrollér input",
        style=wx.YES_NO | wx.ICON_WARNING,
    )

    dialog.SetYesNoLabels(
        "Fortsæt",
        "Gå tilbage",
    )

    result = dialog.ShowModal()

    dialog.Destroy()

    if created_app:
        app.Destroy()

    return result == wx.ID_YES

## MAIN FUNCTION ##
@Gooey(
    program_name="PDF-anonymiseringsværktøj",
    program_description=(
        "Dette er et værktøj til anonymisering af danske sagsakter i PDF format."
    ),
    required_cols=1,
    optional_cols=1,
    encoding="utf-8",
    # return_to_config=True,
)
def main() -> dict | None:
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
        should_continue = _confirm_warnings(warnings)

        if not should_continue:
            print(
                "Input skal rettes. Gå tilbage til indstillingerne.",
                flush=True,
            )
            return None

    print(
        "\nInput er valideret.",
        flush=True,
    )

    print(
        "\nArgumenter sendt videre til backend:",
        flush=True,
    )

    return backend_args


## CALL OF MAIN FUNCTION ##
if __name__ == "__main__":
    try:
        main()

    except Exception as exc:
        print(
            "\n"
            "========================================\n"
            "PROGRAMMET STOPPEDE MED EN FEJL\n"
            "========================================\n"
            f"{type(exc).__name__}: {exc}\n",
            flush=True,
        )

        traceback.print_exc()

        sys.exit(1)