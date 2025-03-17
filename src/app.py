import re
import json
import logging
import random
import requests
import urllib.parse

from typing import Any, Dict, List

from google.oauth2.credentials import Credentials


from mind import AnswerStrategyFactory

logger = logging.getLogger(__name__)


FORMS_API_URL = "https://forms.googleapis.com/v1/forms"


def _generate_gaussian_sentiment(sentiment_level: str):
    """
    Generates a sentiment score based on the specified sentiment level.

    :param sentiment_level: "low", "medium", or "high"
    :return: A float between 0.0 and 1.0, clamped within valid range.
    """
    sentiment_map = {
        "low": (0.2, 0.1),  # Mean 0.2, low variance
        "medium": (0.5, 0.2),  # Mean 0.5, moderate variance
        "high": (0.8, 0.1),  # Mean 0.8, low variance
    }

    mean, std_dev = sentiment_map.get(sentiment_level, (0.5, 0.2))  # Default to medium
    sentiment_score = random.gauss(mean, std_dev)
    return max(0.0, min(1.0, sentiment_score))  # Clamp between [0,1]


def gather_entry_data_init(data: dict) -> dict:
    """
    Returns a dict { question_title: "entry.XXXX" } for every question
    found in 'data'. This includes single questions and any row-questions
    in questionGroupItem.
    """
    ENTRY_LABEL = "entry.XXXX"
    entry_questions_data = {}

    for item in data.get("items", []):
        # -- If the item itself has a title, store it:
        #    (Typically single-question items do.)
        if "title" in item and item["title"].strip():
            title = item["title"].strip()
            entry_questions_data[title] = ENTRY_LABEL

        # -- If there's a questionGroupItem, also gather row questions:
        if "questionGroupItem" in item:
            group_questions = item["questionGroupItem"].get("questions", [])
            for row_q in group_questions:
                row_title = row_q["rowQuestion"]["title"].strip()
                entry_questions_data[row_title] = ENTRY_LABEL

    return entry_questions_data


def _map_entry_with_question(
    form_id: str, data: List[Dict[str, Any]]
) -> tuple[List[Dict[str, Any]], int]:
    """
    data: list of dictionaries, each with "entryId", "questionId", "question_title", "answer".
    form_id: the form ID (e.g., "1VsR5Ar...").

    Returns: the same list, but with each "entryId" replaced by the actual "entry.xxx" value
             from entry_data.json, if found.
    """
    # Load entire mapping file
    entry_file_name = f"data/entry_data_{form_id}.json"
    with open(entry_file_name, "r") as f:
        all_forms_entry_data = json.load(f)

    # Get the specific mapping for this form_id
    form_mapping = all_forms_entry_data.get(form_id)

    # Retrieve how many Section are in form
    section_count = len([k for k in form_mapping if re.search(r"^Section\s+\d+:", k)])

    if not form_mapping:
        logger.error(f"No entry data found for form ID: {form_id}")
        return data  # or raise an exception if you prefer

    # Now iterate over the list of questions
    for item in data:
        # Make sure we skip anything that isn't a dictionary
        if not isinstance(item, dict):
            continue  # or remove these extra strings from your list entirely

        question_title = item.get("question_title").strip()
        if not question_title:
            continue  # or raise an error if "question_title" is missing

        # Lookup the 'entry.xxx' using the question title
        # (Be mindful of extra spaces or punctuation changes between the JSON and the form)
        if question_title not in form_mapping:
            raise ValueError(
                f"No matching entry ID found in entry_data.json for question title: {question_title}"
            )

        # Assign the entry.xxx to the item's "entryId"
        item["entryId"] = form_mapping[question_title]

    return data, section_count


def generate_answer(question: Dict[str, Any], sentiment_score: float) -> Any:
    """Uses the Strategy Pattern to generate answers based on the question type."""
    try:
        strategy = AnswerStrategyFactory.get_strategy(question)
        return strategy.generate_answer(question, sentiment_score)
    except ValueError as e:
        logging.error(f"Error generating answer: {e}")
        return None


