"""Dynamic route registration for notification endpoints"""

import logging
from typing import Any

import aiohttp
from fastapi import FastAPI, Header, HTTPException, Request
from jinja2 import Template

from fastbotty.core.config import AppConfig, ButtonConfig, EndpointConfig
from fastbotty.core.interfaces import IPlugin

logger = logging.getLogger(__name__)


def _render_template(value: str, payload: dict[str, Any] | None) -> str:
    """Render Jinja2 template if payload is provided"""
    return Template(value).render(**payload) if payload else value


def build_inline_keyboard(
    buttons: list[list[ButtonConfig]], payload: dict[str, Any] | None = None
) -> dict[str, Any] | None:
    """Build inline keyboard markup from button config with template support.

    Supports all Telegram inline keyboard button types:
    - url: HTTP/HTTPS URL to open
    - callback_data: Data sent in callback query
    - web_app: Web App to launch
    - login_url: Auto-authorization URL via Telegram Login
    - switch_inline_query: Prompt user to select chat for inline query
    - switch_inline_query_current_chat: Insert inline query in current chat
    - switch_inline_query_chosen_chat: Choose specific chat type for inline query
    - copy_text: Copy text to clipboard (Bot API 8.0+)
    - callback_game: Game callback (first button in row only)
    - pay: Payment button (first button in row only)
    """
    if not buttons:
        return None

    keyboard = []
    for row in buttons:
        keyboard_row = []
        for btn in row:
            # Render button text template if payload provided
            text = _render_template(btn.text, payload)
            button: dict[str, Any] = {"text": text}

            # Handle all button types (mutually exclusive)
            if btn.url:
                button["url"] = _render_template(btn.url, payload)
            elif btn.callback_data:
                button["callback_data"] = _render_template(btn.callback_data, payload)
            elif btn.web_app:
                button["web_app"] = {"url": _render_template(btn.web_app.url, payload)}
            elif btn.login_url:
                login_url_obj: dict[str, Any] = {
                    "url": _render_template(btn.login_url.url, payload)
                }
                if btn.login_url.forward_text:
                    login_url_obj["forward_text"] = _render_template(
                        btn.login_url.forward_text, payload
                    )
                if btn.login_url.bot_username:
                    login_url_obj["bot_username"] = btn.login_url.bot_username
                if btn.login_url.request_write_access is not None:
                    login_url_obj["request_write_access"] = btn.login_url.request_write_access
                button["login_url"] = login_url_obj
            # Note: switch_inline_query fields use `is not None` because empty string "" is a
            # valid value meaning "any query", distinct from None (not set)
            elif btn.switch_inline_query is not None:
                button["switch_inline_query"] = _render_template(btn.switch_inline_query, payload)
            elif btn.switch_inline_query_current_chat is not None:
                button["switch_inline_query_current_chat"] = _render_template(
                    btn.switch_inline_query_current_chat, payload
                )
            elif btn.switch_inline_query_chosen_chat:
                chosen_chat: dict[str, Any] = {}
                if btn.switch_inline_query_chosen_chat.query is not None:
                    chosen_chat["query"] = _render_template(
                        btn.switch_inline_query_chosen_chat.query, payload
                    )
                if btn.switch_inline_query_chosen_chat.allow_user_chats is not None:
                    chosen_chat["allow_user_chats"] = (
                        btn.switch_inline_query_chosen_chat.allow_user_chats
                    )
                if btn.switch_inline_query_chosen_chat.allow_bot_chats is not None:
                    chosen_chat["allow_bot_chats"] = (
                        btn.switch_inline_query_chosen_chat.allow_bot_chats
                    )
                if btn.switch_inline_query_chosen_chat.allow_group_chats is not None:
                    chosen_chat["allow_group_chats"] = (
                        btn.switch_inline_query_chosen_chat.allow_group_chats
                    )
                if btn.switch_inline_query_chosen_chat.allow_channel_chats is not None:
                    chosen_chat["allow_channel_chats"] = (
                        btn.switch_inline_query_chosen_chat.allow_channel_chats
                    )
                button["switch_inline_query_chosen_chat"] = chosen_chat
            elif btn.copy_text:
                button["copy_text"] = {"text": _render_template(btn.copy_text.text, payload)}
            elif btn.callback_game:
                # callback_game is an empty object when set
                button["callback_game"] = {}
            elif btn.pay:
                button["pay"] = True

            keyboard_row.append(button)
        keyboard.append(keyboard_row)

    return {"inline_keyboard": keyboard}


