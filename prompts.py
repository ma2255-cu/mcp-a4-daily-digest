"""
Formatting instructions for the daily digest.

This describes HOW to turn calendar + email data into a written
summary. It does not contain the data itself — the data comes from
live calls to this server's own tools, made fresh every time the
digest is requested (see the daily_digest prompt in server.py).
"""

DAILY_DIGEST_PROMPT = """Write a clear, organized digest of the student's day and week ahead.

- Group events by day. Don't skip any of them.
- Each event already includes a day_of_week field — use that
  directly, don't calculate weekdays yourself from the date.
- Flag any scheduling conflicts (events with overlapping times).
- Flag any emails that look like they need a response or action.
- End with one encouraging or motivating sentence.
"""