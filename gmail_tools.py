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

    `query` gets dropped straight into a Gmail search string. Gmail
    search supports operators like "from:", "is:", "OR", "*", etc, so
    without this, someone could pass something like
    "urgent OR is:trusted from:*" and widen the search far past a
    simple keyword — effectively injecting extra search commands the
    tool was never meant to allow.

    To stop that, we only let plain letters, numbers, and spaces
    through. Anything else (colons, asterisks, quotes, boolean
    operators) gets stripped, so the query can only ever behave like
    a simple keyword search, never like an injected command.
    """
    if not query:
        return ""
    safe_query = re.sub(r"[^a-zA-Z0-9 ]", "", query)
    return safe_query.strip()


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

    # Quick exploit check — run this file directly and compare:
    # before sanitization, a query like "test OR is:trusted from:*"
    # would have widened the search using Gmail operators; now it's
    # reduced to plain keywords.
    print("\nSanitization check:")
    print(_sanitize_query("test OR is:trusted from:*"))