import logging
import argparse

from app import submit_form
from auth import authenticate

logger = logging.getLogger(__name__)

def main():
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(message)s", level=logging.DEBUG
    )

    parser = argparse.ArgumentParser(description="Emulate a Google Form submission")
    parser.add_argument("--form-id", required=True, help="Google Form ID")
    args = parser.parse_args()

    form_id: str = args.form_id

    credentials = authenticate()  # Replace with your real auth routine

    if not credentials:
        logger.error("Authentication failed. Exiting script.")
        return

    # Attempt the submission
    submission_result = submit_form(credentials, form_id)
    if submission_result.get("success"):
        logger.info("Emulated submission completed!")
    else:
        logger.error(
            f"Emulated submission failed. Reason: {submission_result.get('error')}"
        )


if __name__ == "__main__":
    main()
