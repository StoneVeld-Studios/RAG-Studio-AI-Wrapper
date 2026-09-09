import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest

from lib.redactor import SecurityRedactor


@pytest.fixture
def redactor():
    return SecurityRedactor()


def test_generic_password_is_redacted(redactor):
    result, count = redactor.scrub_text('password = "hello123"')

    assert "hello123" not in result
    assert "[REDACTED_" in result
    assert count == 1


def test_api_key_is_redacted(redactor):
    result, count = redactor.scrub_text('api_key = "abc123"')

    assert "abc123" not in result
    assert "[REDACTED_" in result
    assert count == 1


def test_openai_api_key_is_redacted(redactor):
    result, count = redactor.scrub_text('OPENAI_API_KEY="abc123"')

    assert "abc123" not in result
    assert "[REDACTED_" in result
    assert count == 1


def test_secret_is_redacted(redactor):
    result, count = redactor.scrub_text('secret: "mysecret"')

    assert "mysecret" not in result
    assert "[REDACTED_" in result
    assert count == 1


def test_authorization_bearer_token_is_redacted(redactor):
    result, count = redactor.scrub_text(
        "Authorization: Bearer abc123"
    )

    assert "abc123" not in result
    assert "[REDACTED_" in result
    assert count == 1


def test_custom_target_is_redacted(redactor):
    result, count = redactor.scrub_text(
        'MY_PRIVATE_THING = "keep_this_private"',
        "MY_PRIVATE_THING",
    )

    assert "keep_this_private" not in result
    assert "[REDACTED_" in result
    assert count == 1


def test_custom_target_is_literal_not_regex(redactor):
    result, count = redactor.scrub_text(
        'MY.PRIVATE.THING = "secret_value"',
        "MY.PRIVATE.THING",
    )

    assert "secret_value" not in result
    assert count == 1


def test_empty_payload_is_safe(redactor):
    result, count = redactor.scrub_text("")

    assert result == ""
    assert count == 0


def test_normal_text_is_not_redacted(redactor):
    text = "This is ordinary application configuration."

    result, count = redactor.scrub_text(text)

    assert result == text
    assert count == 0


def test_private_value_without_custom_target_is_not_redacted(redactor):
    text = 'MY_PRIVATE_THING = "keep_this_private"'

    result, count = redactor.scrub_text(text)

    assert result == text
    assert count == 0


def test_multiple_secrets_are_counted(redactor):
    text = """
password = "fake_password"
api_key = "fake_api_key"
secret = "fake_secret"
"""

    result, count = redactor.scrub_text(text)

    assert "fake_password" not in result
    assert "fake_api_key" not in result
    assert "fake_secret" not in result
    assert count == 3


def test_fake_private_key_is_redacted(redactor):
    text = """-----BEGIN RSA PRIVATE KEY-----
FAKE_PRIVATE_KEY_DATA
-----END RSA PRIVATE KEY-----"""

    result, count = redactor.scrub_text(text)

    assert "FAKE_PRIVATE_KEY_DATA" not in result
    assert "[REDACTED_CRYPTO_PRIVATE_KEY]" in result
    assert count == 1
