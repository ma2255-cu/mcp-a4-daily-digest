from gmail_tools import _sanitize_query

malicious_query = "test OR is:trusted from:*"

print("--- Input Sanitization Exploit Test ---")
print("Malicious input:")
print(malicious_query)

print("\nSanitized output:")
print(_sanitize_query(malicious_query))