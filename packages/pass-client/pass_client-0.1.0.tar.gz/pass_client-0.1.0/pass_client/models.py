"""Typed models for pass store data structures."""

import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional
from urllib.parse import parse_qs, urlparse


class EntryType(Enum):
  """Type of pass store entry."""
  PASSWORD = "password"
  DIRECTORY = "directory"


class OTPType(Enum):
  """Type of OTP (one-time password)."""
  TOTP = "totp"  # Time-based
  HOTP = "hotp"  # HMAC-based (counter)


class OTPAlgorithm(Enum):
  """Hash algorithm for OTP generation."""
  SHA1 = "SHA1"
  SHA256 = "SHA256"
  SHA512 = "SHA512"


@dataclass
class PasswordEntry:
  """Represents a password entry in the store."""
  path: str
  password: str
  metadata: dict[str, str] = field(default_factory=dict)

  @property
  def username(self) -> Optional[str]:
    """Extract username from metadata."""
    return self.metadata.get("username") or self.metadata.get("user")

  @property
  def url(self) -> Optional[str]:
    """Extract URL from metadata."""
    return self.metadata.get("url") or self.metadata.get("site")

  @property
  def notes(self) -> Optional[str]:
    """Extract notes from metadata."""
    return self.metadata.get("notes")

  @classmethod
  def from_raw(cls, path: str, raw_content: str) -> "PasswordEntry":
    """Parse raw pass output into PasswordEntry."""
    lines = raw_content.strip().split("\n")
    password = lines[0] if lines else ""
    metadata: dict[str, str] = {}

    for line in lines[1:]:
      if ":" in line:
        key, value = line.split(":", 1)
        metadata[key.strip().lower()] = value.strip()

    return cls(path=path, password=password, metadata=metadata)


@dataclass
class StoreEntry:
  """Represents an entry (file or directory) in the pass tree."""
  name: str
  path: str
  entry_type: EntryType
  children: list["StoreEntry"] = field(default_factory=list)

  @property
  def is_password(self) -> bool:
    return self.entry_type == EntryType.PASSWORD

  @property
  def is_directory(self) -> bool:
    return self.entry_type == EntryType.DIRECTORY


@dataclass
class GeneratedPassword:
  """Represents a newly generated password."""
  path: str
  password: str
  length: int
  no_symbols: bool = False

  @property
  def strength(self) -> str:
    """Estimate password strength based on length and character set."""
    if self.length < 8:
      return "weak"
    elif self.length < 12:
      return "moderate"
    elif self.length < 16:
      return "strong"
    else:
      return "very_strong"


@dataclass
class StoreInfo:
  """Information about the password store."""
  store_path: Path
  gpg_id: str
  git_enabled: bool
  entry_count: int

  @property
  def is_initialized(self) -> bool:
    return bool(self.gpg_id)


@dataclass
class GitCommit:
  """Represents a git commit in the pass store history."""
  hash: str
  message: str
  author: str
  timestamp: datetime

  @classmethod
  def from_log_line(cls, line: str) -> "GitCommit":
    """Parse git log --format output."""
    # Expected format: hash|message|author|timestamp
    parts = line.split("|", 3)
    if len(parts) < 4:
      raise ValueError(f"Invalid git log format: {line}")

    return cls(
      hash=parts[0],
      message=parts[1],
      author=parts[2],
      timestamp=datetime.fromisoformat(parts[3])
    )


@dataclass
class SearchResult:
  """Result from searching the password store."""
  path: str
  match_type: str  # "name" or "content"
  context: Optional[str] = None


@dataclass
class OTPCode:
  """Generated OTP code with metadata."""
  code: str
  path: str
  remaining_seconds: Optional[int] = None  # For TOTP

  @property
  def formatted(self) -> str:
    """Format code with space in middle (e.g., '123 456')."""
    if len(self.code) == 6:
      return f"{self.code[:3]} {self.code[3:]}"
    elif len(self.code) == 8:
      return f"{self.code[:4]} {self.code[4:]}"
    return self.code


@dataclass
class OTPUri:
  """Parsed OTP URI (otpauth://)."""
  uri: str
  otp_type: OTPType
  issuer: Optional[str]
  account: str
  secret: str
  algorithm: OTPAlgorithm = OTPAlgorithm.SHA1
  digits: int = 6
  period: int = 30  # TOTP only
  counter: Optional[int] = None  # HOTP only

  @classmethod
  def from_uri(cls, uri: str) -> "OTPUri":
    """Parse otpauth:// URI into OTPUri object."""
    parsed = urlparse(uri)

    if parsed.scheme != "otpauth":
      raise ValueError(f"Invalid OTP URI scheme: {parsed.scheme}")

    otp_type = OTPType(parsed.netloc.lower())

    # Parse label (path) - format: /issuer:account or /account
    label = parsed.path.lstrip("/")
    if ":" in label:
      issuer_from_label, account = label.split(":", 1)
    else:
      issuer_from_label = None
      account = label

    # Parse query parameters
    params = parse_qs(parsed.query)

    secret = params.get("secret", [""])[0]
    if not secret:
      raise ValueError("OTP URI missing secret parameter")

    issuer = params.get("issuer", [issuer_from_label])[0]
    algorithm_str = params.get("algorithm", ["SHA1"])[0].upper()
    algorithm = OTPAlgorithm(algorithm_str)
    digits = int(params.get("digits", ["6"])[0])
    period = int(params.get("period", ["30"])[0])
    counter = params.get("counter", [None])[0]
    if counter is not None:
      counter = int(counter)

    return cls(
      uri=uri,
      otp_type=otp_type,
      issuer=issuer,
      account=account,
      secret=secret,
      algorithm=algorithm,
      digits=digits,
      period=period,
      counter=counter,
    )

  def to_uri(self) -> str:
    """Serialize back to otpauth:// URI."""
    label = f"{self.issuer}:{self.account}" if self.issuer else self.account
    params = [f"secret={self.secret}"]

    if self.issuer:
      params.append(f"issuer={self.issuer}")
    if self.algorithm != OTPAlgorithm.SHA1:
      params.append(f"algorithm={self.algorithm.value}")
    if self.digits != 6:
      params.append(f"digits={self.digits}")
    if self.otp_type == OTPType.TOTP and self.period != 30:
      params.append(f"period={self.period}")
    if self.otp_type == OTPType.HOTP and self.counter is not None:
      params.append(f"counter={self.counter}")

    return f"otpauth://{self.otp_type.value}/{label}?{'&'.join(params)}"


@dataclass
class OTPEntry:
  """OTP entry associated with a password store path."""
  path: str
  otp_uri: OTPUri

  @property
  def issuer(self) -> Optional[str]:
    return self.otp_uri.issuer

  @property
  def account(self) -> str:
    return self.otp_uri.account

  @property
  def otp_type(self) -> OTPType:
    return self.otp_uri.otp_type

  @property
  def is_totp(self) -> bool:
    return self.otp_type == OTPType.TOTP

  @property
  def is_hotp(self) -> bool:
    return self.otp_type == OTPType.HOTP
