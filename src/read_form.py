import json
import logging
import argparse

from app import fetch_form_data, gather_entry_data_init
from auth import authenticate

logger = logging.getLogger(__name__)


def main():
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
    if not credentials:
        logger.error("Authentication failed. Exiting script.")
        return

    # 1) Fetch the form data (the JSON you showed)
    form_data = fetch_form_data(credentials, form_id)
    filename = f"data/form_data_{form_id}.json"
    with open(filename, "w") as file:
        json.dump(form_data, file, indent=4)
        logger.info(f"Form data {form_id} saved to {filename}")

    # 2) Load the existing entry_data (the large mapping file), if present
    entry_data_filename = f"data/entry_data_{form_id}.json"
    try:
        with open(entry_data_filename, "r") as f:
            entry_data = json.load(f)
    except FileNotFoundError:
        entry_data = {}  # start with an empty dict if it doesn't exist

    # 3) If we don't already have an entry for this form_id, create one
    if form_id not in entry_data:
        entry_data[form_id] = gather_entry_data_init(form_data)
        # 4) Save the updated entry_data
        with open(entry_data_filename, "w") as file:
            json.dump(entry_data, file, indent=4)
        logger.info(f"Entry data for form {form_id} saved to {entry_data_filename}")


if __name__ == "__main__":
    main()
