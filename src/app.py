import os
import json
import logging
import requests
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# Define OAuth Scopes
SCOPES = ["https://www.googleapis.com/auth/forms", "https://www.googleapis.com/auth/drive"]

# Your Google Form ID (Replace with actual ID)
FORM_ID = "1VsR5ArlvJurWO4x52IGT1OKPnqzzKie60DZ7RcCOZYg"

# File paths
CLIENT_SECRET_FILE = "credentials.json"  # OAuth JSON file from Google Cloud
TOKEN_FILE = "token.json"  # Stores access token after authentication

def authenticate():
    """
    Authenticate user using Google OAuth and return valid credentials.
    """
    creds = None

    # Load existing token if available
    if os.path.exists(TOKEN_FILE):
        logging.info("Loading existing credentials from token file.")
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    # If no valid credentials, authenticate the user
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            logging.info("Refreshing expired access token.")
            creds.refresh(Request())
        else:
            logging.info("No valid credentials found. Initiating authentication flow.")
            try:
                flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
                creds = flow.run_local_server(port=0)  # Opens browser for login
            except Exception as e:
                logging.error(f"Authentication failed: {e}")
                return None

        # Save credentials for future use
        with open(TOKEN_FILE, "w") as token_file:
            token_file.write(creds.to_json())
            logging.info("Credentials saved successfully.")

    return creds

def fetch_form_questions(credentials):
    """
    Fetches questions from a Google Form using Google Forms API.
    """
    url = f"https://forms.googleapis.com/v1/forms/{FORM_ID}"
    headers = {"Authorization": f"Bearer {credentials.token}"}

    try:
        logging.info("Fetching form questions...")
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            logging.error(f"Failed to fetch form questions. Status Code: {response.status_code}")
            return {"error": response.json()}
        
        logging.info("Form questions retrieved successfully.")
        return response.json()

    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    # Authenticate user and get credentials
    creds = authenticate()
    
    if creds:
        # Fetch form questions
        form_data = fetch_form_questions(creds)
        
        # Print form questions
        print(json.dumps(form_data, indent=4))
    else:
        logging.error("Authentication failed. Exiting script.")
