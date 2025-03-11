import os
import logging
from typing import Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Define OAuth Scopes for Google Forms and Drive API access
SCOPES = [
    "https://www.googleapis.com/auth/forms",
    "https://www.googleapis.com/auth/drive",
]

# File paths for OAuth credentials
CLIENT_SECRET_FILE = "credentials.json"  # OAuth JSON file from Google Cloud
TOKEN_FILE = "token.json"  # Stores access token after authentication


def authenticate() -> Optional[Credentials]:
    """
    Authenticate the user using Google OAuth and return valid credentials.

    Returns:
        Optional[Credentials]: A valid Google OAuth2 credentials object if authentication is successful,
        otherwise None.
    """
    creds: Optional[Credentials] = None

    # Load existing token if available
    if os.path.exists(TOKEN_FILE):
        logging.info("Loading existing credentials from token file.")
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    # If credentials are not valid, authenticate the user
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            logging.info("Refreshing expired access token.")
            try:
                creds.refresh(Request())
                logging.info("Token refreshed successfully.")
            except Exception as e:
                logging.error(f"Token refresh failed: {e}")
                return None
        else:
            logging.info("No valid credentials found. Initiating authentication flow.")
            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    CLIENT_SECRET_FILE, SCOPES
                )
                creds = flow.run_local_server(port=0)  # Opens browser for login
                logging.info("Authentication successful.")
            except Exception as e:
                logging.error(f"Authentication failed: {e}")
                return None

        # Save credentials for future use
        try:
            with open(TOKEN_FILE, "w") as token_file:
                token_file.write(creds.to_json())
                logging.info("Credentials saved successfully.")
        except Exception as e:
            logging.error(f"Failed to save credentials: {e}")
            return None

    return creds
