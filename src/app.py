import json
import logging
import argparse
import requests
from google.oauth2.credentials import Credentials
from typing import Dict, Any, Optional
from auth import authenticate


# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)


def fetch_form_data(credentials: Credentials, form_id: str) -> Dict[str, Any]:
    """
    Fetches questions from a Google Form using the Google Forms API.

    Args:
        credentials (Credentials): Authenticated Google OAuth credentials.
        form_id (str): The Google Form ID.

    Returns:
        Dict[str, Any]: The form data as a dictionary, or an error message.
    """
    url = f"https://forms.googleapis.com/v1/forms/{form_id}"
    headers = {"Authorization": f"Bearer {credentials.token}"}

    try:
        logging.info(f"Fetching form questions for Form ID: {form_id}...")
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            logging.error(
                f"Failed to fetch form questions. Status Code: {response.status_code}"
            )
            return {"error": response.json()}

        logging.info("Form questions retrieved successfully.")
        return response.json()

    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed: {e}")
        return {"error": str(e)}


if __name__ == "__main__":
    """
    Main entry point of the script. Parses command-line arguments,
    authenticates the user, and fetches Google Form questions.
    """
    parser = argparse.ArgumentParser(description="Fetch Google Form Questions via API")
    parser.add_argument(
        "--form-id", required=True, help="Google Form ID to fetch questions from"
    )
    args = parser.parse_args()

    form_id: str = args.form_id

    credentials: Optional[Credentials] = authenticate()

    if credentials:
        # Fetch form questions
        form_data = fetch_form_data(credentials, form_id)

        # Print form questions in a readable JSON format
        print(json.dumps(form_data, indent=4))
    else:
        logging.error("Authentication failed. Exiting script.")
