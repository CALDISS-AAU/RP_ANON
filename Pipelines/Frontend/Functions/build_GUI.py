"""Functions for constructing the frontend GUI."""

## IMPORTS ##
import logging
from gooey import GooeyParser
## _______ ##


## HELPER FUNCTIONS ##
def _add_browse_field(
    parser: GooeyParser,
    argument_name: str,
    label: str,
    text_for_user: str,
    widget: str,
    gooey_options: dict | None = None,
) -> None:
    """Add a file or directory chooser field."""

    parser.add_argument(
        argument_name,
        metavar=label,
        help=text_for_user,
        widget=widget,
        gooey_options=gooey_options or {},
    )


def _add_text_field(
    parser,
    argument_name: str,
    label: str,
    text_for_user: str | None = None,
    required: bool = False,
) -> None:
    """Add a text field to the GUI."""

    kwargs = {
        "dest": argument_name,
        "required": required,
    }

    if not required:
        kwargs["default"] = ""

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
        label="Input",
        text_for_user="Vælg en PDF-fil der skal anonymiseres",
        widget="FileChooser",
        gooey_options={
            "wildcard": "PDF-filer (*.pdf)|*.pdf",
        },
    )

    _add_browse_field(
        parser=parser,
        argument_name="output_path",
        label="Output",
        text_for_user="Vælg den mappe de anonymiserede PDF-filer skal gemmes i",
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
        label="Barnets navn",
        required=True,  
    )

    _add_text_field(
        parser=names,
        argument_name="parent_1_name",
        label="Forældre 1's navn",
        required=True,
    )

    _add_text_field(
        parser=names,
        argument_name="parent_2_name",
        label="Forældre 2's navn"
    )

    other = parser.add_argument_group(
        "Andet der skal anonymiseres",
        ("Hvis der er andet der skal anonymiseres, kan det tilføjes her. "
            "Dette kunne f.eks. være skolens navn, andre navne end barnet og "
            "forældrene, fødselsdage, eller lignende. \n"
            "Denne liste separeres med semikolon, ligesom navnelisterne, "
            "og denne liste er også følsom overfor store/små bogstaver."
        )
    )
    _add_text_field(
        parser=other,
        argument_name="additions",
        label=""
    )
    