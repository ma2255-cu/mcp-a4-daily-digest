# Daily Digest — MCP Server

ENMGT 4405, Assignment 4. Domain: **Personal Productivity**.

An MCP server that exposes a student's Google Calendar and Gmail as tools,
plus a prompt that turns that data into a written daily digest.

## Files

- `server.py` — entry point; defines the tools and the prompt, and wires
  everything into an MCP server
- `calendar_tools.py` — fetches and merges Google Calendar events
- `gmail_tools.py` — fetches Gmail messages; sanitizes search input
- `google_auth.py` — shared Google OAuth login and token handling
- `prompts.py` — formatting instructions used by the `daily_digest` prompt
- `requirements.txt` — Python dependencies
- `claude_desktop_config.json` — example Claude Desktop config for
  connecting to this server
- `.gitignore` — excludes `credentials_enmgt4405_A4.json`, `token.json`,
  and the local venv/cache from the repo
- `test_auth.py` — small standalone script used to manually verify the
  Google OAuth flow during development

## Setup

1. Clone this repo and `cd` into it.
2. Create and activate a virtual environment:
   ```
   uv venv .venv
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Get Google OAuth credentials:
   - In Google Cloud Console, enable the Gmail API and Calendar API for
     your project.
   - Create an OAuth client ID (type: Desktop app) and download it.
   - Save it in this folder as `credentials_enmgt4405_A4.json`.
   - This file is not included in the repo — it contains a secret and is
     excluded via `.gitignore`.
5. Run the server once from the terminal (`python server.py`). The first
   run opens a browser to log into Google. After that, a `token.json` is
   saved locally so you don't have to log in again. This file is also
   excluded via `.gitignore`.

## Running it

- Standalone: `python server.py`
- Connected to Claude Desktop: copy the contents of
  `claude_desktop_config.json` into your Claude Desktop config file
  (on Mac: `~/Library/Application Support/Claude/claude_desktop_config.json`),
  updating the paths to match where you cloned this repo. Restart Claude
  Desktop afterward.

## Tools and prompt

- `get_upcoming_events(days=7)` — calendar events for the next N days,
  merged across all calendars except "Classes"
- `get_recent_emails(max_results=10, unread_only=False, query="")` —
  recent Gmail messages, optionally filtered by a sanitized keyword search
- `get_emails_awaiting_reply()` — emails sent this month with no reply yet
- `daily_digest(days=7)` — an MCP prompt that instructs the assistant to
  call the tools above for fresh data, then format the result into a
  written digest

## Best practices implemented

1. **Input Sanitization** (`gmail_tools.py`, `_sanitize_query`) — the
   `query` parameter is stripped to letters, numbers, and spaces before
   being used in a Gmail search. Without this, a value like
   `"test OR is:trusted from:*"` could inject extra Gmail search
   operators far beyond a simple keyword lookup. After sanitization, the
   same input is reduced to plain keywords with no operators left.

2. **Error Disclosure** (`server.py`, `_safe_error`) — every tool wraps
   its Google API calls in a try/except. If something fails internally
   (expired login, network issue, bad request), the tool returns one
   generic message instead of the raw exception, so internal details
   never reach the caller.

## Testing the best practices

- **Input Sanitization**: run `python gmail_tools.py` directly — the
  last line prints a sample malicious query (`"test OR is:trusted
  from:*"`) before and after sanitization, showing the operators get
  stripped out.
- **Error Disclosure**: temporarily rename `credentials_enmgt4405_A4.json`
  to something else, then call any tool (e.g. ask for the daily digest
  in Claude Desktop). You'll get the generic safe-error message instead
  of a raw exception with internal file paths. Rename the file back
  afterward to restore normal function.

## AI tools used

Claude Sonnet 5 (via claude.ai) was used to write and debug this MCP
server, including diagnosing the FastMCP/MCPServer SDK migration issue
and drafting the input sanitization and error handling. Per the
syllabus, code produced with AI does not need line-by-line attribution.

## Citations

- The Google authentication flow in `google_auth.py` is adapted from
  Google's official quickstart:
  https://developers.google.com/workspace/gmail/api/quickstart/python