def setup_routes(app: FastAPI) -> None:
    """Setup dynamic routes based on configuration"""
    config = app.state.config
    bot = app.state.bot
    registry = app.state.registry
    templates = app.state.templates

    for endpoint_config in config.endpoints:
        create_endpoint_handler(
            app, endpoint_config, bot, registry, config.server.api_key, templates
        )

    # Setup webhook endpoint if configured
    if config.bot.webhook_url:
        setup_webhook_handler(app, bot, config)


def create_endpoint_handler(
    app: FastAPI,
    endpoint_config: EndpointConfig,
    bot: Any,
    registry: Any,
    api_key: str | None,
    templates: dict[str, str],
) -> None:
    """Create handler for a specific endpoint"""

    def get_field(payload: dict[str, Any], field: str, default: Any = None) -> Any:
        """Get field value using field_map or direct access"""
        mapped = endpoint_config.field_map.get(field)
        if mapped:
            # Support nested fields with dot notation
            value: Any = payload
            for key in mapped.split("."):
                if isinstance(value, dict):
                    value = value.get(key)
                else:
                    return default
            return value if value is not None else default
        return payload.get(field, default)

    def render_template(template_str: str, payload: dict[str, Any], parse_mode: str | None) -> str:
        """Render Jinja2 template with payload values"""
        # Escaping is handled by sanitize_text in bot.py, so pass payload as-is to Jinja2
        return Template(template_str).render(**payload)

    async def handler(
        payload: dict[str, Any],
        x_api_key: str | None = Header(None),
    ) -> dict[str, Any]:
        if api_key and x_api_key != api_key:
            raise HTTPException(
                status_code=401,
                detail={"error": "invalid_api_key", "message": "Invalid or missing API key"},
            )

        try:
            # Get chat IDs from payload or config
            payload_chat_id = get_field(payload, "chat_id")
            payload_chat_ids = get_field(payload, "chat_ids", [])

            if payload_chat_ids:
                target_chat_ids = payload_chat_ids
            elif payload_chat_id:
                target_chat_ids = [payload_chat_id]
            else:
                target_chat_ids = endpoint_config.get_chat_ids()

            if not target_chat_ids:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "no_chat_id",
                        "message": "No chat_id specified in config or request",
                    },
                )

            # Use template if specified, otherwise use formatter
            parse_mode = get_field(payload, "parse_mode") or endpoint_config.parse_mode

            if endpoint_config.template and endpoint_config.template in templates:
                formatted_message = render_template(
                    templates[endpoint_config.template], payload, parse_mode
                )
            else:
                formatter = registry.get_formatter(endpoint_config.formatter)
                if not formatter:
                    raise HTTPException(
                        status_code=500,
                        detail={
                            "error": "formatter_not_found",
                            "message": f"Formatter '{endpoint_config.formatter}' not found",
                        },
                    )

                if hasattr(formatter, "labels"):
                    formatter.labels = endpoint_config.labels

                if isinstance(formatter, IPlugin):
                    formatted_message = formatter.format(payload, endpoint_config.plugin_config)
                else:
                    formatted_message = formatter.format(payload)

            image_url = get_field(payload, "image_url")
            image_urls = get_field(payload, "image_urls", [])

            # Build inline keyboard if buttons configured
            reply_markup = build_inline_keyboard(endpoint_config.buttons, payload)

            # Send to all target chats
            results = []
            for chat_id in target_chat_ids:
                if image_urls:
                    result = await bot.send_media_group(
                        chat_id=chat_id,
                        photo_urls=image_urls,
                        caption=formatted_message,
                        parse_mode=parse_mode,
                    )
                elif image_url:
                    result = await bot.send_photo(
                        chat_id=chat_id,
                        photo_url=image_url,
                        caption=formatted_message,
                        parse_mode=parse_mode,
                    )
                else:
                    result = await bot.send_message(
                        chat_id=chat_id,
                        text=formatted_message,
                        parse_mode=parse_mode,
                        reply_markup=reply_markup,
                    )

                msg_id = (
                    result.get("result", {}).get("message_id")
                    if isinstance(result.get("result"), dict)
                    else result.get("result", [{}])[0].get("message_id")
                )
                results.append({"chat_id": chat_id, "message_id": msg_id})
                logger.info(f"Notification sent to {chat_id}")

            return {
                "status": "sent",
                "results": results,
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to send notification: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail={"error": "send_failed", "message": str(e)})

    app.post(endpoint_config.path)(handler)
    logger.info(f"Registered endpoint: {endpoint_config.path}")


