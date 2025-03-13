import os
import random
from typing import Dict, Any, List

from openai import OpenAI
from dotenv import load_dotenv

from config import AI_PROMPT


# Loads environment variables from a .env file into your shell’s environment.
# Make sure you have a .env file at the project’s root (or specify the path).
load_dotenv()


class AnswerStrategy:
    """Abstract base class for answer generation strategies."""

    def generate_answer(self, question: Dict[str, Any]) -> Dict[str, Any]:
        """Generates a structured response dictionary."""
        raise NotImplementedError


class TextAnswerStrategy(AnswerStrategy):
    """Handles free-text question answers."""

    OPENAI_KEY = os.getenv("OPENAI_API_KEY")
    if not OPENAI_KEY:
        raise ValueError("OPENAI_API_KEY not found in .env file.")

    def generate_answer(self, question: Dict[str, Any]) -> Dict[str, Any]:
        question_id = question["questionItem"]["question"]["questionId"]
        question_text = question["title"].strip()

        # 1) Skip optional questions
        if "(optional)" in question_text.lower():
            return {}
        if "email" in question_text.lower():
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

            generated_answer = response.choices[0].message.content

        return {
            "entryId": "<TO ADD>",
            "questionId": question_id,
            "question_title": question_text,
            "answers": [generated_answer],
        }


class ChoiceAnswerStrategy(AnswerStrategy):
    """Handles multiple-choice (checkbox, radio, dropdown) question answers."""

    def generate_answer(self, question: Dict[str, Any]) -> Dict[str, Any]:
        question_id = question["questionItem"]["question"]["questionId"]
        question_text = question["title"]
        choices = question["questionItem"]["question"]["choiceQuestion"]["options"]

        choice_values = [choice["value"] for choice in choices if "value" in choice]

        # Determine if single-choice (RADIO, DROPDOWN) or multiple-choice (CHECKBOX)
        question_type = question["questionItem"]["question"]["choiceQuestion"].get(
            "type", ""
        )

        if question_type == "CHECKBOX":  # Multiple selections allowed
            num_choices = random.randint(1, len(choice_values))  # Select 1 to N answers
            answers = random.sample(choice_values, num_choices)
        else:
            answers = [random.choice(choice_values)]

        return {
            "entryId": "<TO ADD>",
            "questionId": question_id,
            "question_title": question_text,
            "answers": answers,
        }


class ScaleAnswerStrategy(AnswerStrategy):
    """Handles scale-based (linear scale) question answers."""

    def generate_answer(self, question: Dict[str, Any]) -> Dict[str, Any]:
        question_id = question["questionItem"]["question"]["questionId"]
        question_text = question["title"]
        scale = question["questionItem"]["question"]["scaleQuestion"]
        low, high = scale["low"], scale["high"]

        return {
            "entryId": "<TO ADD>",
            "questionId": question_id,
            "question_title": question_text,
            "answers": [str(random.randint(low, high))],
        }


class MatrixAnswerStrategy(AnswerStrategy):
    """Handles matrix/grid questions where each row has a single selection."""

    def generate_answer(self, question: Dict[str, Any]) -> List[Dict[str, Any]]:
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
            chosen_answer = random.choice(choice_values)

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
