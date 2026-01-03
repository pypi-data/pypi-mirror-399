"""Tests for TelegramAlert client."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from telegram_alert import ConfigError, RateLimitError, SendError, TelegramAlert


class TestTelegramAlertInit:
    """Tests for TelegramAlert initialization."""

    def test_init_with_explicit_config(self):
        """Should accept explicit token and chat_id."""
        alert = TelegramAlert(token="test-token", chat_id="123456")
        assert alert.chat_id == "123456"
        assert "test-token" in alert.api_url

    def test_init_with_list_of_chat_ids(self):
        """Should accept list of chat IDs."""
        alert = TelegramAlert(token="test-token", chat_id=["123", "456", "789"])
        assert alert.chat_ids == ["123", "456", "789"]
        assert alert.chat_id == "123"  # First one is primary

    def test_init_from_env(self, monkeypatch):
        """Should load config from environment variables."""
        monkeypatch.setenv("TELEGRAM_TOKEN", "env-token")
        monkeypatch.setenv("TELEGRAM_CHAT_ID", "789")

        alert = TelegramAlert()
        assert alert.chat_id == "789"
        assert "env-token" in alert.api_url

    def test_init_comma_separated_chat_ids(self, monkeypatch):
        """Should parse comma-separated chat IDs from env."""
        monkeypatch.setenv("TELEGRAM_TOKEN", "env-token")
        monkeypatch.setenv("TELEGRAM_CHAT_ID", "123, 456, 789")

        alert = TelegramAlert()
        assert alert.chat_ids == ["123", "456", "789"]

    def test_init_missing_token_raises(self, monkeypatch):
        """Should raise ConfigError when token is missing."""
        monkeypatch.delenv("TELEGRAM_TOKEN", raising=False)
        monkeypatch.delenv("TELEGRAM_CHAT_ID", raising=False)

        with pytest.raises(ConfigError) as exc_info:
            TelegramAlert()
        assert "token" in str(exc_info.value).lower()

    def test_init_missing_chat_id_raises(self, monkeypatch):
        """Should raise ConfigError when chat_id is missing."""
        monkeypatch.setenv("TELEGRAM_TOKEN", "test-token")
        monkeypatch.delenv("TELEGRAM_CHAT_ID", raising=False)

        with pytest.raises(ConfigError) as exc_info:
            TelegramAlert()
        assert "chat" in str(exc_info.value).lower()


class TestTelegramAlertSend:
    """Tests for send method."""

    @pytest.fixture
    def alert(self):
        """Create alert with test credentials."""
        return TelegramAlert(token="test-token", chat_id="123")

    @pytest.fixture
    def mock_response(self):
        """Create successful mock response."""
        response = MagicMock()
        response.status_code = 200
        response.raise_for_status = MagicMock()
        return response

    @pytest.mark.asyncio
    async def test_send_success(self, alert, mock_response):
        """Should return True on successful send."""
        with patch.object(alert, "_get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_client

            result = await alert.send("Test message")
            assert result is True
            mock_client.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_includes_chat_id(self, alert, mock_response):
        """Should include chat_id in request payload."""
        with patch.object(alert, "_get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_client

            await alert.send("Test")
            call_args = mock_client.post.call_args
            payload = call_args.kwargs["json"]
            assert payload["chat_id"] == "123"

    @pytest.mark.asyncio
    async def test_send_silent(self, alert, mock_response):
        """Should set disable_notification when silent=True."""
        with patch.object(alert, "_get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_client

            await alert.send("Test", silent=True)
            call_args = mock_client.post.call_args
            payload = call_args.kwargs["json"]
            assert payload["disable_notification"] is True

    @pytest.mark.asyncio
    async def test_send_plain_text(self, alert, mock_response):
        """Should not include parse_mode for plain text."""
        with patch.object(alert, "_get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_client

            await alert.send("Test", parse_mode=None)
            call_args = mock_client.post.call_args
            payload = call_args.kwargs["json"]
            assert "parse_mode" not in payload

    @pytest.mark.asyncio
    async def test_send_markdown(self, alert, mock_response):
        """Should include parse_mode and escape for MarkdownV2."""
        with patch.object(alert, "_get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_client

            await alert.send("Hello_world", parse_mode="MarkdownV2")
            call_args = mock_client.post.call_args
            payload = call_args.kwargs["json"]
            assert payload["parse_mode"] == "MarkdownV2"
            assert "\\_" in payload["text"]  # Escaped underscore

    @pytest.mark.asyncio
    async def test_send_to_multiple_chats(self, mock_response):
        """Should broadcast to all chat IDs."""
        alert = TelegramAlert(token="test-token", chat_id=["111", "222", "333"])

        with patch.object(alert, "_get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_client

            result = await alert.send("Broadcast")
            assert result is True
            assert mock_client.post.call_count == 3

    @pytest.mark.asyncio
    async def test_send_to_specific_chat(self, alert, mock_response):
        """Should send to specific chat via send_to."""
        with patch.object(alert, "_get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_client

            await alert.send_to("999", "Specific message")
            call_args = mock_client.post.call_args
            payload = call_args.kwargs["json"]
            assert payload["chat_id"] == "999"


class TestTelegramAlertTest:
    """Tests for test() method."""

    @pytest.mark.asyncio
    async def test_test_success(self):
        """Should return True when credentials are valid."""
        alert = TelegramAlert(token="test-token", chat_id="123")

        mock_response = MagicMock()
        mock_response.status_code = 200

        with patch.object(alert, "_get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_client

            result = await alert.test()
            assert result is True

    @pytest.mark.asyncio
    async def test_test_failure(self):
        """Should return False when credentials are invalid."""
        alert = TelegramAlert(token="test-token", chat_id="123")

        mock_response = MagicMock()
        mock_response.status_code = 401

        with patch.object(alert, "_get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_client

            result = await alert.test()
            assert result is False


class TestTelegramAlertContextManager:
    """Tests for context manager support."""

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Should close client on exit."""
        alert = TelegramAlert(token="test-token", chat_id="123")

        async with alert:
            # Force client creation
            alert._client = AsyncMock()

        # Client should be closed
        assert alert._client is None


class TestTelegramAlertSendSync:
    """Tests for send_sync method."""

    def test_send_sync_success(self):
        """Should work as sync wrapper."""
        alert = TelegramAlert(token="test-token", chat_id="123")

        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()

        with patch.object(alert, "_get_client") as mock_get_client:
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_client

            result = alert.send_sync("Test")
            assert result is True
