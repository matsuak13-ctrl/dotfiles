import os
from dotenv import load_dotenv

# Load environment variables from .env file in the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(current_dir, ".env")
load_dotenv(dotenv_path)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
RECIPIENT_ADDRESS = os.getenv("RECIPIENT_ADDRESS") or GMAIL_ADDRESS
GOOGLE_DOC_ID = os.getenv("GOOGLE_DOC_ID")
GAS_WEBAPP_URL = os.getenv("GAS_WEBAPP_URL")
GAS_ACCESS_TOKEN = os.getenv("GAS_ACCESS_TOKEN")

try:
    SEARCH_LIMIT_DAYS = int(os.getenv("SEARCH_LIMIT_DAYS", "3"))
except ValueError:
    SEARCH_LIMIT_DAYS = 3


def validate_config() -> tuple[bool, list[str]]:
    """Validates that all required configuration settings are present.

    Returns:
        tuple[bool, list[str]]: A tuple where the first element is a boolean indicating
                                validity, and the second element is a list of error messages.
    """
    errors = []
    if not GEMINI_API_KEY or GEMINI_API_KEY == "your_gemini_api_key_here":
        errors.append(
            "GEMINI_API_KEY is not set or is still the default placeholder value."
        )
    if not GMAIL_ADDRESS or GMAIL_ADDRESS == "your_gmail_address@gmail.com":
        errors.append(
            "GMAIL_ADDRESS is not set or is still the default placeholder value."
        )
    if not GMAIL_APP_PASSWORD or GMAIL_APP_PASSWORD == "xxxx_xxxx_xxxx_xxxx":
        errors.append(
            "GMAIL_APP_PASSWORD is not set or is still the default placeholder value."
        )
    if not GOOGLE_DOC_ID or GOOGLE_DOC_ID == "your_google_doc_id_here":
        errors.append(
            "GOOGLE_DOC_ID is not set or is still the default placeholder value."
        )
    if not GAS_WEBAPP_URL or GAS_WEBAPP_URL == "your_gas_webapp_url_here":
        errors.append(
            "GAS_WEBAPP_URL is not set or is still the default placeholder value."
        )
    if not GAS_ACCESS_TOKEN or GAS_ACCESS_TOKEN == "your_custom_secure_token_here":
        errors.append(
            "GAS_ACCESS_TOKEN is not set or is still the default placeholder value."
        )

    return len(errors) == 0, errors
