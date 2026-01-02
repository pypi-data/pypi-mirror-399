"""Tests for pass-otp extension support."""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from pass_client import (
  PassClient,
  AsyncPassClient,
  OTPType,
  OTPAlgorithm,
  OTPCode,
  OTPUri,
  OTPEntry,
  PassOTPNotFoundError,
  PassOTPInvalidURIError,
  PassOTPExtensionNotFoundError,
)


class TestOTPUri:
  def test_parse_totp_uri(self):
    uri = "otpauth://totp/GitHub:user@example.com?secret=JBSWY3DPEHPK3PXP&issuer=GitHub"
    parsed = OTPUri.from_uri(uri)

    assert parsed.otp_type == OTPType.TOTP
    assert parsed.issuer == "GitHub"
    assert parsed.account == "user@example.com"
    assert parsed.secret == "JBSWY3DPEHPK3PXP"
    assert parsed.algorithm == OTPAlgorithm.SHA1
    assert parsed.digits == 6
    assert parsed.period == 30

  def test_parse_hotp_uri(self):
    uri = "otpauth://hotp/Service:user?secret=ABCDEFGH&counter=42"
    parsed = OTPUri.from_uri(uri)

    assert parsed.otp_type == OTPType.HOTP
    assert parsed.account == "user"
    assert parsed.counter == 42

  def test_parse_uri_with_custom_params(self):
    uri = "otpauth://totp/Test:user?secret=ABC123&algorithm=SHA256&digits=8&period=60"
    parsed = OTPUri.from_uri(uri)

    assert parsed.algorithm == OTPAlgorithm.SHA256
    assert parsed.digits == 8
    assert parsed.period == 60

  def test_parse_uri_without_issuer_prefix(self):
    uri = "otpauth://totp/myaccount?secret=SECRETKEY&issuer=MyService"
    parsed = OTPUri.from_uri(uri)

    assert parsed.issuer == "MyService"
    assert parsed.account == "myaccount"

  def test_parse_invalid_scheme(self):
    with pytest.raises(ValueError, match="Invalid OTP URI scheme"):
      OTPUri.from_uri("http://example.com")

  def test_parse_missing_secret(self):
    with pytest.raises(ValueError, match="missing secret"):
      OTPUri.from_uri("otpauth://totp/Test:user?issuer=Test")

  def test_to_uri_roundtrip(self):
    original = "otpauth://totp/GitHub:user?secret=JBSWY3DPEHPK3PXP&issuer=GitHub"
    parsed = OTPUri.from_uri(original)
    regenerated = parsed.to_uri()

    # Parse again to verify
    reparsed = OTPUri.from_uri(regenerated)
    assert reparsed.issuer == parsed.issuer
    assert reparsed.account == parsed.account
    assert reparsed.secret == parsed.secret


class TestOTPCode:
  def test_formatted_6_digits(self):
    code = OTPCode(code="123456", path="test")
    assert code.formatted == "123 456"

  def test_formatted_8_digits(self):
    code = OTPCode(code="12345678", path="test")
    assert code.formatted == "1234 5678"

  def test_formatted_other_length(self):
    code = OTPCode(code="12345", path="test")
    assert code.formatted == "12345"


class TestOTPEntry:
  def test_properties(self):
    uri = OTPUri.from_uri(
      "otpauth://totp/GitHub:user@example.com?secret=ABC&issuer=GitHub"
    )
    entry = OTPEntry(path="2fa/github", otp_uri=uri)

    assert entry.issuer == "GitHub"
    assert entry.account == "user@example.com"
    assert entry.is_totp is True
    assert entry.is_hotp is False


