
import logging
import requests

from typing import Any, Dict

from google.oauth2.credentials import Credentials

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.DEBUG
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