def generate_submission_payload(
    form_id: str, questions: List[Dict[str, Any]], sentiment_score: float
) -> str:
    """
    Generates the final query-string payload (the part after '?') for submitting or pre-filling
    form responses. The string begins with "usp=pp_url" and includes repeated entries like
    entry.XXXX=ANSWER for each answer.

    :param form_id: The Google Form ID
    :param questions: A list of question objects (like those from your Form JSON),
                      each potentially containing 'questionItem' or 'questionGroupItem'.
    :return: A query-string-like string ready to be appended to a Google Forms URL.
    """
    # 1) Gather answers from all questions
    all_answers = []
    for question in questions:
        if "questionGroupItem" in question:
            # This is a matrix/grid question – generate a list of answers for each row
            # e.g., generate_answer(question) returns multiple row-answers
            row_answers = generate_answer(question, sentiment_score)
            all_answers.extend(row_answers)
        elif "questionItem" in question:
            # This is a standard question
            answer_obj = generate_answer(question, sentiment_score)
            if answer_obj:
                all_answers.append(answer_obj)

    # 2) Map each question or row-answer from your data to the correct entry.xxx
    #    e.g., item["question_title"] => item["entryId"]
    data_with_entry_id, section_count = _map_entry_with_question(form_id, all_answers)

    # 3) Build the 'usp=pp_url&entry.XXXX=ANSWER' string

    if section_count > 0:
        action = "&pageHistory=" + ",".join(str(i) for i in range(section_count + 1))
    else:
        action = "usp=pp_url"

    parts = [action]
    for item in data_with_entry_id:
        entry_id = item["entryId"]  # e.g. "entry.343824263"
        for answer in item["answers"]:
            encoded_answer = urllib.parse.quote_plus(answer)
            parts.append(f"{entry_id}={encoded_answer}")

    # Join into the final query string
    return "&".join(parts)


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


def submit_form(
    credentials: Credentials, form_id: str, sentiment_level: str
) -> Dict[str, Any]:
    """
    Fetches Google Form questions, generates answers, and submits the form.

    Args:
        credentials: Authenticated Google OAuth credentials.
        form_id (str): The Google Form ID.

    Returns:
        Dict[str, Any]: The API response from the Google Forms submission.
    """

    logging.info("Fetching form questions...")
    form_data = fetch_form_data(credentials, form_id)

    responder_url = form_data.get("responderUri", "")
    if not responder_url:
        logging.warning("No responderUri found in form_data.")
        return {"success": False, "error": "No responderUri"}

    # Change 'viewform' to 'formResponse'
    submit_url = responder_url.replace("/viewform", "/formResponse")

    # Extract the questions array from the JSON
    questions = form_data.get("items", [])

    #  Randomly assign a sentiment score (0.0 - 1.0) with more weight on higher range
    sentiment_score = _generate_gaussian_sentiment(sentiment_level)
    logger.info(
        f"Assigning a sentiment {sentiment_level} with score: {sentiment_score}"
    )

    # Build your query-string payload (e.g., 'usp=pp_url&entry.XXXX=answer...')
    payload = generate_submission_payload(form_id, questions, sentiment_score)

    # logging.debug(f"Generated payload: {payload}")

    # Construct the final URL:
    # e.g. 'https://docs.google.com/forms/d/e/.../formResponse?usp=pp_url&entry.XXXX=ANSWER...'
    final_url = f"{submit_url}?{payload}"

    logging.debug(f"Making GET request to: {final_url}")
    try:
        response = requests.get(final_url)
        # Optional: raise an exception if the status code indicates an error
        response.raise_for_status()
        return {
            "success": True,
            "status_code": response.status_code,
            "response_text": response.text,
        }
    except requests.exceptions.RequestException as e:
        logging.error(f"Request error: {e}", exc_info=True)
        return {"success": False, "error": str(e)}
