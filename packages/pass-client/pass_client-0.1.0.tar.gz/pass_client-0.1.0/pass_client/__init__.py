"""Pass store API client for Python.

A typed, modern Python client for the standard Unix password manager (pass).

Example (sync):
  from pass_client import PassClient

  client = PassClient()
  entry = client.get("websites/github")
  print(entry.password)
  print(entry.username)

Example (async):
  import asyncio
  from pass_client import AsyncPassClient

  async def main():
    client = AsyncPassClient()
    entry = await client.get("websites/github")
    print(entry.password)

    # Concurrent fetches
    entries = await client.get_many(["site1", "site2", "site3"])

  asyncio.run(main())
"""

from .client import PassClient
from .async_client import AsyncPassClient, AsyncPassClientContext
from .exceptions import (
  PassError,
  PassNotFoundError,
  PassStoreNotInitializedError,
  PassGPGError,
  PassClipboardError,
  PassGitError,
  PassGenerateError,
  PassInsertError,
  # OTP exceptions
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
  # OTP models
  OTPType,
  OTPAlgorithm,
  OTPCode,
  OTPUri,
  OTPEntry,
)

__version__ = "0.1.0"
__all__ = [
  # Clients
  "PassClient",
  "AsyncPassClient",
  "AsyncPassClientContext",
  # Exceptions
  "PassError",
  "PassNotFoundError",
  "PassStoreNotInitializedError",
  "PassGPGError",
  "PassClipboardError",
  "PassGitError",
  "PassGenerateError",
  "PassInsertError",
  "PassOTPError",
  "PassOTPNotFoundError",
  "PassOTPInvalidURIError",
  "PassOTPExtensionNotFoundError",
  # Models
  "PasswordEntry",
  "StoreEntry",
  "EntryType",
  "GeneratedPassword",
  "StoreInfo",
  "GitCommit",
  "SearchResult",
  # OTP models
  "OTPType",
  "OTPAlgorithm",
  "OTPCode",
  "OTPUri",
  "OTPEntry",
]
