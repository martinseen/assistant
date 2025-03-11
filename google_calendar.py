import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Define the required scopes
SCOPES = ["https://www.googleapis.com/auth/calendar"]

# Authenticate and get credentials
def authenticate():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    
    # If there are no (valid) credentials, request user authentication
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for future use
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return creds

# Build the Calendar API service
def get_calendar_service():
    creds = authenticate()
    service = build("calendar", "v3", credentials=creds)
    return service


def create_google_calendar_event(summary, description, start_time, end_time, attendees):
    service = get_calendar_service()

    event = {
        "summary": summary,
        "description": description,
        "start": {
            "dateTime": start_time,
            "timeZone": "America/Los_Angeles",
        },
        "end": {
            "dateTime": end_time,
            "timeZone": "America/Los_Angeles",
        },
        "attendees": [{"email": email} for email in attendees],
        "conferenceData": {
            "createRequest": {
                "requestId": "some-random-string",
                "conferenceSolutionKey": {"type": "hangoutsMeet"},
            }
        },
    }

    event = service.events().insert(
        calendarId="primary",
        body=event,
        conferenceDataVersion=1
    ).execute()

    return {
        "event_link": event.get("htmlLink"),
        "meet_link": event.get("conferenceData", {}).get("entryPoints", [{}])[0].get("uri", "No link available"),
    }
