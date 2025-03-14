import os
import string
import random
from typing import Dict, Any, List

from openai import OpenAI
from dotenv import load_dotenv

from config import AI_PROMPT, SKIP_WORDS, SKIP_PHRASES, IGNORE_SENTIMENT_QUESTIONS


# Loads environment variables from a .env file into your shell’s environment.
# Make sure you have a .env file at the project’s root (or specify the path).
load_dotenv()


class AnswerStrategy:
    """Abstract base class for answer generation strategies."""

    def generate_answer(
        self, question: Dict[str, Any], sentiment_score: float
    ) -> Dict[str, Any]:
        """Generates a structured response dictionary."""
        raise NotImplementedError


class TextAnswerStrategy(AnswerStrategy):
    """Handles free-text question answers."""

    OPENAI_KEY = os.getenv("OPENAI_API_KEY")
    if not OPENAI_KEY:
        raise ValueError("OPENAI_API_KEY not found in .env file.")

    def _process_generated_answer(self, text: str) -> str:
        """

        Make it more natural:

        - Selects a random number of words (1-5).
        - Randomizes the order of words.
        - Randomly capitalizes the first letter of some words.
        - Removes trailing punctuation if present.

        :param text: The generated answer string.
        :return: A formatted string following these rules.
        """
        text = text.replace(".", "")
        words = [word.strip() for word in text.split(",") if word.strip()]
        if not words:
            return ""  # Return empty string if no words are present

        # Randomly shuffle words
        random.shuffle(words)

        # Select a random number of words (min 1, max 5)
        num_words = random.randint(1, min(4, len(words)))
        selected_words = words[:num_words]

        # Randomly capitalize the first letter of some words
        randomized_words = [
            word.capitalize() if random.choice([True, False]) else word.lower()
            for word in selected_words
        ]

        # Join words back into a single string
        result = ", ".join(randomized_words)

        # Remove last character if it's a punctuation mark
        if result and result[-1] in string.punctuation:
            result = result[:-1]

        return result

    def generate_answer(
        self, question: Dict[str, Any], sentiment_score: float
    ) -> Dict[str, Any]:
        question_id = question["questionItem"]["question"]["questionId"]
        question_text = question["title"].strip()

        # 1) Skip some questions
        if any(skip_phrase in question_text.lower() for skip_phrase in SKIP_PHRASES):
            return {}

        # 2) If question mentions 'Country', pick from a small set
        if "country" in question_text.lower():
            possible_countries = ("Romania", "Germany", "Austria")
            generated_answer = random.choice(possible_countries)
        else:
            # 3) Otherwise, use OpenAI to generate an answer
            client = OpenAI(api_key=self.OPENAI_KEY)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "user", "content": (f"{AI_PROMPT}\n\n{question_text}")}
                ],
            )
            generated_answer = self._process_generated_answer(
                response.choices[0].message.content
            )

        return {
            "entryId": "<TO ADD>",
            "questionId": question_id,
            "question_title": question_text,
            "answers": [generated_answer],
        }


