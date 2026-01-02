"""Tests for async pass client."""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock

from pass_client import (
  AsyncPassClient,
  AsyncPassClientContext,
  PasswordEntry,
  PassNotFoundError,
  PassGPGError,
)


@pytest.fixture
def client():
  return AsyncPassClient()


class TestAsyncPassClient:
  @pytest.mark.asyncio
  async def test_get_success(self, client):
    mock_proc = AsyncMock()
    mock_proc.communicate = AsyncMock(return_value=(
      b"mypassword\nusername: test@example.com\n",
      b"",
    ))
    mock_proc.returncode = 0

    with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
      entry = await client.get("websites/test")

    assert entry.password == "mypassword"
    assert entry.username == "test@example.com"

  @pytest.mark.asyncio
  async def test_get_not_found(self, client):
    mock_proc = AsyncMock()
    mock_proc.communicate = AsyncMock(return_value=(
      b"",
      b"Error: websites/missing is not in the password store.",
    ))
    mock_proc.returncode = 1

    with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
      with pytest.raises(PassNotFoundError) as exc:
        await client.get("websites/missing")

    assert "websites/missing" in str(exc.value)

  @pytest.mark.asyncio
  async def test_insert_with_metadata(self, client):
    mock_proc = AsyncMock()
    mock_proc.communicate = AsyncMock(return_value=(b"", b""))
    mock_proc.returncode = 0

    with patch("asyncio.create_subprocess_exec", return_value=mock_proc) as mock_exec:
      result = await client.insert(
        "websites/new",
        "newpassword",
        metadata={"username": "user@test.com"},
      )

    assert result is True
    call_args = mock_exec.call_args[0]
    assert "insert" in call_args
    assert "--multiline" in call_args

  @pytest.mark.asyncio
  async def test_generate(self, client):
    mock_proc = AsyncMock()
    mock_proc.communicate = AsyncMock(return_value=(
      b"The generated password for test is:\nAb3$xYz9!kL2@mN\n",
      b"",
    ))
    mock_proc.returncode = 0

    with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
      result = await client.generate("test", length=16)

    assert result.path == "test"
    assert result.length == 16

  @pytest.mark.asyncio
  async def test_get_many_concurrent(self, client):
    """Test concurrent fetching of multiple entries."""
    call_count = 0

    async def mock_communicate():
      nonlocal call_count
      call_count += 1
      return (f"password{call_count}\n".encode(), b"")

    mock_proc = AsyncMock()
    mock_proc.communicate = mock_communicate
    mock_proc.returncode = 0

    with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
      entries = await client.get_many(["site1", "site2", "site3"])

    assert len(entries) == 3
    assert call_count == 3  # All three ran

  @pytest.mark.asyncio
  async def test_insert_many_concurrent(self, client):
    """Test concurrent insertion of multiple entries."""
    mock_proc = AsyncMock()
    mock_proc.communicate = AsyncMock(return_value=(b"", b""))
    mock_proc.returncode = 0

    with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
      status = await client.insert_many([
        ("site1", "pass1", None),
        ("site2", "pass2", {"username": "user2"}),
        ("site3", "pass3", {"username": "user3", "url": "https://site3.com"}),
      ])

    assert status["site1"] is True
    assert status["site2"] is True
    assert status["site3"] is True

  @pytest.mark.asyncio
  async def test_list_empty_store(self, client):
    mock_proc = AsyncMock()
    mock_proc.communicate = AsyncMock(return_value=(
      b"",
      b"Error: password store is empty.",
    ))
    mock_proc.returncode = 1

    with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
      result = await client.list()

    assert result == []

  @pytest.mark.asyncio
  async def test_gpg_error(self, client):
    mock_proc = AsyncMock()
    mock_proc.communicate = AsyncMock(return_value=(
      b"",
      b"gpg: decryption failed: No secret key",
    ))
    mock_proc.returncode = 2

    with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
      with pytest.raises(PassGPGError):
        await client.get("secured/entry")


class TestAsyncContextManager:
  @pytest.mark.asyncio
  async def test_context_manager(self):
    async with AsyncPassClientContext() as client:
      assert isinstance(client, AsyncPassClient)

  @pytest.mark.asyncio
  async def test_context_manager_with_path(self):
    from pathlib import Path
    custom_path = Path("/custom/store")

    async with AsyncPassClientContext(store_path=custom_path) as client:
      assert client.store_path == custom_path
