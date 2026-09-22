"""
Shared Google authentication for the MCP server.
Handles login the first time, then reuses a saved token
so we don't need to open a browser on every run.

Adapted from Google's official quickstart pattern:
https://developers.google.com/workspace/gmail/api/quickstart/python
"""

from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/calendar.readonly",
]

# Use paths relative to THIS FILE's location, not the current working
# directory — so this works no matter what folder the program is
# launched from (e.g. Claude Desktop launches it from somewhere else
# entirely, unlike running it yourself in the terminal).
BASE_DIR = Path(__file__).parent
CREDENTIALS_FILE = BASE_DIR / "credentials_enmgt4405_A4.json"
TOKEN_FILE = BASE_DIR / "token.json"


def get_credentials():
    """
    Returns valid Google API credentials.
    - If token.json exists and is still valid, reuse it (no browser popup).
    - If it's expired, refresh it automatically.
    - If neither exists, run the browser login flow and save the result.
    """
    creds = None

    # TOKEN_FILE is a pathlib.Path, so we use its own .exists() method
    # instead of the os.path module.
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Save for next time so we don't have to log in again
        with open(TOKEN_FILE, "w") as token_file:
            token_file.write(creds.to_json())

    return creds