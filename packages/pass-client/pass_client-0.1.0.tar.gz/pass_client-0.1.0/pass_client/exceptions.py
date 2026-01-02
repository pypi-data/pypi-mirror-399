"""Custom exceptions for pass store client."""

from dataclasses import dataclass
from typing import Optional


class PassError(Exception):
  """Base exception for pass store operations."""

  def __init__(self, message: str, command: Optional[str] = None):
    self.message = message
    self.command = command
    super().__init__(message)


class PassNotFoundError(PassError):
  """Raised when a password entry is not found."""

  def __init__(self, path: str):
    self.path = path
    super().__init__(f"Password not found: {path}")


class PassStoreNotInitializedError(PassError):
  """Raised when pass store is not initialized."""

  def __init__(self):
    super().__init__(
      "Password store not initialized. Run 'pass init <gpg-id>' first."
    )


class PassGPGError(PassError):
  """Raised when GPG operations fail."""

  def __init__(self, message: str, gpg_output: Optional[str] = None):
    self.gpg_output = gpg_output
    super().__init__(f"GPG error: {message}")


class PassClipboardError(PassError):
  """Raised when clipboard operations fail."""

  def __init__(self):
    super().__init__("Failed to copy to clipboard. Is xclip/xsel installed?")


class PassGitError(PassError):
  """Raised when git operations in pass store fail."""

  def __init__(self, message: str, git_output: Optional[str] = None):
    self.git_output = git_output
    super().__init__(f"Git error in password store: {message}")


class PassGenerateError(PassError):
  """Raised when password generation fails."""

  def __init__(self, message: str):
    super().__init__(f"Password generation failed: {message}")


class PassInsertError(PassError):
  """Raised when inserting a password fails."""

  def __init__(self, path: str, reason: str):
    self.path = path
    super().__init__(f"Failed to insert password at '{path}': {reason}")


# OTP-specific exceptions

class PassOTPError(PassError):
  """Base exception for OTP operations."""

  def __init__(self, message: str, path: Optional[str] = None):
    self.path = path
    super().__init__(f"OTP error: {message}")


class PassOTPNotFoundError(PassOTPError):
  """Raised when no OTP is configured for an entry."""

  def __init__(self, path: str):
    super().__init__(f"No OTP configured for '{path}'", path=path)


class PassOTPInvalidURIError(PassOTPError):
  """Raised when OTP URI is invalid."""

  def __init__(self, uri: str, reason: str):
    self.uri = uri
    super().__init__(f"Invalid OTP URI '{uri}': {reason}")


class PassOTPExtensionNotFoundError(PassOTPError):
  """Raised when pass-otp extension is not installed."""

  def __init__(self):
    super().__init__(
      "pass-otp extension not found. Install with: "
      "apt install pass-extension-otp (Debian/Ubuntu) or "
      "brew install pass-otp (macOS)"
    )
