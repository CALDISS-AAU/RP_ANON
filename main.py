"""This is the main script of the ANON-project.
This script is reserved for calling and combining pipelines from the
Pipelines/ folders.
For a description of the overall functionality of the individual
pipelines, please consult their respective Pipelines/README.md.

To run this script, please use this command in the terminal,
from the project root:
    uv run python -m main
"""

## IMPORTS ##
from pathlib import Path
import argparse

# Pipeline mains
from Pipelines.Frontend.frontend_main import main as run_frontend
from Pipelines.Backend.backend_main import main as run_backend
# from Pipelines.Backend.Functions.ocr_func import searchable_pdf
## _______ ##


## MAIN FUNCTION ##
def main():
    backend_args = run_frontend()

    if backend_args is None:
        return None

    run_backend(
        pdf_path=backend_args["input"],
        output_dir=backend_args["output-dir"],
        barn_navn=backend_args["barn-navn"],
        foraeldre_1=backend_args["foraeldre-1"],
        foraeldre_2=backend_args["foraeldre-2"],
        patterns=backend_args["patterns"],
    )

    print("Programmet er nu færdigkørt.")


## _____________ ##

## CALL OF MAIN FUNCTION ##
if __name__ == "__main__":
    main()
