"""
Functions for reading Google Calendar events.
Pulls from ALL of the user's calendars and merges them,
except for calendars explicitly excluded (e.g. a separate
class-schedule calendar the user already knows by heart).
"""

from datetime import datetime, date, timedelta
from googleapiclient.discovery import build
from google_auth import get_credentials

# Calendars to skip by name. Add more strings here if you want
# to exclude other calendars later (e.g. "Exams").
EXCLUDED_CALENDARS = ["Classes"]


def get_upcoming_events(days: int = 7) -> list[dict]:
    """
    Fetches calendar events between now and `days` days from now,
    merged across all calendars except EXCLUDED_CALENDARS.
    Returns a list of simple dicts: title, day of week, start time,
    end time, location.
    """
    creds = get_credentials()
    service = build("calendar", "v3", credentials=creds)

    now = datetime.utcnow()
    time_min = now.isoformat() + "Z"
    time_max = (now + timedelta(days=days)).isoformat() + "Z"

    # Step 1: get the list of all calendars this account has
    calendar_list = service.calendarList().list().execute()
    calendars_to_query = [
        cal for cal in calendar_list["items"]
        if cal.get("summary") not in EXCLUDED_CALENDARS
    ]

    # Step 2: pull events from each calendar and merge them into one list
    all_events = []
    for cal in calendars_to_query:
        events_result = service.events().list(
            calendarId=cal["id"],
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy="startTime",
        ).execute()

        for event in events_result.get("items", []):
            start = event["start"].get("dateTime", event["start"].get("date"))
            end = event["end"].get("dateTime", event["end"].get("date"))

            # Compute the day of the week ourselves, in code, so the AI
            # never has to (and can't get wrong) calculate weekdays from
            # a raw date string.
            try:
                start_dt = datetime.fromisoformat(start)
            except ValueError:
                start_dt = date.fromisoformat(start)  # all-day events
            day_of_week = start_dt.strftime("%A")

            all_events.append({
                "title": event.get("summary", "(No title)"),
                "day_of_week": day_of_week,
                "start": start,
                "end": end,
                "location": event.get("location", ""),
                "calendar": cal.get("summary", ""),  # useful for debugging
            })

    # Step 3: sort everything chronologically since we pulled from
    # multiple calendars in separate batches
    all_events.sort(key=lambda e: e["start"])

    return all_events


if __name__ == "__main__":
    events = get_upcoming_events(days=7)
    print(f"Found {len(events)} events in the next 7 days:\n")
    for e in events:
        print(f"- [{e['calendar']}] {e['day_of_week']} | {e['title']} | {e['start']} to {e['end']} | {e['location']}")