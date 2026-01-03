"""
Telegram Alert Client.

The main TelegramAlert class for sending messages to Telegram.
"""

import asyncio
import html
from datetime import datetime
from typing import Literal

import httpx

from .config import TelegramConfig, load_config
from .exceptions import RateLimitError, SendError
from .formatters import escape_markdown

ParseMode = Literal["MarkdownV2", "HTML"] | None


class TelegramAlert:
    """
    Simple, async-first Telegram alerting client.

    Example:
        >>> alert = TelegramAlert()  # Auto-loads from environment
        >>> await alert.send("Hello!")

        >>> # Or with explicit config
        >>> alert = TelegramAlert(token="...", chat_id="...")

        >>> # Sync usage for scripts
        >>> alert.send_sync("Quick message!")

        >>> # Context manager for connection reuse
        >>> async with TelegramAlert() as alert:
        ...     await alert.send("msg1")
        ...     await alert.send("msg2")
    """

    def __init__(
        self,
        token: str | None = None,
        chat_id: str | list[str] | None = None,
        rate_limit_delay: float = 1.0,
    ):
        """
        Initialize TelegramAlert client.

        Args:
            token: Bot token (optional, falls back to TELEGRAM_TOKEN env var)
            chat_id: Chat ID or list of chat IDs (optional, falls back to TELEGRAM_CHAT_ID env var)
            rate_limit_delay: Minimum seconds between messages (default 1.0)

        Raises:
            ConfigError: If token or chat_id cannot be resolved
        """
        self._config: TelegramConfig = load_config(token=token, chat_id=chat_id)
        self._rate_limit_delay = rate_limit_delay
        self._last_send_time: datetime | None = None
        self._client: httpx.AsyncClient | None = None

    async def send(
        self,
        message: str,
        parse_mode: ParseMode = None,
        max_retries: int = 3,
        backoff_factor: float = 2.0,
        disable_preview: bool = True,
        silent: bool = False,
    ) -> bool:
        """
        Send a message to Telegram.

        If multiple chat IDs were configured, broadcasts to all of them.

        Args:
            message: Message text to send
            parse_mode: "MarkdownV2", "HTML", or None for plain text
            max_retries: Number of retry attempts on failure (default 3)
            backoff_factor: Exponential backoff multiplier (default 2.0)
            disable_preview: Disable link previews (default True)
            silent: Send without notification sound (default False)

        Returns:
            True if message was sent successfully to all chats

        Raises:
            SendError: If message fails after all retries
            RateLimitError: If rate limited after all retries
        """
        results = []
        for chat_id in self._config.chat_ids:
            result = await self._send_to_chat(
                chat_id=chat_id,
                message=message,
                parse_mode=parse_mode,
                max_retries=max_retries,
                backoff_factor=backoff_factor,
                disable_preview=disable_preview,
                silent=silent,
            )
            results.append(result)

        return all(results)

    async def send_to(
        self,
        chat_id: str,
        message: str,
        parse_mode: ParseMode = None,
        max_retries: int = 3,
        backoff_factor: float = 2.0,
        disable_preview: bool = True,
        silent: bool = False,
    ) -> bool:
        """
        Send a message to a specific chat ID.

        Use this to send to a chat different from the default configured ones.

        Args:
            chat_id: The chat ID to send to
            message: Message text to send
            parse_mode: "MarkdownV2", "HTML", or None for plain text
            max_retries: Number of retry attempts on failure (default 3)
            backoff_factor: Exponential backoff multiplier (default 2.0)
            disable_preview: Disable link previews (default True)
            silent: Send without notification sound (default False)

        Returns:
            True if message was sent successfully

        Raises:
            SendError: If message fails after all retries
            RateLimitError: If rate limited after all retries
        """
        return await self._send_to_chat(
            chat_id=chat_id,
            message=message,
            parse_mode=parse_mode,
            max_retries=max_retries,
            backoff_factor=backoff_factor,
            disable_preview=disable_preview,
            silent=silent,
        )

    async def _send_to_chat(
        self,
        chat_id: str,
        message: str,
        parse_mode: ParseMode = None,
        max_retries: int = 3,
        backoff_factor: float = 2.0,
        disable_preview: bool = True,
        silent: bool = False,
    ) -> bool:
        """Internal method to send to a single chat."""
        # Apply rate limiting
        await self._apply_rate_limit()

        # Escape message based on parse mode
        escaped_message = self._escape_for_mode(message, parse_mode)

        # Build request payload
        data: dict = {
            "chat_id": chat_id,
            "text": escaped_message,
            "disable_web_page_preview": disable_preview,
            "disable_notification": silent,
        }
        if parse_mode:
            data["parse_mode"] = parse_mode

        # Send with retries
        last_error: Exception | None = None
        for attempt in range(max_retries):
            try:
                client = await self._get_client()
                response = await client.post(self._config.api_url, json=data)
                response.raise_for_status()

                self._last_send_time = datetime.now()
                return True

            except httpx.TimeoutException:
                last_error = SendError("Request timed out")
                if attempt < max_retries - 1:
                    wait_time = backoff_factor**attempt
                    await asyncio.sleep(wait_time)

            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    retry_after = int(e.response.headers.get("Retry-After", 60))
                    if attempt < max_retries - 1:
                        await asyncio.sleep(retry_after)
                        last_error = RateLimitError(retry_after)
                    else:
                        raise RateLimitError(retry_after)
                else:
                    raise SendError(
                        f"API error: {e.response.text}",
                        status_code=e.response.status_code,
                    )

        if last_error:
            raise last_error
        return False

    def send_sync(
        self,
        message: str,
        parse_mode: ParseMode = None,
        max_retries: int = 3,
        backoff_factor: float = 2.0,
        disable_preview: bool = True,
        silent: bool = False,
    ) -> bool:
        """
        Synchronous wrapper for send().

        Convenience method for scripts that don't use asyncio.

        Args:
            message: Message text to send
            parse_mode: "MarkdownV2", "HTML", or None for plain text
            max_retries: Number of retry attempts on failure (default 3)
            backoff_factor: Exponential backoff multiplier (default 2.0)
            disable_preview: Disable link previews (default True)
            silent: Send without notification sound (default False)

        Returns:
            True if message was sent successfully

        Raises:
            SendError: If message fails after all retries
            RateLimitError: If rate limited after all retries
        """
        return asyncio.run(
            self.send(
                message=message,
                parse_mode=parse_mode,
                max_retries=max_retries,
                backoff_factor=backoff_factor,
                disable_preview=disable_preview,
                silent=silent,
            )
        )

    def send_to_sync(
        self,
        chat_id: str,
        message: str,
        parse_mode: ParseMode = None,
        max_retries: int = 3,
        backoff_factor: float = 2.0,
        disable_preview: bool = True,
        silent: bool = False,
    ) -> bool:
        """Synchronous wrapper for send_to()."""
        return asyncio.run(
            self.send_to(
                chat_id=chat_id,
                message=message,
                parse_mode=parse_mode,
                max_retries=max_retries,
                backoff_factor=backoff_factor,
                disable_preview=disable_preview,
                silent=silent,
            )
        )

    async def test(self) -> bool:
        """
        Test connection by verifying bot credentials.

        Calls the Telegram getMe API to verify the bot token is valid.

        Returns:
            True if credentials are valid, False otherwise
        """
        url = f"https://api.telegram.org/bot{self._config.token}/getMe"
        try:
            client = await self._get_client()
            response = await client.get(url)
            return response.status_code == 200
        except Exception:
            return False

    def test_sync(self) -> bool:
        """Synchronous wrapper for test()."""
        return asyncio.run(self.test())

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client

    async def close(self) -> None:
        """Close the HTTP client connection."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self) -> "TelegramAlert":
        """Enter async context manager."""
        return self

    async def __aexit__(self, *args) -> None:
        """Exit async context manager, closing connections."""
        await self.close()

    async def _apply_rate_limit(self) -> None:
        """Apply rate limiting between messages."""
        if self._last_send_time is None:
            return

        elapsed = (datetime.now() - self._last_send_time).total_seconds()
        if elapsed < self._rate_limit_delay:
            await asyncio.sleep(self._rate_limit_delay - elapsed)

    def _escape_for_mode(self, message: str, parse_mode: ParseMode) -> str:
        """Escape message based on parse mode."""
        if parse_mode == "MarkdownV2":
            return escape_markdown(message)
        elif parse_mode == "HTML":
            return html.escape(message)
        return message

    @property
    def chat_id(self) -> str:
        """Primary chat ID (first in list)."""
        return self._config.chat_ids[0]

    @property
    def chat_ids(self) -> list[str]:
        """All configured chat IDs."""
        return self._config.chat_ids

    @property
    def api_url(self) -> str:
        """Telegram API URL (for debugging)."""
        return self._config.api_url
