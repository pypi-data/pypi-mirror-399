"""Tests for pass client."""

import pytest
from unittest.mock import patch, MagicMock
import subprocess

from pass_client import (
  PassClient,
  PasswordEntry,
  PassNotFoundError,
  PassGPGError,
  PassError,
)


@pytest.fixture
def client():
  return PassClient()


class TestPasswordEntry:
  def test_from_raw_simple(self):
    raw = "mysecretpassword"
    entry = PasswordEntry.from_raw("test/path", raw)
    assert entry.password == "mysecretpassword"
    assert entry.path == "test/path"
    assert entry.metadata == {}

  def test_from_raw_with_metadata(self):
    raw = """secretpass123
username: john@example.com
url: https://github.com
notes: My GitHub account"""
    entry = PasswordEntry.from_raw("github", raw)
    assert entry.password == "secretpass123"
    assert entry.username == "john@example.com"
    assert entry.url == "https://github.com"
    assert entry.notes == "My GitHub account"

  def test_username_alias(self):
    raw = """pass123
user: alice"""
    entry = PasswordEntry.from_raw("test", raw)
    assert entry.username == "alice"


class TestPassClient:
  @patch("subprocess.run")
  def test_get_success(self, mock_run, client):
    mock_run.return_value = MagicMock(
      returncode=0,
      stdout="mypassword\nusername: test@example.com\n",
      stderr="",
    )

    entry = client.get("websites/test")

    assert entry.password == "mypassword"
    assert entry.username == "test@example.com"
    mock_run.assert_called_once()

  @patch("subprocess.run")
  def test_get_not_found(self, mock_run, client):
    mock_run.return_value = MagicMock(
      returncode=1,
      stdout="",
      stderr="Error: websites/missing is not in the password store.",
    )

    with pytest.raises(PassNotFoundError) as exc:
      client.get("websites/missing")

    assert "websites/missing" in str(exc.value)

  @patch("subprocess.run")
  def test_insert_with_metadata(self, mock_run, client):
    mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

    result = client.insert(
      "websites/new",
      "newpassword",
      metadata={"username": "user@test.com", "url": "https://test.com"},
    )

    assert result is True
    call_args = mock_run.call_args
    assert "insert" in call_args[0][0]
    assert "--multiline" in call_args[0][0]

  @patch("subprocess.run")
  def test_generate(self, mock_run, client):
    mock_run.return_value = MagicMock(
      returncode=0,
      stdout="The generated password for test is:\nAb3$xYz9!kL2@mN\n",
      stderr="",
    )

    result = client.generate("test", length=16, no_symbols=False)

    assert result.path == "test"
    assert result.length == 16
    assert result.strength == "strong"

  @patch("subprocess.run")
  def test_exists_true(self, mock_run, client):
    with patch.object(client.store_path.__class__, "__truediv__") as mock_path:
      mock_gpg_file = MagicMock()
      mock_gpg_file.exists.return_value = True
      mock_path.return_value = mock_gpg_file

      # Direct file check, no subprocess
      result = client.exists("websites/github")
      assert result is True

  @patch("subprocess.run")
  def test_list_empty_store(self, mock_run, client):
    mock_run.return_value = MagicMock(
      returncode=1,
      stdout="",
      stderr="Error: password store is empty.",
    )

    result = client.list()
    assert result == []

  @patch("subprocess.run")
  def test_gpg_error(self, mock_run, client):
    mock_run.return_value = MagicMock(
      returncode=2,
      stdout="",
      stderr="gpg: decryption failed: No secret key",
    )

    with pytest.raises(PassGPGError):
      client.get("secured/entry")


class TestSearchResult:
  @patch("subprocess.run")
  def test_find(self, mock_run, client):
    mock_run.return_value = MagicMock(
      returncode=0,
      stdout="Search Terms: github\n├── websites/github\n└── work/github-enterprise\n",
      stderr="",
    )

    results = client.find("github")
    assert len(results) == 2
    assert results[0].path == "websites/github"
    assert results[0].match_type == "name"
