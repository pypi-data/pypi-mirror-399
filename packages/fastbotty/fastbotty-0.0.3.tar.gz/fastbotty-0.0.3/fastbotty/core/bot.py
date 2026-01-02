"""Telegram bot sender with retry logic"""

import asyncio
import logging
from typing import Any, cast

import aiohttp

from fastbotty.utils.escape import sanitize_text

logger = logging.getLogger(__name__)


class TelegramBot:
    """Telegram bot for sending messages"""

    BASE_URL = "https://api.telegram.org/bot"

    def __init__(self, token: str, test_mode: bool = False):
        self.token = token
        self.test_mode = test_mode
        self.base_url = f"{self.BASE_URL}{token}/"

    async def send_message(
        self,
        chat_id: str,
        text: str,
        parse_mode: str | None = None,
        reply_markup: dict[str, Any] | None = None,
        max_retries: int = 3,
    ) -> dict[str, Any]:
        """Send text message to Telegram"""
        if self.test_mode:
            logger.info(f"TEST MODE - Would send to {chat_id}: {text}")
            return {"ok": True, "result": {"message_id": 0}}

        escaped_text = sanitize_text(text, parse_mode)

        payload: dict[str, Any] = {"chat_id": chat_id, "text": escaped_text}
        if parse_mode:
            payload["parse_mode"] = parse_mode
        if reply_markup:
            payload["reply_markup"] = reply_markup

        return await self._send_with_retry("sendMessage", payload, max_retries)

    async def send_photo(
        self,
        chat_id: str,
        photo_url: str,
        caption: str | None = None,
        parse_mode: str | None = None,
        max_retries: int = 3,
    ) -> dict[str, Any]:
        """Send photo to Telegram"""
        if self.test_mode:
            logger.info(f"TEST MODE - Would send photo to {chat_id}: {photo_url}")
            return {"ok": True, "result": {"message_id": 0}}

        payload: dict[str, Any] = {"chat_id": chat_id, "photo": photo_url}
        if caption:
            escaped_caption = sanitize_text(caption, parse_mode)
            payload["caption"] = escaped_caption
        if parse_mode:
            payload["parse_mode"] = parse_mode

        return await self._send_with_retry("sendPhoto", payload, max_retries)

    async def send_media_group(
        self,
        chat_id: str,
        photo_urls: list[str],
        caption: str | None = None,
        parse_mode: str | None = None,
        max_retries: int = 3,
    ) -> dict[str, Any]:
        """Send multiple photos as media group"""
        if self.test_mode:
            logger.info(f"TEST MODE - Would send {len(photo_urls)} photos to {chat_id}")
            return {"ok": True, "result": [{"message_id": 0}]}

        media: list[dict[str, Any]] = []
        for i, url in enumerate(photo_urls[:10]):  # Telegram limit: 10
            item: dict[str, Any] = {"type": "photo", "media": url}
            if i == 0 and caption:
                escaped_caption = sanitize_text(caption, parse_mode)
                item["caption"] = escaped_caption
                if parse_mode:
                    item["parse_mode"] = parse_mode
            media.append(item)

        payload = {"chat_id": chat_id, "media": media}
        return await self._send_with_retry("sendMediaGroup", payload, max_retries)

    async def _send_with_retry(
        self, method: str, payload: dict[str, Any], max_retries: int
    ) -> dict[str, Any]:
        """Send request with exponential backoff retry"""
        url = f"{self.base_url}{method}"

        for attempt in range(max_retries):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, json=payload) as response:
                        result: dict[str, Any] = await response.json()

                        if response.status == 200:
                            return result

                        if response.status == 429:
                            retry_after = int(response.headers.get("Retry-After", 1))
                            logger.warning(f"Rate limited. Retrying after {retry_after}s")
                            await asyncio.sleep(retry_after)
                            continue

                        error_msg = result.get("description", "Unknown error")
                        logger.error(f"Telegram API error: {error_msg}")

                        if attempt < max_retries - 1:
                            wait_time = 2**attempt
                            logger.info(f"Retrying in {wait_time}s...")
                            await asyncio.sleep(wait_time)
                        else:
                            raise Exception(f"Failed after {max_retries} attempts: {error_msg}")

            except aiohttp.ClientError as e:
                logger.error(f"Network error: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2**attempt)
                else:
                    raise

        raise Exception(f"Failed to send message after {max_retries} attempts")

    async def set_webhook(self, url: str) -> dict[str, Any]:
        """Set webhook URL for receiving updates"""
        payload: dict[str, Any] = {"url": url}
        return await self._send_with_retry("setWebhook", payload, 1)

    async def delete_webhook(self) -> dict[str, Any]:
        """Delete webhook"""
        return await self._send_with_retry("deleteWebhook", cast(dict[str, Any], {}), 1)

    async def get_webhook_info(self) -> dict[str, Any]:
        """Get current webhook info"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}getWebhookInfo") as response:
                return cast(dict[str, Any], await response.json())

    async def answer_callback_query(
        self,
        callback_query_id: str,
        text: str | None = None,
        show_alert: bool = False,
    ) -> dict[str, Any]:
        """Answer callback query from inline keyboard"""
        payload: dict[str, Any] = {"callback_query_id": callback_query_id}
        if text:
            payload["text"] = text
        payload["show_alert"] = show_alert
        return await self._send_with_retry("answerCallbackQuery", payload, 1)

    async def send_document(
        self,
        chat_id: str,
        document_url: str,
        caption: str | None = None,
        parse_mode: str | None = None,
        filename: str | None = None,
        reply_markup: dict[str, Any] | None = None,
        max_retries: int = 3,
    ) -> dict[str, Any]:
        """Send document to Telegram"""
        if self.test_mode:
            logger.info(f"TEST MODE - Would send document to {chat_id}: {document_url}")
            return {"ok": True, "result": {"message_id": 0}}

        payload: dict[str, Any] = {"chat_id": chat_id, "document": document_url}
        if caption:
            escaped_caption = sanitize_text(caption, parse_mode)
            payload["caption"] = escaped_caption
        if parse_mode:
            payload["parse_mode"] = parse_mode
        if filename:
            payload["filename"] = filename
        if reply_markup:
            payload["reply_markup"] = reply_markup

        return await self._send_with_retry("sendDocument", payload, max_retries)

    async def send_video(
        self,
        chat_id: str,
        video_url: str,
        caption: str | None = None,
        parse_mode: str | None = None,
        thumbnail_url: str | None = None,
        width: int | None = None,
        height: int | None = None,
        duration: int | None = None,
        supports_streaming: bool | None = None,
        reply_markup: dict[str, Any] | None = None,
        max_retries: int = 3,
    ) -> dict[str, Any]:
        """Send video to Telegram"""
        if self.test_mode:
            logger.info(f"TEST MODE - Would send video to {chat_id}: {video_url}")
            return {"ok": True, "result": {"message_id": 0}}

        payload: dict[str, Any] = {"chat_id": chat_id, "video": video_url}
        if caption:
            escaped_caption = sanitize_text(caption, parse_mode)
            payload["caption"] = escaped_caption
        if parse_mode:
            payload["parse_mode"] = parse_mode
        if thumbnail_url:
            payload["thumbnail"] = thumbnail_url
        if width is not None:
            payload["width"] = width
        if height is not None:
            payload["height"] = height
        if duration is not None:
            payload["duration"] = duration
        if supports_streaming is not None:
            payload["supports_streaming"] = supports_streaming
        if reply_markup:
            payload["reply_markup"] = reply_markup

        return await self._send_with_retry("sendVideo", payload, max_retries)

    async def send_audio(
        self,
        chat_id: str,
        audio_url: str,
        caption: str | None = None,
        parse_mode: str | None = None,
        duration: int | None = None,
        performer: str | None = None,
        title: str | None = None,
        thumbnail_url: str | None = None,
        reply_markup: dict[str, Any] | None = None,
        max_retries: int = 3,
    ) -> dict[str, Any]:
        """Send audio to Telegram"""
        if self.test_mode:
            logger.info(f"TEST MODE - Would send audio to {chat_id}: {audio_url}")
            return {"ok": True, "result": {"message_id": 0}}

        payload: dict[str, Any] = {"chat_id": chat_id, "audio": audio_url}
        if caption:
            escaped_caption = sanitize_text(caption, parse_mode)
            payload["caption"] = escaped_caption
        if parse_mode:
            payload["parse_mode"] = parse_mode
        if duration is not None:
            payload["duration"] = duration
        if performer:
            payload["performer"] = performer
        if title:
            payload["title"] = title
        if thumbnail_url:
            payload["thumbnail"] = thumbnail_url
        if reply_markup:
            payload["reply_markup"] = reply_markup

        return await self._send_with_retry("sendAudio", payload, max_retries)

    async def send_voice(
        self,
        chat_id: str,
        voice_url: str,
        caption: str | None = None,
        parse_mode: str | None = None,
        duration: int | None = None,
        reply_markup: dict[str, Any] | None = None,
        max_retries: int = 3,
    ) -> dict[str, Any]:
        """Send voice message to Telegram"""
        if self.test_mode:
            logger.info(f"TEST MODE - Would send voice message to {chat_id}: {voice_url}")
            return {"ok": True, "result": {"message_id": 0}}

        payload: dict[str, Any] = {"chat_id": chat_id, "voice": voice_url}
        if caption:
            escaped_caption = sanitize_text(caption, parse_mode)
            payload["caption"] = escaped_caption
        if parse_mode:
            payload["parse_mode"] = parse_mode
        if duration is not None:
            payload["duration"] = duration
        if reply_markup:
            payload["reply_markup"] = reply_markup

        return await self._send_with_retry("sendVoice", payload, max_retries)

    async def send_location(
        self,
        chat_id: str,
        latitude: float,
        longitude: float,
        horizontal_accuracy: float | None = None,
        live_period: int | None = None,
        heading: int | None = None,
        proximity_alert_radius: int | None = None,
        reply_markup: dict[str, Any] | None = None,
        max_retries: int = 3,
    ) -> dict[str, Any]:
        """Send location to Telegram"""
        if self.test_mode:
            logger.info(f"TEST MODE - Would send location to {chat_id}: ({latitude}, {longitude})")
            return {"ok": True, "result": {"message_id": 0}}

        payload: dict[str, Any] = {
            "chat_id": chat_id,
            "latitude": latitude,
            "longitude": longitude,
        }
        if horizontal_accuracy is not None:
            payload["horizontal_accuracy"] = horizontal_accuracy
        if live_period is not None:
            payload["live_period"] = live_period
        if heading is not None:
            payload["heading"] = heading
        if proximity_alert_radius is not None:
            payload["proximity_alert_radius"] = proximity_alert_radius
        if reply_markup:
            payload["reply_markup"] = reply_markup

        return await self._send_with_retry("sendLocation", payload, max_retries)

    async def send_invoice(
        self,
        chat_id: str,
        title: str,
        description: str,
        payload_str: str,
        currency: str,
        prices: list[dict[str, Any]],
        provider_token: str | None = None,
        max_tip_amount: int | None = None,
        suggested_tip_amounts: list[int] | None = None,
        start_parameter: str | None = None,
        provider_data: str | None = None,
        photo_url: str | None = None,
        photo_size: int | None = None,
        photo_width: int | None = None,
        photo_height: int | None = None,
        need_name: bool | None = None,
        need_phone_number: bool | None = None,
        need_email: bool | None = None,
        need_shipping_address: bool | None = None,
        send_phone_number_to_provider: bool | None = None,
        send_email_to_provider: bool | None = None,
        is_flexible: bool | None = None,
        reply_markup: dict[str, Any] | None = None,
        max_retries: int = 3,
    ) -> dict[str, Any]:
        """Send invoice to Telegram (required for pay button)"""
        if self.test_mode:
            logger.info(f"TEST MODE - Would send invoice to {chat_id}: {title}")
            return {"ok": True, "result": {"message_id": 0}}

        payload: dict[str, Any] = {
            "chat_id": chat_id,
            "title": title,
            "description": description,
            "payload": payload_str,
            "currency": currency,
            "prices": prices,
        }

        # provider_token can be empty string for Telegram Stars
        if provider_token is not None:
            payload["provider_token"] = provider_token

        if max_tip_amount is not None:
            payload["max_tip_amount"] = max_tip_amount
        if suggested_tip_amounts is not None:
            payload["suggested_tip_amounts"] = suggested_tip_amounts
        if start_parameter:
            payload["start_parameter"] = start_parameter
        if provider_data:
            payload["provider_data"] = provider_data
        if photo_url:
            payload["photo_url"] = photo_url
        if photo_size is not None:
            payload["photo_size"] = photo_size
        if photo_width is not None:
            payload["photo_width"] = photo_width
        if photo_height is not None:
            payload["photo_height"] = photo_height
        if need_name is not None:
            payload["need_name"] = need_name
        if need_phone_number is not None:
            payload["need_phone_number"] = need_phone_number
        if need_email is not None:
            payload["need_email"] = need_email
        if need_shipping_address is not None:
            payload["need_shipping_address"] = need_shipping_address
        if send_phone_number_to_provider is not None:
            payload["send_phone_number_to_provider"] = send_phone_number_to_provider
        if send_email_to_provider is not None:
            payload["send_email_to_provider"] = send_email_to_provider
        if is_flexible is not None:
            payload["is_flexible"] = is_flexible
        if reply_markup:
            payload["reply_markup"] = reply_markup

        return await self._send_with_retry("sendInvoice", payload, max_retries)
