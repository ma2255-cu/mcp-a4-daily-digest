"""
Functions for reading Gmail messages.
Same pattern as calendar_tools.py: plain function first, MCP wrapper later.
"""

import re
from datetime import date
from googleapiclient.discovery import build
from google_auth import get_credentials


def _sanitize_query(query: str) -> str:
    """
    BEST PRACTICE — Input Sanitization.

    `query` gets passed into a Gmail search string. Gmail supports operators
    such as "from:", "is:", "OR", "*", etc. Without sanitization, a caller
    could provide input that changes the behavior of the Gmail search instead
    of acting as a simple keyword search.

    To prevent this, the input is cleaned in two steps:
    1. Remove special characters used by Gmail search syntax.
    2. Remove Boolean operators such as OR, AND, and NOT.

    The result is limited to simple keyword-style input before it is sent
    to Gmail.
    """
    if not query:
        return ""

    # Remove special characters such as :, *, quotes, braces, and -
    safe_query = re.sub(r"[^a-zA-Z0-9 ]", " ", query)

    # Break the remaining text into individual words.
    words = safe_query.split()

    # Remove Boolean operators that Gmail could interpret as commands.
    blocked_words = {"OR", "AND", "NOT"}
    safe_words = [
        word for word in words
        if word.upper() not in blocked_words
    ]

    return " ".join(safe_words)


def get_recent_emails(
    max_results: int = 10,
    unread_only: bool = False,
    query: str = "",
) -> list[dict]:
    """
    Fetches recent Gmail messages, optionally filtered by a keyword search.
    Returns a list of simple dicts: sender, subject, snippet, date.
    """
    creds = get_credentials()
    service = build("gmail", "v1", credentials=creds)

    query = _sanitize_query(query)

    parts = []
    if unread_only:
        parts.append("is:unread")
    if query:
        parts.append(query)
    search_query = " ".join(parts)

    results = service.users().messages().list(
        userId="me",
        maxResults=max_results,
        q=search_query,
    ).execute()

    message_refs = results.get("messages", [])

    emails = []
    for ref in message_refs:
        msg = service.users().messages().get(
            userId="me",
            id=ref["id"],
            format="metadata",
            metadataHeaders=["From", "Subject", "Date"],
        ).execute()

        headers = {h["name"]: h["value"] for h in msg["payload"]["headers"]}

        emails.append({
            "from": headers.get("From", "(unknown sender)"),
            "subject": headers.get("Subject", "(no subject)"),
            "date": headers.get("Date", ""),
            "snippet": msg.get("snippet", ""),
        })

    return emails


def get_emails_awaiting_reply(since: str | None = None) -> list[dict]:
    """
    Finds emails YOU sent that have not received any reply yet.
    Defaults to the start of the current calendar month.
    `since` can override this — format YYYY/MM/DD (Gmail's date format).
    """
    creds = get_credentials()
    service = build("gmail", "v1", credentials=creds)

    if since is None:
        since = date.today().replace(day=1).strftime("%Y/%m/%d")

    results = service.users().messages().list(
        userId="me",
        q=f"in:sent after:{since}",
        maxResults=50,
    ).execute()

    sent_refs = results.get("messages", [])

    awaiting = []
    seen_threads = set()
    for ref in sent_refs:
        msg = service.users().messages().get(
            userId="me", id=ref["id"], format="metadata",
            metadataHeaders=["To", "Subject", "Date"],
        ).execute()

        thread_id = msg["threadId"]
        if thread_id in seen_threads:
            continue
        seen_threads.add(thread_id)

        # If the thread still has only ONE message, nothing has come
        # back since you sent it — meaning no reply yet.
        thread = service.users().threads().get(
            userId="me", id=thread_id, format="metadata",
            metadataHeaders=["To", "Subject", "Date"],
        ).execute()

        if len(thread.get("messages", [])) == 1:
            headers = {h["name"]: h["value"] for h in msg["payload"]["headers"]}
            awaiting.append({
                "to": headers.get("To", "(unknown recipient)"),
                "subject": headers.get("Subject", "(no subject)"),
                "date": headers.get("Date", ""),
            })

    return awaiting


if __name__ == "__main__":
    emails = get_recent_emails(max_results=5)
    print(f"Found {len(emails)} recent emails:\n")
    for e in emails:
        print(f"From: {e['from']}")
        print(f"Subject: {e['subject']}")
        print(f"Snippet: {e['snippet']}")
        print("---")

    print("\nAwaiting reply this month:\n")
    for e in get_emails_awaiting_reply():
        print(f"To: {e['to']} | Subject: {e['subject']} | Sent: {e['date']}")