class TestPassClientOTP:
  @pytest.fixture
  def client(self):
    return PassClient()

  @patch("subprocess.run")
  def test_otp_code(self, mock_run, client):
    mock_run.return_value = MagicMock(
      returncode=0,
      stdout="123456\n",
      stderr="",
    )

    code = client.otp_code("2fa/github")

    assert code.code == "123456"
    assert code.path == "2fa/github"
    assert code.formatted == "123 456"

  @patch("subprocess.run")
  def test_otp_uri(self, mock_run, client):
    mock_run.return_value = MagicMock(
      returncode=0,
      stdout="otpauth://totp/GitHub:user?secret=ABCD1234&issuer=GitHub\n",
      stderr="",
    )

    uri = client.otp_uri("2fa/github")

    assert uri.otp_type == OTPType.TOTP
    assert uri.issuer == "GitHub"
    assert uri.secret == "ABCD1234"

  @patch("subprocess.run")
  def test_otp_insert(self, mock_run, client):
    mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

    result = client.otp_insert(
      "2fa/newsite",
      "otpauth://totp/NewSite:user?secret=SECRETKEY&issuer=NewSite"
    )

    assert result is True
    call_args = mock_run.call_args[0][0]
    assert "otp" in call_args
    assert "insert" in call_args

  @patch("subprocess.run")
  def test_otp_insert_from_secret(self, mock_run, client):
    mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

    result = client.otp_insert("2fa/site", "JBSWY3DPEHPK3PXP", from_secret=True)

    assert result is True
    call_args = mock_run.call_args[0][0]
    assert "--secret" in call_args

  @patch("subprocess.run")
  def test_otp_append(self, mock_run, client):
    mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

    result = client.otp_append(
      "websites/github",
      "otpauth://totp/GitHub:user?secret=ABC123&issuer=GitHub"
    )

    assert result is True
    call_args = mock_run.call_args[0][0]
    assert "append" in call_args

  @patch("subprocess.run")
  def test_otp_validate_valid(self, mock_run, client):
    mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

    result = client.otp_validate(
      "otpauth://totp/Test:user?secret=VALIDKEY&issuer=Test"
    )

    assert result is True

  @patch("subprocess.run")
  def test_otp_validate_invalid(self, mock_run, client):
    mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="Invalid URI")

    result = client.otp_validate("not-a-valid-uri")

    assert result is False

  @patch("subprocess.run")
  def test_otp_has_true(self, mock_run, client):
    mock_run.return_value = MagicMock(
      returncode=0,
      stdout="otpauth://totp/Test:user?secret=ABC&issuer=Test\n",
      stderr="",
    )

    assert client.otp_has("2fa/test") is True

  @patch("subprocess.run")
  def test_otp_has_false(self, mock_run, client):
    mock_run.return_value = MagicMock(
      returncode=1,
      stdout="",
      stderr="Error: 2fa/noentry does not contain an otpauth:// URI",
    )

    assert client.otp_has("2fa/noentry") is False

  @patch("subprocess.run")
  def test_otp_not_found_error(self, mock_run, client):
    mock_run.return_value = MagicMock(
      returncode=1,
      stdout="",
      stderr="Error: 2fa/missing does not contain an otpauth:// URI",
    )

    with pytest.raises(PassOTPNotFoundError):
      client.otp_code("2fa/missing")

  @patch("subprocess.run")
  def test_otp_get(self, mock_run, client):
    mock_run.return_value = MagicMock(
      returncode=0,
      stdout="otpauth://totp/GitHub:user?secret=SECRET123&issuer=GitHub\n",
      stderr="",
    )

    entry = client.otp_get("2fa/github")

    assert isinstance(entry, OTPEntry)
    assert entry.path == "2fa/github"
    assert entry.issuer == "GitHub"


class TestAsyncPassClientOTP:
  @pytest.fixture
  def client(self):
    return AsyncPassClient()

  @pytest.mark.asyncio
  async def test_otp_code(self, client):
    mock_proc = AsyncMock()
    mock_proc.communicate = AsyncMock(return_value=(b"654321\n", b""))
    mock_proc.returncode = 0

    with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
      code = await client.otp_code("2fa/site")

    assert code.code == "654321"
    assert code.path == "2fa/site"

  @pytest.mark.asyncio
  async def test_otp_uri(self, client):
    uri_response = b"otpauth://totp/Service:user?secret=MYSECRET&issuer=Service\n"
    mock_proc = AsyncMock()
    mock_proc.communicate = AsyncMock(return_value=(uri_response, b""))
    mock_proc.returncode = 0

    with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
      uri = await client.otp_uri("2fa/service")

    assert uri.issuer == "Service"
    assert uri.secret == "MYSECRET"

  @pytest.mark.asyncio
  async def test_otp_insert(self, client):
    mock_proc = AsyncMock()
    mock_proc.communicate = AsyncMock(return_value=(b"", b""))
    mock_proc.returncode = 0

    with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
      result = await client.otp_insert(
        "2fa/new",
        "otpauth://totp/New:user?secret=KEY123&issuer=New"
      )

    assert result is True

  @pytest.mark.asyncio
  async def test_otp_code_many(self, client):
    """Test concurrent OTP code generation."""
    call_count = 0

    async def mock_communicate():
      nonlocal call_count
      call_count += 1
      return (f"{100000 + call_count}\n".encode(), b"")

    mock_proc = AsyncMock()
    mock_proc.communicate = mock_communicate
    mock_proc.returncode = 0

    with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
      codes = await client.otp_code_many(["2fa/site1", "2fa/site2", "2fa/site3"])

    assert len(codes) == 3
    assert call_count == 3

  @pytest.mark.asyncio
  async def test_otp_has(self, client):
    uri_response = b"otpauth://totp/Test:user?secret=ABC&issuer=Test\n"
    mock_proc = AsyncMock()
    mock_proc.communicate = AsyncMock(return_value=(uri_response, b""))
    mock_proc.returncode = 0

    with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
      result = await client.otp_has("2fa/test")

    assert result is True
