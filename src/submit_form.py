import logging
import argparse

from app import submit_form
from auth import authenticate

logger = logging.getLogger(__name__)


def main():
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
    )

    parser = argparse.ArgumentParser(description="Emulate a Google Form submission")
    parser.add_argument("--form-id", required=True, help="Google Form ID")
    parser.add_argument(
        "--repeat", type=int, default=1, help="Repeat the submission (default: 1)"
    )
    parser.add_argument(
        "--sentiment",
        type=str,
        choices=["low", "medium", "high"],
        default="medium",
        help="Set the sentiment level (default: medium)",
    )
    args = parser.parse_args()

    form_id: str = args.form_id
    repeat_no: int = args.repeat
    sentiment_level = args.sentiment

    credentials = authenticate()  # Replace with your real auth routine

    if not credentials:
        logger.error("Authentication failed. Exiting script.")
        return

    # Attempt the submission the specified number of times
    for idx in range(repeat_no):
        submission_result = submit_form(credentials, form_id, sentiment_level)
        if submission_result.get("success"):
            logger.info("Emulated submission completed!")
        else:
            logger.error(
                f"Emulated submission failed. Reason: {submission_result.get('error')}"
            )


if __name__ == "__main__":
    main()
