"""
MCP server entry point.
Wires calendar_tools, gmail_tools, and prompts into an
actual MCP server that Claude Desktop can connect to.

Note: built against MCP Python SDK v2.x, where the main
server class is MCPServer (renamed from FastMCP in v1.x).
See: https://py.sdk.modelcontextprotocol.io/v2/migration/
"""

from mcp.server.mcpserver import MCPServer

from calendar_tools import get_upcoming_events as _get_upcoming_events
from gmail_tools import get_recent_emails as _get_recent_emails
from gmail_tools import get_emails_awaiting_reply as _get_emails_awaiting_reply
from prompts import DAILY_DIGEST_PROMPT

mcp = MCPServer("daily-digest")


def _safe_error(action: str) -> dict:
    """
    BEST PRACTICE — Error Disclosure.

    If something goes wrong inside a tool (expired login, a network
    blip, a bad request to Google's API), we don't want the raw
    exception — which could include file paths, account details, or
    other internal info — going out to whoever is calling this
    server. Each tool catches its internal errors and returns this
    generic message instead.
    """
    return {"error": f"Something went wrong while trying to {action}. Please try again in a moment."}

@mcp.tool()
def get_upcoming_events(days: int = 7) -> list[dict]:
    """
    Get upcoming calendar events for the next N days, merged across
    all calendars except the Classes calendar. Each event includes
    title, day_of_week, start time, end time, location, and source calendar.
    """
    try:
        return _get_upcoming_events(days=days)
    except Exception:
        return [_safe_error("fetch your calendar events")]


@mcp.tool()
def get_recent_emails(
    max_results: int = 10,
    unread_only: bool = False,
    query: str = "",
) -> list[dict]:
    """
    Get recent Gmail messages, optionally filtered by a keyword search
    (e.g. a sender name or subject topic). Each message includes sender,
    subject, date, and a short snippet of the content.
    """
    try:
        return _get_recent_emails(max_results=max_results, unread_only=unread_only, query=query)
    except Exception:
        return [_safe_error("fetch your recent emails")]


@mcp.tool()
def get_emails_awaiting_reply() -> list[dict]:
    """
    Get emails the user sent this month that have not received any
    reply yet. Each entry includes recipient, subject, and date sent.
    Useful for following up on emails that may have been forgotten.
    """
    try:
        return _get_emails_awaiting_reply()
    except Exception:
        return [_safe_error("check for emails awaiting reply")]


@mcp.prompt()
def daily_digest(days: int = 7) -> str:
    """
    Generates instructions for producing a daily digest of the
    student's upcoming calendar events and recent emails. Tells the
    assistant to call this server's own tools for fresh data, then
    format the result using the style below.

    Args:
        days: How many days ahead to include in the calendar lookup.
            Defaults to 7.
    """
    return f"""Call get_upcoming_events(days={days}) and get_recent_emails() \
on this MCP server to get today's real calendar and email data. \
Then write the digest using these formatting instructions:

{DAILY_DIGEST_PROMPT}"""


if __name__ == "__main__":
    mcp.run()