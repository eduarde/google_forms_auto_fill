import json
import logging
import requests

from typing import Any, Dict

from google.oauth2.credentials import Credentials

from mind import AnswerStrategyFactory

logger = logging.getLogger(__name__)

FORMS_API_URL = "https://forms.googleapis.com/v1/forms"


def generate_random_answer(question: Dict[str, Any]) -> Any:
    """
    Uses the Strategy Pattern to generate random answers based on the question type.
    """
    try:
        strategy = AnswerStrategyFactory.get_strategy(question)
        return strategy.generate_answer(question)
    except ValueError as e:
        return f"Error: {str(e)}"


def fetch_form_data(credentials: Credentials, form_id: str) -> Dict[str, Any]:
    """
    Fetches questions from a Google Form using the Google Forms API.

    Args:
        credentials (Credentials): Authenticated Google OAuth credentials.
        form_id (str): The Google Form ID.

    Returns:
        Dict[str, Any]: The form data as a dictionary, or an error message.
    """
    url = f"{FORMS_API_URL}/{form_id}"
    headers = {"Authorization": f"Bearer {credentials.token}"}

    try:
        logger.info(f"Fetching form questions for Form ID: {form_id}...")
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            logger.error(
                f"Failed to fetch form questions. Status Code: {response.status_code}"
            )
            return {"error": response.json()}

        logger.info("Form questions retrieved successfully.")
        return response.json()

    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {e}")
        return {"error": str(e)}





def submit_form(credentials, form_id: str) -> Dict[str, Any]:
    """
    Fetches Google Form questions, generates random answers, and submits the form.

    Args:
        credentials: Authenticated Google OAuth credentials.
        form_id (str): The Google Form ID.

    Returns:
        Dict[str, Any]: The API response from the Google Forms submission.
    """
   
    headers = {"Authorization": f"Bearer {credentials.token}"}

    try:
        # Step 1: Fetch form questions
        logging.info("Fetching form questions...")
        form_data = fetch_form_data(credentials, form_id)
        questions = form_data.get("items", [])

        # Step 2: Generate answers
        responses = {}
        for question in questions:
            # Check if the question is a group of multiple questions (grid/matrix)
            if "questionGroupItem" in question:
                for row_question in question["questionGroupItem"]["questions"]:
                    question_id = row_question["questionId"]
                    responses[question_id] = generate_random_answer(question)
            # Standard single-question case
            elif "questionItem" in question:
                question_id = question["questionItem"]["question"]["questionId"]
                responses[question_id] = generate_random_answer(question)

        logging.info(f"Generated answers: {json.dumps(responses, indent=2)}")

        # Step 3: Submit answers to Google Forms API
        submission_url = f"{FORMS_API_URL}/{form_id}:responses"
        payload = {
            "responses": [
                {
                    "questionId": q_id,
                    "textAnswers": {"answers": [{"value": answer}] if isinstance(answer, str) else answer}
                }
                for q_id, answer in responses.items()
            ]
        }

        submission_response = requests.post(submission_url, json=payload, headers=headers)

        if submission_response.status_code == 200:
            logging.info("Form submitted successfully!")
        else:
            logging.error(f"Failed to submit form. Status Code: {submission_response.status_code}")

        return submission_response.json()

    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed: {e}")
        return {"error": str(e)}