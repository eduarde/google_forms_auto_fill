import json
import logging
import argparse
from typing import Optional

from google.oauth2.credentials import Credentials

from app import fetch_form_data
from auth import authenticate

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.DEBUG
)

FILENAME = "data/form_data.json"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch Google Form Questions via API")
    parser.add_argument(
        "--form-id", required=True, help="Google Form ID to fetch questions from"
    )
    args = parser.parse_args()

    form_id: str = args.form_id

    credentials: Optional[Credentials] = authenticate()

    if credentials:
        form_data = fetch_form_data(credentials, form_id)
        with open(FILENAME, "w") as file:
            json.dump(form_data, file, indent=4)
            logging.info(f"Form data saved to {FILENAME}")

    else:
        logging.error("Authentication failed. Exiting script.")
