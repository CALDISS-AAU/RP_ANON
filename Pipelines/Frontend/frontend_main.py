"""Main script for the Frontend pipeline.

To run this script, use the following command from the project root:
    uv run python -m Pipelines.Frontend.frontend_main
"""

## IMPORTS ##
from gooey import Gooey, GooeyParser
from argparse import Namespace
# Internal
from Shared_Functions.logger_functionality import *
from Pipelines.Frontend.Functions.build_GUI import build_GUI
from Pipelines.Frontend.Functions.extract_and_validate import extract_and_validate
## _______ ##


## STATIC VARIABLES ##
# Directories - input
# INPUT_DIR_AAA = "xxx/yyy.zzz"

# Directories - internal output
# OUTPUT_DIR_AAA = "Pipelines/Frontend/Data/xxx.zzz"

# Directories - global output
# OUTPUT_DIR_AAA = "./Data/Frontend/xxx.zzz"

# Directories - logs
# OUTPUT_DIR_LOG_FULL_PIPELINE = "./Pipelines/Frontend/Logs/full_pipeline.log"
# OUTPUT_DIR_LOG_1 = "./Pipelines/Frontend/Logs/example_1.log"
# OUTPUT_DIR_LOG_2 = "./Pipelines/Frontend/Logs/example_2.log"

## _______________________ ##


## HELPER FUNCTIONS ##
@Gooey(
    program_name="PDF-anonymiseringsværktøj",
    program_description=(
        "Dette er et værktøj til anonymisering af danske sagsakter i PDF format."
    ),
    required_cols=1,
    optional_cols=1,
)
## ________________ ##


## MAIN FUNCTION ##
def main() -> Namespace:
    """Run the full Frontend pipeline."""

    parser = GooeyParser()

    build_GUI(parser)

    args = parser.parse_args()

    print("Programmet er startet")

    validated_args = extract_and_validate(args)

    print("Der er givet følgende input:\n"
          f"Input fil: ")

    return validated_args

## CALL OF MAIN FUNCTION ##
# if __name__ == "__main__":
#     main()
if __name__ == "__main__":
    try:
        main()
    except Exception:
        import traceback

        traceback.print_exc()
        input("\nPress Enter to close...")
        raise