def setup_webhook_handler(app: FastAPI, bot: Any, config: AppConfig) -> None:
    """Setup webhook endpoint for receiving Telegram updates"""

    async def webhook_handler(request: Request) -> dict[str, Any]:
        """Handle incoming Telegram webhook updates"""
        try:
            update = await request.json()
            logger.debug(f"Received webhook update: {update}")

            # Handle callback queries (button clicks)
            if "callback_query" in update:
                callback = update["callback_query"]
                callback_id = callback["id"]
                callback_data = callback.get("data", "")
                user = callback.get("from", {})

                logger.info(f"Callback query: {callback_data} from user {user.get('id')}")

                # Find matching callback handler
                for callback_handler in config.callbacks:
                    if callback_handler.data == callback_data:
                        await bot.answer_callback_query(callback_id, callback_handler.response)

                        if callback_handler.url:
                            async with aiohttp.ClientSession() as session:
                                await session.post(
                                    callback_handler.url,
                                    json={
                                        "callback_data": callback_data,
                                        "user": user,
                                        "message": callback.get("message", {}),
                                    },
                                )
                        break
                else:
                    await bot.answer_callback_query(callback_id)

            # Handle messages (including commands)
            elif "message" in update:
                message = update["message"]
                chat_id = str(message["chat"]["id"])
                user = message.get("from", {})
                text = message.get("text", "")

                # Check for commands
                if text.startswith("/"):
                    command = text.split()[0].split("@")[0]  # Handle /cmd@botname
                    logger.info(f"Command: {command} from user {user.get('id')}")

                    for handler in config.commands:
                        if handler.command == command:
                            # Render response with user context
                            context = {
                                "user": user,
                                "chat_id": chat_id,
                                "first_name": user.get("first_name", ""),
                                "username": user.get("username", ""),
                                "command": command,
                            }

                            response_text = (
                                Template(handler.response).render(**context)
                                if handler.response
                                else None
                            )

                            if response_text:
                                reply_markup = (
                                    build_inline_keyboard(handler.buttons, context)
                                    if handler.buttons
                                    else None
                                )
                                await bot.send_message(
                                    chat_id=chat_id,
                                    text=response_text,
                                    parse_mode=handler.parse_mode,
                                    reply_markup=reply_markup,
                                )
                            break

            return {"ok": True}

        except Exception as e:
            logger.error(f"Webhook error: {e}", exc_info=True)
            return {"ok": False, "error": str(e)}

    app.post(config.bot.webhook_path)(webhook_handler)
    logger.info(f"Registered webhook endpoint: {config.bot.webhook_path}")
