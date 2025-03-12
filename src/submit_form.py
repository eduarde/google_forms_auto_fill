import json
import logging
import argparse

from app import submit_form
from auth import authenticate

logger = logging.getLogger(__name__)

if __name__ == "__main__":

    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(message)s", level=logging.DEBUG
    )

    parser = argparse.ArgumentParser(description="Auto-Fill & Submit a Google Form")
    parser.add_argument("--form-id", required=True, help="Google Form ID to submit responses")
    args = parser.parse_args()

    form_id: str = args.form_id

    credentials = authenticate()

    if credentials:
        submission_result = submit_form(credentials, args.form_id)
        filename = f"data/form_data_filled_{form_id}.json"
        with open(filename, "w") as file:
            json.dump(submission_result, file, indent=4)
            logger.info(f"Form data filled {form_id} saved to {filename}")
    else:
        logging.error("Authentication failed. Exiting script.")