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
- `test_sanitization.py` — standalone exploit test for the input sanitization best practice
- `test_error_disclosure.py` — standalone test showing that internal errors are replaced with a generic safe message

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
   `query` parameter is cleaned before being used in a Gmail search.
   Special characters used by Gmail search syntax (`:`, `*`, quotes,
   etc.) are removed, and Boolean operators such as `OR`, `AND`, and
   `NOT` are filtered out. Without this, a value like
   `"test OR is:trusted from:*"` could inject extra Gmail search
   behavior far beyond a simple keyword lookup. After sanitization, the
   same input is reduced to plain keywords with no operators left.

2. **Error Disclosure** (`server.py`, `_safe_error`) — every tool wraps
   its Google API calls in a try/except. If something fails internally
   (expired login, network issue, bad request), the tool returns one
   generic message instead of the raw exception, so internal details
   never reach the caller.

## Testing the best practices

- **Input Sanitization**: run `python test_sanitization.py`. The script
  passes a malicious Gmail search string containing operators such as
  `OR`, `is:`, and `from:*` through `_sanitize_query()` and prints both
  the original and sanitized versions, showing the input is reduced to
  plain keywords before it can reach Gmail.

- **Error Disclosure**: run `python test_error_disclosure.py`. The
  script shows an example internal error containing a local file path,
  then shows the generic message returned by `_safe_error()`. The MCP
  tools in `server.py` use try/except blocks to replace internal
  exceptions with this generic response so implementation details are
  not returned to the MCP client.

  For the live exploit demonstration, temporarily rename both
  `credentials_enmgt4405_A4.json` and `token.json`, then call a calendar
  or Gmail tool through Claude Desktop. With both authentication files
  unavailable, the Google authentication process generates an internal
  error. The MCP tool catches that exception and returns the generic
  safe message instead of exposing the raw error or local file paths.
  Restore both filenames afterward.

## AI tools used

Claude Sonnet 5 (via claude.ai) was used to write and debug this MCP
server, including diagnosing the FastMCP/MCPServer SDK migration issue
and drafting the input sanitization and error handling. Per the
syllabus, code produced with AI does not need line-by-line attribution.

## Citations

- The Google authentication flow in `google_auth.py` is adapted from
  Google's official quickstart:
  https://developers.google.com/workspace/gmail/api/quickstart/python