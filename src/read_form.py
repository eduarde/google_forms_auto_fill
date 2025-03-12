import json
import logging
import argparse

from app import fetch_form_data
from auth import authenticate

logger = logging.getLogger(__name__)


if __name__ == "__main__":

    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(message)s", level=logging.DEBUG
    )

    parser = argparse.ArgumentParser(description="Fetch Google Form Questions via API")
    parser.add_argument(
        "--form-id", required=True, help="Google Form ID to fetch questions from"
    )
    args = parser.parse_args()

    form_id: str = args.form_id

    credentials = authenticate()

    if credentials:
        form_data = fetch_form_data(credentials, form_id)
        filename = f"data/form_data_{form_id}.json"
        with open(filename, "w") as file:
            json.dump(form_data, file, indent=4)
            logger.info(f"Form data {form_id} saved to {filename}")

    else:
        logger.error("Authentication failed. Exiting script.")
