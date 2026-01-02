"""Pass store API client with typed interface."""

import os
import subprocess
from pathlib import Path
from typing import Optional

from .exceptions import (
  PassError,
  PassNotFoundError,
  PassStoreNotInitializedError,
  PassGPGError,
  PassClipboardError,
  PassGitError,
  PassGenerateError,
  PassInsertError,
  PassOTPError,
  PassOTPNotFoundError,
  PassOTPInvalidURIError,
  PassOTPExtensionNotFoundError,
)
from .models import (
  PasswordEntry,
  StoreEntry,
  EntryType,
  GeneratedPassword,
  StoreInfo,
  GitCommit,
  SearchResult,
  OTPCode,
  OTPUri,
  OTPEntry,
)


class PassClient:
  """Client for interacting with pass (Unix password store)."""

  def __init__(
    self,
    store_path: Optional[Path] = None,
    gpg_id: Optional[str] = None,
  ):
    """
    Initialize pass client.

    Args:
      store_path: Custom password store path. Defaults to ~/.password-store
      gpg_id: GPG key ID for encryption. Only needed for init.
    """
    self.store_path = store_path or Path.home() / ".password-store"
    self.gpg_id = gpg_id
    self._env = os.environ.copy()
    if store_path:
      self._env["PASSWORD_STORE_DIR"] = str(store_path)

  def _run(
    self,
    args: list[str],
    input_text: Optional[str] = None,
    check: bool = True,
  ) -> subprocess.CompletedProcess:
    """Execute pass command with error handling."""
    cmd = ["pass"] + args
    try:
      result = subprocess.run(
        cmd,
        input=input_text,
        capture_output=True,
        text=True,
        env=self._env,
        check=False,
      )

      if check and result.returncode != 0:
        stderr = result.stderr.strip()
        self._handle_error(stderr, args)

      return result
    except FileNotFoundError:
      raise PassError("pass command not found. Is pass installed?")

  def _handle_error(self, stderr: str, args: list[str]) -> None:
    """Parse stderr and raise appropriate exception."""
    cmd = " ".join(args)

    if "is not in the password store" in stderr:
      path = args[-1] if args else "unknown"
      raise PassNotFoundError(path)
    elif "password store is empty" in stderr.lower():
      raise PassStoreNotInitializedError()
    elif "gpg" in stderr.lower() and "error" in stderr.lower():
      raise PassGPGError(stderr)
    elif "git" in stderr.lower():
      raise PassGitError(stderr)
    elif "clipboard" in stderr.lower():
      raise PassClipboardError()
    else:
      raise PassError(stderr, command=cmd)

  def init(self, gpg_id: Optional[str] = None) -> bool:
    """
    Initialize password store.

    Args:
      gpg_id: GPG key ID for encryption.

    Returns:
      True if initialization succeeded.
    """
    key_id = gpg_id or self.gpg_id
    if not key_id:
      raise PassError("GPG ID required for initialization")

    result = self._run(["init", key_id])
    return result.returncode == 0

  def get(self, path: str) -> PasswordEntry:
    """
    Retrieve a password entry.

    Args:
      path: Path to password in store (e.g., "websites/github")

    Returns:
      PasswordEntry with password and metadata.

    Raises:
      PassNotFoundError: If entry doesn't exist.
      PassGPGError: If decryption fails.
    """
    result = self._run(["show", path])
    return PasswordEntry.from_raw(path, result.stdout)

  def get_password(self, path: str) -> str:
    """
    Get just the password (first line) from an entry.

    Args:
      path: Path to password in store.

    Returns:
      The password string.
    """
    return self.get(path).password

  def insert(
    self,
    path: str,
    password: str,
    metadata: Optional[dict[str, str]] = None,
    force: bool = False,
  ) -> bool:
    """
    Insert a new password.

    Args:
      path: Path for new entry.
      password: Password to store.
      metadata: Optional key-value metadata (username, url, etc.)
      force: Overwrite existing entry.

    Returns:
      True if insertion succeeded.
    """
    content_lines = [password]
    if metadata:
      for key, value in metadata.items():
        content_lines.append(f"{key}: {value}")
    content = "\n".join(content_lines)

    args = ["insert", "--multiline"]
    if force:
      args.append("--force")
    args.append(path)

    try:
      result = self._run(args, input_text=content)
      return result.returncode == 0
    except PassError as e:
      raise PassInsertError(path, str(e))

  def generate(
    self,
    path: str,
    length: int = 25,
    no_symbols: bool = False,
    in_place: bool = False,
    force: bool = False,
  ) -> GeneratedPassword:
    """
    Generate a new password.

    Args:
      path: Path for new entry.
      length: Password length.
      no_symbols: Exclude symbols from password.
      in_place: Only replace first line of existing entry.
      force: Overwrite existing entry.

    Returns:
      GeneratedPassword with the new password.
    """
    args = ["generate"]
    if no_symbols:
      args.append("--no-symbols")
    if in_place:
      args.append("--in-place")
    if force:
      args.append("--force")
    args.extend([path, str(length)])

    try:
      result = self._run(args)
      # Parse generated password from output
      lines = result.stdout.strip().split("\n")
      password = ""
      for line in lines:
        if line and not line.startswith("The generated password"):
          password = line.strip()
          break

      return GeneratedPassword(
        path=path,
        password=password,
        length=length,
        no_symbols=no_symbols,
      )
    except PassError as e:
      raise PassGenerateError(str(e))

  def remove(self, path: str, recursive: bool = False, force: bool = False) -> bool:
    """
    Remove a password or directory.

    Args:
      path: Path to remove.
      recursive: Remove directories recursively.
      force: Don't prompt for confirmation.

    Returns:
      True if removal succeeded.
    """
    args = ["rm"]
    if recursive:
      args.append("--recursive")
    if force:
      args.append("--force")
    args.append(path)

    result = self._run(args)
    return result.returncode == 0

  def move(self, src: str, dst: str, force: bool = False) -> bool:
    """
    Move/rename a password or directory.

    Args:
      src: Source path.
      dst: Destination path.
      force: Overwrite destination if exists.

    Returns:
      True if move succeeded.
    """
    args = ["mv"]
    if force:
      args.append("--force")
    args.extend([src, dst])

    result = self._run(args)
    return result.returncode == 0

  def copy(self, src: str, dst: str, force: bool = False) -> bool:
    """
    Copy a password or directory.

    Args:
      src: Source path.
      dst: Destination path.
      force: Overwrite destination if exists.

    Returns:
      True if copy succeeded.
    """
    args = ["cp"]
    if force:
      args.append("--force")
    args.extend([src, dst])

    result = self._run(args)
    return result.returncode == 0

  def list(self, path: str = "") -> list[StoreEntry]:
    """
    List entries in the password store.

    Args:
      path: Subdirectory to list. Empty for root.

    Returns:
      List of StoreEntry objects.
    """
    args = ["ls", path] if path else ["ls"]
    result = self._run(args, check=False)

    if result.returncode != 0:
      if "password store is empty" in result.stderr.lower():
        return []
      self._handle_error(result.stderr, args)

    return self._parse_tree(result.stdout, path)

  def _parse_tree(self, output: str, base_path: str = "") -> list[StoreEntry]:
    """Parse pass ls tree output into StoreEntry list."""
    entries: list[StoreEntry] = []
    lines = output.strip().split("\n")

    for line in lines:
      if not line.strip():
        continue
      # Skip the header line (store name)
      if line.startswith("Password Store"):
        continue

      # Remove tree drawing characters
      name = line.lstrip("│├└─ ").strip()
      if not name:
        continue

      # Determine if it's a directory (ends with /)
      is_dir = name.endswith("/")
      name = name.rstrip("/")

      full_path = f"{base_path}/{name}".lstrip("/") if base_path else name

      entries.append(StoreEntry(
        name=name,
        path=full_path,
        entry_type=EntryType.DIRECTORY if is_dir else EntryType.PASSWORD,
      ))

    return entries

  def find(self, pattern: str) -> list[SearchResult]:
    """
    Search for entries by name.

    Args:
      pattern: Search pattern (supports globs).

    Returns:
      List of matching SearchResult objects.
    """
    result = self._run(["find", pattern], check=False)
    results: list[SearchResult] = []

    for line in result.stdout.strip().split("\n"):
      line = line.lstrip("│├└─ ").strip()
      if line and not line.startswith("Search Terms:"):
        results.append(SearchResult(path=line, match_type="name"))

    return results

  def grep(self, pattern: str) -> list[SearchResult]:
    """
    Search password contents.

    Args:
      pattern: Regex pattern to search for.

    Returns:
      List of matching SearchResult objects.
    """
    result = self._run(["grep", pattern], check=False)
    results: list[SearchResult] = []

    for line in result.stdout.strip().split("\n"):
      if ":" in line:
        path, context = line.split(":", 1)
        results.append(SearchResult(
          path=path.strip(),
          match_type="content",
          context=context.strip(),
        ))

    return results

  def clip(self, path: str, line: int = 1, timeout: int = 45) -> bool:
    """
    Copy password to clipboard.

    Args:
      path: Path to password.
      line: Line number to copy (1-indexed).
      timeout: Seconds before clipboard is cleared.

    Returns:
      True if copy succeeded.
    """
    args = ["show", "--clip"]
    if line > 1:
      args.extend(["--line", str(line)])
    args.append(path)

    self._env["PASSWORD_STORE_CLIP_TIME"] = str(timeout)

    try:
      result = self._run(args)
      return result.returncode == 0
    except PassError:
      raise PassClipboardError()

  def git(self, *args: str) -> str:
    """
    Run git command in password store.

    Args:
      *args: Git command arguments.

    Returns:
      Command output.
    """
    result = self._run(["git"] + list(args))
    return result.stdout

  def git_log(self, limit: int = 10) -> list[GitCommit]:
    """
    Get git commit history.

    Args:
      limit: Maximum commits to return.

    Returns:
      List of GitCommit objects.
    """
    format_str = "%H|%s|%an|%aI"
    output = self.git("log", f"--format={format_str}", f"-{limit}")

    commits: list[GitCommit] = []
    for line in output.strip().split("\n"):
      if line:
        try:
          commits.append(GitCommit.from_log_line(line))
        except ValueError:
          continue

    return commits

  def git_push(self) -> bool:
    """Push changes to remote."""
    self.git("push")
    return True

  def git_pull(self) -> bool:
    """Pull changes from remote."""
    self.git("pull")
    return True

  def info(self) -> StoreInfo:
    """
    Get password store information.

    Returns:
      StoreInfo with store details.
    """
    gpg_id = ""
    gpg_id_file = self.store_path / ".gpg-id"
    if gpg_id_file.exists():
      gpg_id = gpg_id_file.read_text().strip()

    git_enabled = (self.store_path / ".git").is_dir()

    # Count entries
    entry_count = 0
    if self.store_path.exists():
      entry_count = len(list(self.store_path.rglob("*.gpg")))

    return StoreInfo(
      store_path=self.store_path,
      gpg_id=gpg_id,
      git_enabled=git_enabled,
      entry_count=entry_count,
    )

  def exists(self, path: str) -> bool:
    """Check if a password entry exists."""
    gpg_file = self.store_path / f"{path}.gpg"
    return gpg_file.exists()

  def edit(self, path: str) -> bool:
    """
    Edit existing password in $EDITOR.

    Note: This opens an interactive editor.

    Args:
      path: Path to password.

    Returns:
      True if edit completed.
    """
    result = self._run(["edit", path])
    return result.returncode == 0

  # ==========================================================================
  # OTP Methods (requires pass-otp extension)
  # ==========================================================================

  def _run_otp(
    self,
    args: list[str],
    input_text: Optional[str] = None,
    check: bool = True,
  ) -> subprocess.CompletedProcess:
    """Execute pass otp command with OTP-specific error handling."""
    cmd = ["pass", "otp"] + args
    try:
      result = subprocess.run(
        cmd,
        input=input_text,
        capture_output=True,
        text=True,
        env=self._env,
        check=False,
      )

      if check and result.returncode != 0:
        stderr = result.stderr.strip()
        self._handle_otp_error(stderr, args)

      return result
    except FileNotFoundError:
      raise PassOTPExtensionNotFoundError()

  def _handle_otp_error(self, stderr: str, args: list[str]) -> None:
    """Parse OTP-specific errors."""
    path = args[-1] if args else "unknown"

    if "otp" in stderr.lower() and "not" in stderr.lower():
      raise PassOTPExtensionNotFoundError()
    elif "does not contain" in stderr.lower() or "no otp" in stderr.lower():
      raise PassOTPNotFoundError(path)
    elif "invalid" in stderr.lower() and "uri" in stderr.lower():
      raise PassOTPInvalidURIError(path, stderr)
    elif "is not in the password store" in stderr:
      raise PassNotFoundError(path)
    else:
      raise PassOTPError(stderr, path=path)

  def otp_code(self, path: str) -> OTPCode:
    """
    Generate current OTP code for an entry.

    Args:
      path: Path to password entry with OTP configured.

    Returns:
      OTPCode with the current code.

    Raises:
      PassOTPNotFoundError: If no OTP is configured.
      PassOTPExtensionNotFoundError: If pass-otp not installed.
    """
    result = self._run_otp([path])
    code = result.stdout.strip()

    return OTPCode(
      code=code,
      path=path,
    )

  def otp_code_clip(self, path: str, timeout: int = 45) -> bool:
    """
    Copy OTP code to clipboard.

    Args:
      path: Path to password entry with OTP.
      timeout: Seconds before clipboard is cleared.

    Returns:
      True if copy succeeded.
    """
    self._env["PASSWORD_STORE_CLIP_TIME"] = str(timeout)
    result = self._run_otp(["--clip", path])
    return result.returncode == 0

  def otp_uri(self, path: str) -> OTPUri:
    """
    Get the OTP URI for an entry.

    Args:
      path: Path to password entry with OTP.

    Returns:
      Parsed OTPUri object.

    Raises:
      PassOTPNotFoundError: If no OTP is configured.
    """
    result = self._run_otp(["uri", path])
    uri_str = result.stdout.strip()

    try:
      return OTPUri.from_uri(uri_str)
    except ValueError as e:
      raise PassOTPInvalidURIError(uri_str, str(e))

  def otp_uri_qrcode(self, path: str) -> bool:
    """
    Display OTP URI as QR code in terminal.

    Args:
      path: Path to password entry with OTP.

    Returns:
      True if QR code was displayed.

    Note:
      Requires qrencode to be installed.
    """
    result = self._run_otp(["uri", "--qrcode", path])
    return result.returncode == 0

  def otp_insert(
    self,
    path: str,
    uri: str,
    force: bool = False,
    from_secret: bool = False,
  ) -> bool:
    """
    Insert OTP configuration into a new entry.

    Args:
      path: Path for the new entry.
      uri: OTP URI (otpauth://...) or base32 secret if from_secret=True.
      force: Overwrite existing entry.
      from_secret: Treat uri as base32 secret instead of full URI.

    Returns:
      True if insertion succeeded.

    Example:
      # Insert with full URI
      client.otp_insert("2fa/github",
        "otpauth://totp/GitHub:user?secret=JBSWY3DPEHPK3PXP&issuer=GitHub")

      # Insert with just the secret
      client.otp_insert("2fa/github", "JBSWY3DPEHPK3PXP", from_secret=True)
    """
    args = ["insert"]
    if force:
      args.append("--force")
    if from_secret:
      args.append("--secret")
    args.append(path)

    result = self._run_otp(args, input_text=uri)
    return result.returncode == 0

  def otp_append(
    self,
    path: str,
    uri: str,
    from_secret: bool = False,
  ) -> bool:
    """
    Append OTP configuration to an existing entry.

    Args:
      path: Path to existing password entry.
      uri: OTP URI or base32 secret if from_secret=True.
      from_secret: Treat uri as base32 secret.

    Returns:
      True if append succeeded.
    """
    args = ["append"]
    if from_secret:
      args.append("--secret")
    args.append(path)

    result = self._run_otp(args, input_text=uri)
    return result.returncode == 0

  def otp_validate(self, uri: str) -> bool:
    """
    Validate an OTP URI without storing it.

    Args:
      uri: OTP URI to validate.

    Returns:
      True if URI is valid.
    """
    result = self._run_otp(["validate", uri], check=False)
    return result.returncode == 0

  def otp_get(self, path: str) -> OTPEntry:
    """
    Get full OTP entry with parsed URI.

    Args:
      path: Path to password entry with OTP.

    Returns:
      OTPEntry with path and parsed OTPUri.
    """
    otp_uri = self.otp_uri(path)
    return OTPEntry(path=path, otp_uri=otp_uri)

  def otp_has(self, path: str) -> bool:
    """
    Check if an entry has OTP configured.

    Args:
      path: Path to password entry.

    Returns:
      True if OTP is configured.
    """
    try:
      self._run_otp(["uri", path])
      return True
    except (PassOTPNotFoundError, PassNotFoundError):
      return False
