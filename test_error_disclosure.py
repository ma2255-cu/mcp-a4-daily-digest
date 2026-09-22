from server import _safe_error

print("--- Error Disclosure Protection Test ---")

print("\nSimulated internal error:")
print("FileNotFoundError: /Users/example/private/credentials.json")

print("\nWhat the MCP client receives:")
print(_safe_error("fetch your calendar events"))