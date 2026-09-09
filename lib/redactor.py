import re


class SecurityRedactor:
    """
    Enforces security compliance parameters by intercepting data payloads
    and scrubbing hardcoded credentials or private data in system memory.
    """

    def __init__(self):
        # High-performance compiled regular expressions for standard leak profiles
        self.patterns = {
            "Generic_Secret": re.compile(r'(?i)(password|passwd|secret|private_key|passphrase)\s*[:=]\s*["\']([^"\']+)["\']'),
            "API_Key": re.compile(r'(?i)(api[_-]key|auth[_-]token|bearer)\s*[:=]\s*["\']([^"\']+)["\']'),
            "SSH_Private_Key": re.compile(r'-----BEGIN [A-Z]+ PRIVATE KEY-----[\s\S]+?-----END [A-Z]+ PRIVATE KEY-----'),
            "Environment_Assignment": re.compile(r'(?i)(db[_-]pass|db[_-]password|aws[_-]secret)\s*=\s*["\']([^"\']+)["\']')
        }
    def scrub_text(self, raw_payload, custom_target=""):
        """
        Scrubs matching patterns from text strings entirely in RAM.
        Returns a tuple: (scrubbed_text: str, total_redactions_found: int)
        """
        if not raw_payload:
            return "", 0

        redacted_text = raw_payload
        redaction_count = 0

        # Handle structural block redactions first (like multi-line private keys)
        if self.patterns["SSH_Private_Key"].search(redacted_text):
            redacted_text, count = self.patterns["SSH_Private_Key"].subn("[REDACTED_CRYPTO_PRIVATE_KEY]", redacted_text)
            redaction_count += count

        # Process standard dictionary-based assignment vectors
        # Using lambda patterns to strictly mask values while preserving label structures
        for label, regex in self.patterns.items():
            if label == "SSH_Private_Key":
                continue
            
            # Match the variable name and dynamically overwrite the assignment text
            def replacer(match):
                nonlocal redaction_count
                redaction_count += 1
                return f'{match.group(1)} = "[REDACTED_COMPLIANCE_{label.upper()}]"'

            redacted_text = regex.sub(replacer, redacted_text)

        return redacted_text, redaction_count
