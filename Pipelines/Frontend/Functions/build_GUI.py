"""Example helper functions for the pipeline."""

## IMPORTS ##
import logging
import gooey
## _______ ##


## HELPER FUNCTIONS ##
def _add_browse_field(
    text_for_user: str,
    logger: logging.Logger,
) -> None:
    """Generates a browse field, including a browse button and a text field"""
    print("Browse button")
    logger.info("Browse field with the text %s was sucesessfully added to the interface.", text_for_user)

def _add_additional_anonymisations_field(
    text_for_user: str,
    identifier_text: str,
    logger: logging.Logger,
) -> None:
    """Generates field for additional anonymisation patterns, e.g. names"""


## MAIN FUNCTIONALITY ##
def build_GUI(logger: logging.Logger) -> None:
    input_browse_text = "Vælg en PDF fil der skal anonymiseres"
    _add_browse_field(
        text_for_user=input_browse_text,
        logger=logger
    )

    output_browse_text = "Vælg en mappe den anonymiserede PDF skal gemmes i"
    _add_browse_field(
        text_for_user=output_browse_text,
        logger=logger
    )

    