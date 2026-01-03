"""Dynamic route registration for notification endpoints"""

import logging
from typing import Any

import aiohttp
from fastapi import FastAPI, Header, HTTPException, Request
from jinja2 import Template

from fastbotty.core.config import (
    AppConfig,
    ButtonConfig,
    EndpointConfig,
    ForceReply,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from fastbotty.core.interfaces import IPlugin

logger = logging.getLogger(__name__)


def _render_template(value: str, payload: dict[str, Any] | None) -> str:
    """Render Jinja2 template if payload is provided"""
    return Template(value).render(**payload) if payload else value


def build_reply_keyboard_markup(
    reply_keyboard: ReplyKeyboardMarkup, payload: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Build reply keyboard markup from config with template support.

    Returns a reply keyboard that replaces the user's keyboard with custom buttons.
    Supports text buttons and special request buttons (contact, location, poll, web_app).
    """
    keyboard = []
    for row in reply_keyboard.keyboard:
        keyboard_row = []
        for btn in row:
            if isinstance(btn, str):
                # Simple text button
                keyboard_row.append({"text": _render_template(btn, payload)})
            elif isinstance(btn, KeyboardButton):
                # KeyboardButton with optional special requests
                button: dict[str, Any] = {"text": _render_template(btn.text, payload)}
                if btn.request_contact is not None:
                    button["request_contact"] = btn.request_contact
                if btn.request_location is not None:
                    button["request_location"] = btn.request_location
                if btn.request_poll is not None:
                    button["request_poll"] = btn.request_poll
                if btn.web_app is not None:
                    button["web_app"] = {"url": _render_template(btn.web_app.url, payload)}
                keyboard_row.append(button)
        keyboard.append(keyboard_row)

    markup: dict[str, Any] = {"keyboard": keyboard}
    if reply_keyboard.is_persistent is not None:
        markup["is_persistent"] = reply_keyboard.is_persistent
    if reply_keyboard.resize_keyboard is not None:
        markup["resize_keyboard"] = reply_keyboard.resize_keyboard
    if reply_keyboard.one_time_keyboard is not None:
        markup["one_time_keyboard"] = reply_keyboard.one_time_keyboard
    if reply_keyboard.input_field_placeholder is not None:
        markup["input_field_placeholder"] = _render_template(
            reply_keyboard.input_field_placeholder, payload
        )
    if reply_keyboard.selective is not None:
        markup["selective"] = reply_keyboard.selective

    return markup


def build_reply_keyboard_remove(
    reply_keyboard_remove: ReplyKeyboardRemove,
) -> dict[str, Any]:
    """Build reply keyboard remove markup from config.

    Returns a markup that removes the reply keyboard.
    """
    markup: dict[str, Any] = {"remove_keyboard": reply_keyboard_remove.remove_keyboard}
    if reply_keyboard_remove.selective is not None:
        markup["selective"] = reply_keyboard_remove.selective
    return markup


def build_force_reply(
    force_reply: ForceReply, payload: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Build force reply markup from config with template support.

    Returns a markup that forces the user to reply to the message.
    """
    markup: dict[str, Any] = {"force_reply": force_reply.force_reply}
    if force_reply.input_field_placeholder is not None:
        markup["input_field_placeholder"] = _render_template(
            force_reply.input_field_placeholder, payload
        )
    if force_reply.selective is not None:
        markup["selective"] = force_reply.selective
    return markup


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
    - callback_game: Game callback (first button in first row only)
    - pay: Payment button (first button in first row only)

    Note: Pay and callback_game buttons must be the first button in the first row.
    """
    if not buttons:
        return None

    # Validate pay and callback_game button placement
    if buttons and buttons[0]:
        first_button = buttons[0][0]
        if first_button.pay or first_button.callback_game:
            # Pay and callback_game must be first button in first row
            pass
        else:
            # Check if pay or callback_game appears elsewhere (not allowed)
            for row_idx, row in enumerate(buttons):
                for btn_idx, btn in enumerate(row):
                    if btn.pay and (row_idx != 0 or btn_idx != 0):
                        raise ValueError("Pay button must be the first button in the first row")
                    if btn.callback_game and (row_idx != 0 or btn_idx != 0):
                        raise ValueError(
                            "Callback game button must be the first button in the first row"
                        )

    keyboard = []
    for row in buttons:
        keyboard_row = []
        for btn in row:
            # Render button text template if payload provided
            text = _render_template(btn.text, payload)

            # For pay buttons, replace ⭐️ and XTR with Telegram Star icon
            if btn.pay:
                text = text.replace("⭐️", "⭐")
                text = text.replace("XTR", "⭐")

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

            # Get media fields from payload
            document_url = get_field(payload, "document_url")
            video_url = get_field(payload, "video_url")
            audio_url = get_field(payload, "audio_url")
            voice_url = get_field(payload, "voice_url")
            location = get_field(payload, "location")

            # Build reply markup - prioritize inline keyboard, then reply keyboard types
            reply_markup = None
            if endpoint_config.buttons:
                reply_markup = build_inline_keyboard(endpoint_config.buttons, payload)
            elif endpoint_config.reply_keyboard:
                reply_markup = build_reply_keyboard_markup(endpoint_config.reply_keyboard, payload)
            elif endpoint_config.reply_keyboard_remove:
                reply_markup = build_reply_keyboard_remove(endpoint_config.reply_keyboard_remove)
            elif endpoint_config.force_reply:
                reply_markup = build_force_reply(endpoint_config.force_reply, payload)

            # Send to all target chats
            results = []
            for chat_id in target_chat_ids:
                # Determine message type and send accordingly
                # Check for invoice (if pay button is used)
                if endpoint_config.invoice:
                    # If there's a template or formatted message, send it first
                    # Then send the invoice as a separate message
                    if formatted_message and formatted_message.strip():
                        # Send the formatted message first (without buttons)
                        # The invoice will have the buttons with the pay button
                        await bot.send_message(
                            chat_id=chat_id,
                            text=formatted_message,
                            parse_mode=parse_mode,
                            reply_markup=None,  # No buttons on the message
                        )

                    # Render invoice fields with Jinja2 templates
                    invoice_title = _render_template(endpoint_config.invoice.title, payload)
                    invoice_description = _render_template(
                        endpoint_config.invoice.description, payload
                    )
                    invoice_payload = _render_template(endpoint_config.invoice.payload, payload)

                    # Prepare prices with template rendering
                    prices = []
                    for price in endpoint_config.invoice.prices:
                        label = _render_template(price.label, payload)
                        # Amount can be a template too
                        amount = price.amount
                        if isinstance(price.amount, str):
                            amount_str = _render_template(str(price.amount), payload)
                            amount = int(amount_str)
                        prices.append({"label": label, "amount": amount})

                    # Render max_tip_amount if it's a template string
                    max_tip_amount_config = endpoint_config.invoice.max_tip_amount
                    max_tip_amount: int | None = None
                    if max_tip_amount_config is not None:
                        if isinstance(max_tip_amount_config, str):
                            max_tip_amount_str = _render_template(max_tip_amount_config, payload)
                            max_tip_amount = int(max_tip_amount_str)
                        else:
                            max_tip_amount = max_tip_amount_config

                    # Render suggested_tip_amounts if any are template strings
                    suggested_tip_amounts_raw = endpoint_config.invoice.suggested_tip_amounts
                    suggested_tip_amounts: list[int] | None = None
                    if suggested_tip_amounts_raw:
                        rendered_tips: list[int] = []
                        for tip in suggested_tip_amounts_raw:
                            if isinstance(tip, str):
                                tip_str = _render_template(tip, payload)
                                rendered_tips.append(int(tip_str))
                            else:
                                rendered_tips.append(tip)
                        suggested_tip_amounts = rendered_tips

                    # Send invoice
                    result = await bot.send_invoice(
                        chat_id=chat_id,
                        title=invoice_title,
                        description=invoice_description,
                        payload_str=invoice_payload,
                        currency=endpoint_config.invoice.currency,
                        prices=prices,
                        provider_token=endpoint_config.invoice.provider_token or "",
                        max_tip_amount=max_tip_amount,
                        suggested_tip_amounts=suggested_tip_amounts,
                        start_parameter=endpoint_config.invoice.start_parameter,
                        provider_data=endpoint_config.invoice.provider_data,
                        photo_url=(
                            _render_template(endpoint_config.invoice.photo_url, payload)
                            if endpoint_config.invoice.photo_url
                            else None
                        ),
                        photo_size=endpoint_config.invoice.photo_size,
                        photo_width=endpoint_config.invoice.photo_width,
                        photo_height=endpoint_config.invoice.photo_height,
                        need_name=endpoint_config.invoice.need_name,
                        need_phone_number=endpoint_config.invoice.need_phone_number,
                        need_email=endpoint_config.invoice.need_email,
                        need_shipping_address=endpoint_config.invoice.need_shipping_address,
                        send_phone_number_to_provider=(
                            endpoint_config.invoice.send_phone_number_to_provider
                        ),
                        send_email_to_provider=endpoint_config.invoice.send_email_to_provider,
                        is_flexible=endpoint_config.invoice.is_flexible,
                        reply_markup=reply_markup,
                    )
                elif location:
                    # Send location
                    lat = location.get("latitude")
                    lon = location.get("longitude")
                    if lat is None or lon is None:
                        raise HTTPException(
                            status_code=400,
                            detail={
                                "error": "invalid_location",
                                "message": "Location must have latitude and longitude",
                            },
                        )
                    result = await bot.send_location(
                        chat_id=chat_id,
                        latitude=lat,
                        longitude=lon,
                        horizontal_accuracy=location.get("horizontal_accuracy"),
                        live_period=location.get("live_period"),
                        heading=location.get("heading"),
                        proximity_alert_radius=location.get("proximity_alert_radius"),
                        reply_markup=reply_markup,
                    )
                elif document_url:
                    # Send document
                    result = await bot.send_document(
                        chat_id=chat_id,
                        document_url=document_url,
                        caption=formatted_message,
                        parse_mode=parse_mode,
                        filename=get_field(payload, "filename"),
                        reply_markup=reply_markup,
                    )
                elif video_url:
                    # Send video
                    result = await bot.send_video(
                        chat_id=chat_id,
                        video_url=video_url,
                        caption=formatted_message,
                        parse_mode=parse_mode,
                        thumbnail_url=get_field(payload, "thumbnail_url"),
                        width=get_field(payload, "width"),
                        height=get_field(payload, "height"),
                        duration=get_field(payload, "duration"),
                        supports_streaming=get_field(payload, "supports_streaming"),
                        reply_markup=reply_markup,
                    )
                elif audio_url:
                    # Send audio
                    result = await bot.send_audio(
                        chat_id=chat_id,
                        audio_url=audio_url,
                        caption=formatted_message,
                        parse_mode=parse_mode,
                        duration=get_field(payload, "duration"),
                        performer=get_field(payload, "performer"),
                        title=get_field(payload, "title"),
                        thumbnail_url=get_field(payload, "thumbnail_url"),
                        reply_markup=reply_markup,
                    )
                elif voice_url:
                    # Send voice message
                    result = await bot.send_voice(
                        chat_id=chat_id,
                        voice_url=voice_url,
                        caption=formatted_message,
                        parse_mode=parse_mode,
                        duration=get_field(payload, "duration"),
                        reply_markup=reply_markup,
                    )
                elif image_urls:
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
