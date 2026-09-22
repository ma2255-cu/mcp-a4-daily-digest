from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

flow = InstalledAppFlow.from_client_secrets_file(
    'credentials_enmgt4405_A4.json', SCOPES
)
creds = flow.run_local_server(port=0)

print("SUCCESS! Authentication worked.")