class ChoiceAnswerStrategy(AnswerStrategy):
    """Handles multiple-choice (checkbox, radio, dropdown) question answers."""

    def _get_choices_based_on_sentiment(self, choice_values, sentiment_score):
        """
        Splits choices into three sentiment-based categories with overlapping ranges.

        :param choice_values: Sorted list of available choices.
        :param sentiment_score: Float (0.0 - 1.0) representing sentiment level.
        :return: List of choices corresponding to the sentiment category.
        """
        num_choices = len(choice_values)
        if num_choices == 0:
            return []  # Edge case: No choices available

        # Calculate cutoffs for overlapping ranges
        low_cutoff = max(2, num_choices // 3)  # Ensures at least 2 values in low
        medium_cutoff = (2 * num_choices) // 3  # Mid cutoff

        # Overlapping segments for smoother sentiment transitions
        low_range = choice_values[
            :medium_cutoff
        ]  # Covers first third + one from medium
        medium_range = choice_values[
            low_cutoff:medium_cutoff
        ]  # Properly centered medium range
        high_range = choice_values[medium_cutoff:]  # Covers last third

        # Assign ranges dynamically
        if sentiment_score < 0.33:
            return low_range  # Low sentiment gets broader choices
        elif sentiment_score < 0.66:
            return medium_range  # Medium sentiment properly centered
        else:
            return high_range  # High sentiment remains higher values

    def generate_answer(
        self, question: Dict[str, Any], sentiment_score: float
    ) -> Dict[str, Any]:
        question_id = question["questionItem"]["question"]["questionId"]
        question_text = question["title"]
        choices = question["questionItem"]["question"]["choiceQuestion"]["options"]

        choice_values = [
            choice["value"]
            for choice in choices
            if "value" in choice and choice["value"].strip().lower() not in SKIP_WORDS
        ]

        # Determine if single-choice (RADIO, DROPDOWN) or multiple-choice (CHECKBOX)
        question_type = question["questionItem"]["question"]["choiceQuestion"].get(
            "type", ""
        )

        if question_type == "CHECKBOX":  # Multiple selections allowed
            min_choices = min(
                2, len(choice_values)
            )  # Ensure it does not exceed available choices
            max_choices = max(
                min_choices, int(len(choice_values) * 0.6)
            )  # Ensure valid range
            num_choices = random.randint(
                min_choices, max_choices
            )  # Guaranteed valid range
            answers = random.sample(choice_values, num_choices)
        else:
            if any(
                q.lower() in question_text.lower().split()
                for q in IGNORE_SENTIMENT_QUESTIONS
            ):
                possible_choices = (
                    self._get_choices_based_on_sentiment(choice_values, sentiment_score)
                    or choice_values
                )
            else:
                possible_choices = choice_values

            answers = [random.choice(possible_choices)]

        return {
            "entryId": "<TO ADD>",
            "questionId": question_id,
            "question_title": question_text,
            "answers": answers,
        }


class ScaleAnswerStrategy(AnswerStrategy):
    """Handles scale-based (linear scale) question answers."""

    def _get_values_based_on_sentiment(
        self, low: int, high: int, sentiment_score: float, question_text: str
    ) -> List[int]:
        """
        Extracts scale values based on sentiment with a smoother distribution.

        :param low: Lower bound of the scale.
        :param high: Upper bound of the scale.
        :param sentiment_score: Sentiment score between 0.0 and 1.0.
        :param question_text: The question text (for debugging errors).
        :return: List of possible values based on sentiment.
        """
        # Ensure the scale is valid
        if low > high:
            raise ValueError(
                f"Invalid scale range: {low} to {high} in question '{question_text}'"
            )

        # Generate the full range of scale values
        scale_range = list(range(low, high + 1))  # Inclusive range
        num_values = len(scale_range)

        # Compute segment cutoffs for overlapping ranges
        low_cutoff = max(1, num_values // 3)
        medium_cutoff = (2 * num_values) // 3

        # Define overlapping sentiment ranges
        low_range = scale_range[:medium_cutoff]  # Covers 1st and 2nd thirds
        medium_range = scale_range[
            low_cutoff : medium_cutoff + 1
        ]  # Covers 2nd and 3rd thirds
        high_range = scale_range[medium_cutoff:]  # Covers last third

        # Select appropriate range based on sentiment score
        if sentiment_score < 0.33:
            possible_values = low_range
        elif sentiment_score < 0.66:
            possible_values = medium_range
        else:
            possible_values = high_range

        # Shuffle for better distribution before selecting
        random.shuffle(possible_values)

        return possible_values

    def generate_answer(
        self, question: Dict[str, Any], sentiment_score: float
    ) -> Dict[str, Any]:
        question_id = question["questionItem"]["question"]["questionId"]
        question_text = question["title"]
        scale = question["questionItem"]["question"]["scaleQuestion"]
        low, high = scale["low"], scale["high"]

        # Extract possible values based on sentiment
        possible_values = self._get_values_based_on_sentiment(
            low, high, sentiment_score, question_text
        )

        return {
            "entryId": "<TO ADD>",
            "questionId": question_id,
            "question_title": question_text,
            "answers": [str(random.choice(possible_values))],
        }


class MatrixAnswerStrategy(AnswerStrategy):
    """Handles matrix/grid questions where each row has a single selection."""

    def _get_matrix_choice_based_on_sentiment(
        self, choice_values: List[Any], sentiment_score: float
    ) -> Any:
        """
        Selects a matrix answer choice based on sentiment.

        :param choice_values: Sorted list of available choices.
        :param sentiment_score: Sentiment score between 0.0 and 1.0.
        :return: A single choice based on sentiment.
        """
        num_choices = len(choice_values)
        if num_choices == 0:
            raise ValueError("No available choices for matrix question.")

        # Determine sentiment category cutoffs
        low_cutoff = max(1, num_choices // 3)
        medium_cutoff = (2 * num_choices) // 3

        # Assign choices based on sentiment
        if sentiment_score < 0.33:
            possible_choices = choice_values[:low_cutoff]  # Low sentiment
        elif sentiment_score < 0.66:
            possible_choices = choice_values[
                low_cutoff:medium_cutoff
            ]  # Medium sentiment
        else:
            possible_choices = choice_values[medium_cutoff:]  # High sentiment

        # Ensure a valid choice is always selected
        return (
            random.choice(possible_choices)
            if possible_choices
            else random.choice(choice_values)
        )

    def generate_answer(
        self, question: Dict[str, Any], sentiment_score: float
    ) -> List[Dict[str, Any]]:
        responses = []

        grid_data = question.get("questionGroupItem", {})
        questions = grid_data.get("questions", [])
        columns = grid_data.get("grid", {}).get("columns", {}).get("options", [])

        if not questions or not columns:
            raise ValueError("Invalid matrix question format: Missing rows or options.")

        # Extract column choices
        choice_values = [option["value"] for option in columns]

        # Generate a random answer for each row in the matrix
        for row in questions:
            row_question_id = row["questionId"]
            chosen_answer = self._get_matrix_choice_based_on_sentiment(
                choice_values, sentiment_score
            )

            responses.append(
                {
                    "entryId": "<TO ADD>",
                    "questionId": row_question_id,
                    "question_title": row["rowQuestion"]["title"],
                    "answers": [chosen_answer],
                }
            )

        return responses


class AnswerStrategyFactory:
    """Factory for selecting the correct answer generation strategy based on question type."""

    @staticmethod
    def get_strategy(question: Dict[str, Any]) -> AnswerStrategy:
        question_data = question.get("questionItem", {}).get("question", {})

        if "textQuestion" in question_data:
            return TextAnswerStrategy()
        elif "choiceQuestion" in question_data:
            return ChoiceAnswerStrategy()
        elif "scaleQuestion" in question_data:
            return ScaleAnswerStrategy()
        elif "questionGroupItem" in question:
            return MatrixAnswerStrategy()

        raise ValueError("Unknown question type")
