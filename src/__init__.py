import os
from dotenv import load_dotenv

# Loads environment variables from a .env file into your shell’s environment.
# Make sure you have a .env file at the project’s root (or specify the path).

env_path = os.path.join(os.path.dirname(__file__), '../..', '.env')
load_dotenv()