import random
from typing import Any, Dict


class AnswerStrategy:
    """
    Abstract base class for all answer generation strategies.
    """

    def generate_answer(self, question: Dict[str, Any]) -> Any:
        """
        Generates a random answer for the given question.

        Args:
            question (Dict[str, Any]): The question data.

        Returns:
            Any: The generated answer.
        """
        raise NotImplementedError


class TextAnswerStrategy(AnswerStrategy):
    """
    Generates a random free-text answer.
    """

    def generate_answer(self, question: Dict[str, Any]) -> str:
        return f"Random response {random.randint(1, 100)}"


class ChoiceAnswerStrategy(AnswerStrategy):
    """
    Generates a random answer for choice-based questions (radio, checkbox, dropdown).
    """

    def generate_answer(self, question: Dict[str, Any]) -> Any:
        choices = question["questionItem"]["question"]["choiceQuestion"]["options"]
        choice_values = [choice["value"] for choice in choices]

        # Determine type: Single choice or Multiple choice (Checkbox)
        question_type = question["questionItem"]["question"]["choiceQuestion"].get(
            "type", ""
        )

        if question_type == "CHECKBOX":  # Multiple selections allowed
            num_choices = random.randint(1, len(choice_values))  # Choose 1 to N answers
            return random.sample(choice_values, num_choices)

        return random.choice(choice_values)  # Single choice (RADIO, DROPDOWN)


class ScaleAnswerStrategy(AnswerStrategy):
    """
    Generates a random answer within the defined scale range.
    """

    def generate_answer(self, question: Dict[str, Any]) -> str:
        scale = question["questionItem"]["question"]["scaleQuestion"]
        low, high = scale["low"], scale["high"]
        return str(random.randint(low, high))


class MatrixAnswerStrategy(AnswerStrategy):
    """
    Generates random answers for matrix (grid) questions, selecting one answer per row.
    """

    def generate_answer(self, question: Dict[str, Any]) -> Dict[str, str]:
        row_answers = {}
        for row in question["questionGroupItem"]["questions"]:
            # row_label = row["question"]["questionId"]
            row_label = row["questionId"]
            strategy = AnswerStrategyFactory.get_strategy(row)
            row_answers[row_label] = strategy.generate_answer(row)
        return row_answers


class AnswerStrategyFactory:
    """
    Factory for selecting the correct answer generation strategy based on question type.
    """

    @staticmethod
    def get_strategy(question: Dict[str, Any]) -> AnswerStrategy:
        """
        Returns the appropriate strategy based on the question type.

        Args:
            question (Dict[str, Any]): The question data.

        Returns:
            AnswerStrategy: The corresponding strategy class instance.
        """
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
