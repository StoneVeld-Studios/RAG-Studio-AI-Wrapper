import re


class SecurityRedactor:
    """
    Detects and redacts common credentials and user-specified private targets.

    The redactor operates on text only and returns:
        (redacted_text, redaction_count)
    """

    def __init__(self):
        self.patterns = {
            "Generic_Secret": re.compile(
                r'(?i)(password|passwd|secret|private_key|passphrase)'
                r'\s*[:=]\s*["\']([^"\']+)["\']'
            ),
            "API_Key": re.compile(
                r'(?i)(api[_-]key|auth[_-]token|bearer)'
                r'\s*[:=]\s*["\']([^"\']+)["\']'
            ),
            "SSH_Private_Key": re.compile(
                r'-----BEGIN [A-Z0-9 ]+ PRIVATE KEY-----'
                r'[\s\S]+?'
                r'-----END [A-Z0-9 ]+ PRIVATE KEY-----'
            ),
            "Environment_Assignment": re.compile(
                r'(?i)(db[_-]pass|db[_-]password|aws[_-]secret'
                r'|aws[_-]secret[_-]access[_-]key)'
                r'\s*=\s*["\']?([^"\'\s]+)["\']?'
            ),
            "Authorization_Bearer": re.compile(
                r'(?i)(authorization\s*:\s*bearer\s+)'
                r'([^\s"\']+)'
            ),
        }

    def scrub_text(self, raw_payload, custom_target=""):
        """
        Redact known credentials and an optional user-supplied target.

        Returns:
            tuple[str, int]: redacted text and number of redactions.
        """
        if not raw_payload:
            return "", 0

        redacted_text = raw_payload
        redaction_count = 0

        # Private cryptographic keys are handled first.
        ssh_pattern = self.patterns["SSH_Private_Key"]

        redacted_text, count = ssh_pattern.subn(
            "[REDACTED_CRYPTO_PRIVATE_KEY]",
            redacted_text,
        )
        redaction_count += count

        # Handle Authorization: Bearer <token>.
        bearer_pattern = self.patterns["Authorization_Bearer"]

        def bearer_replacer(match):
            nonlocal redaction_count
            redaction_count += 1
            return (
                f"{match.group(1)}"
                "[REDACTED_COMPLIANCE_AUTHORIZATION_BEARER]"
            )

        redacted_text = bearer_pattern.sub(
            bearer_replacer,
            redacted_text,
        )

        # Handle structured credential assignments.
        for label, regex in self.patterns.items():
            if label in {
                "SSH_Private_Key",
                "Authorization_Bearer",
            }:
                continue

            def replacer(match, current_label=label):
                nonlocal redaction_count
                redaction_count += 1
                return (
                    f'{match.group(1)} = '
                    f'"[REDACTED_COMPLIANCE_'
                    f'{current_label.upper()}]"'
                )

            redacted_text = regex.sub(
                replacer,
                redacted_text,
            )

        # Handle an optional user-defined target.
        #
        # The target is treated literally, never as a regular expression.
        # If it appears as an assignment, redact the assigned value rather
        # than merely hiding the variable name.
        if custom_target:
            target = custom_target.strip()

            if len(target) > 2:
                custom_pattern = re.compile(
                    rf'({re.escape(target)}\s*[:=]\s*)'
                    r'(["\'])(.*?)\2',
                    re.IGNORECASE,
                )

                def custom_replacer(match):
                    nonlocal redaction_count
                    redaction_count += 1
                    return (
                        f'{match.group(1)}'
                        f'{match.group(2)}'
                        f'[REDACTED_CUSTOM_TARGET]'
                        f'{match.group(2)}'
                    )

                redacted_text = custom_pattern.sub(
                    custom_replacer,
                    redacted_text,
                )
        return redacted_text, redaction_count
