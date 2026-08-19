"""Functions for constructing the frontend GUI."""

## IMPORTS ##
import logging
from gooey import GooeyParser
## _______ ##


## HELPER FUNCTIONS ##
def _add_browse_field(
    parser: GooeyParser,
    argument_name: str,
    text_for_user: str,
    widget: str = "FileDirChooser",
) -> None:
    """Add a field for selecting a filesystem path."""

    parser.add_argument(
        argument_name,
        help=text_for_user,
        widget=widget,
    )


def _add_text_field(
    parser,
    argument_name: str,
    label: str,
    text_for_user: str | None = None,
) -> None:
    """Generates field for additional anonymisation patterns, e.g. names"""

    kwargs = {
        "dest": argument_name,
        "default": "",
    }

    if text_for_user is not None:
        kwargs["help"] = text_for_user

    parser.add_argument(
        f"--{argument_name}",
        metavar=label,
        **kwargs,
    )


## MAIN FUNCTIONALITY ##
def build_GUI(parser: GooeyParser) -> None:
    _add_browse_field(
        parser=parser,
        argument_name="input_path",
        text_for_user=(
            "Vælg en PDF-fil eller mappe med PDF-filer, "
            "der skal anonymiseres"
        ),
        widget="FileDirChooser",
    )

    _add_browse_field(
        parser=parser,
        argument_name="output_path",
        text_for_user=(
            "Vælg den mappe de anonymiserede PDF-filer skal gemmes i"
        ),
        widget="DirChooser",
    )

    names = parser.add_argument_group(
        "Navne",
        ("Indtast ALLE permutationer af navne for de følgende personer, "
         "separeret med semikolon (;).\n"
         "Eksempel: Anna; Anna Hansen; Anna M. Hansen; Frk. Hansen; ...\n"
         "NB! Der adskilles mellem store og små bogstaver." 
         "I eksemplet ovenfor vil 'anna' derfor ikke blive anonymiseret!"
        )
    )

    _add_text_field(
        parser=names,
        argument_name="child_name",
        label="Barnets navn"
    )

    _add_text_field(
        parser=names,
        argument_name="parent_1_name",
        label="Forældre 1's navn"
    )

    _add_text_field(
        parser=names,
        argument_name="parent_2_name",
        label="Forældre 2's navn"
    )

    