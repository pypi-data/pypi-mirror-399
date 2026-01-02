"""Configuration models using Pydantic"""

import os
from typing import Any

from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator, model_validator

# Load .env file
load_dotenv()


def resolve_env_var(value: Any) -> Any:
    """Resolve environment variable with better error messages"""
    if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
        env_var = value[2:-1]
        # Support default values: ${VAR:-default}
        if ":-" in env_var:
            var_name, default_value = env_var.split(":-", 1)
            resolved: str | None = os.getenv(var_name, default_value)
        else:
            resolved = os.getenv(env_var)
            if resolved is None:
                raise ValueError(
                    f"Environment variable '{env_var}' is not set. "
                    f"Please set it in .env file or export {env_var}=your_value"
                )
        return resolved
    elif isinstance(value, list):
        return [resolve_env_var(item) for item in value]
    elif isinstance(value, dict):
        return {k: resolve_env_var(v) for k, v in value.items()}
    return value


class EnvVarMixin:
    """Mixin to add env var resolution to all fields"""

    @model_validator(mode="before")
    @classmethod
    def resolve_env_vars(cls, values: Any) -> Any:
        if isinstance(values, dict):
            return {k: resolve_env_var(v) for k, v in values.items()}
        return values


class BotConfig(BaseModel, EnvVarMixin):
    """Telegram bot configuration"""

    token: str = Field(..., description="Telegram bot token")
    test_mode: bool = Field(default=False, description="Enable test mode")
    webhook_url: str | None = Field(default=None, description="Public URL for webhook")
    webhook_path: str = Field(default="/bot/webhook", description="Webhook endpoint path")


class WebAppInfo(BaseModel):
    """Web App info for inline keyboard button"""

    url: str = Field(..., description="HTTPS URL of Web App to open")


class LoginUrl(BaseModel):
    """Login URL configuration for inline keyboard button"""

    url: str = Field(..., description="HTTPS URL for auto-authorization")
    forward_text: str | None = Field(default=None, description="New text of the forward button")
    bot_username: str | None = Field(default=None, description="Username of bot for authorization")
    request_write_access: bool | None = Field(
        default=None, description="Request permission to send messages"
    )


class SwitchInlineQueryChosenChat(BaseModel):
    """Filter for switch_inline_query_chosen_chat"""

    query: str | None = Field(default=None, description="Default inline query")
    allow_user_chats: bool | None = Field(default=None, description="Allow private chats")
    allow_bot_chats: bool | None = Field(default=None, description="Allow bot chats")
    allow_group_chats: bool | None = Field(default=None, description="Allow group chats")
    allow_channel_chats: bool | None = Field(default=None, description="Allow channel chats")


class CopyTextButton(BaseModel):
    """Copy text configuration for inline keyboard button"""

    text: str = Field(..., description="Text to copy to clipboard")


class ButtonConfig(BaseModel, EnvVarMixin):
    """Configuration for inline keyboard button.

    Only one of url, callback_data, web_app, login_url, switch_inline_query,
    switch_inline_query_current_chat, switch_inline_query_chosen_chat, copy_text,
    callback_game, or pay must be specified.
    """

    text: str = Field(..., description="Button text")
    url: str | None = Field(default=None, description="HTTP/HTTPS URL to open")
    callback_data: str | None = Field(
        default=None, description="Data sent in callback query (1-64 bytes)"
    )
    web_app: WebAppInfo | None = Field(
        default=None, description="Web App to launch when button is pressed"
    )
    login_url: LoginUrl | None = Field(
        default=None, description="HTTPS URL for auto-authorization via Telegram Login"
    )
    switch_inline_query: str | None = Field(
        default=None, description="Prompt user to select chat and insert bot's username + query"
    )
    switch_inline_query_current_chat: str | None = Field(
        default=None, description="Insert bot's username + query in current chat's input field"
    )
    switch_inline_query_chosen_chat: SwitchInlineQueryChosenChat | None = Field(
        default=None, description="Prompt user to select chat with specified types + insert query"
    )
    copy_text: CopyTextButton | None = Field(
        default=None, description="Copy specified text to clipboard when pressed (Bot API 8.0+)"
    )
    callback_game: bool | None = Field(
        default=None, description="Set to true to send a callback game (first button in row only)"
    )
    pay: bool | None = Field(
        default=None, description="Set to true for Pay button (first button in row only)"
    )


class EndpointConfig(BaseModel, EnvVarMixin):
    """Configuration for a single notification endpoint"""

    path: str = Field(..., description="API endpoint path")
    chat_id: str | None = Field(default=None, description="Telegram chat ID or username")
    chat_ids: list[str] = Field(default_factory=list, description="Multiple chat IDs")
    formatter: str = Field(default="plain", description="Formatter to use")
    template: str | None = Field(default=None, description="Template name to use")
    parse_mode: str | None = Field(default=None, description="Telegram parse mode")
    plugin_config: dict[str, Any] = Field(default_factory=dict)
    labels: dict[str, str] = Field(default_factory=dict, description="Custom labels for keys")
    field_map: dict[str, str] = Field(
        default_factory=dict, description="Map payload fields to internal fields"
    )
    buttons: list[list[ButtonConfig]] = Field(
        default_factory=list, description="Inline keyboard buttons (rows)"
    )

    @field_validator("path")
    @classmethod
    def validate_path(cls, v: str) -> str:
        if not v.startswith("/"):
            return f"/{v}"
        return v

    @field_validator("chat_id")
    @classmethod
    def validate_chat_id(cls, v: str | None) -> str | None:
        if v is None:
            return v

        import logging

        logger = logging.getLogger(__name__)

        if v.startswith("@"):
            return v
        try:
            chat_id_int = int(v)
            if chat_id_int > 0 and len(v) > 10:
                logger.warning(
                    f"chat_id '{v}' looks like a channel ID but is positive. "
                    f"Did you mean '-100{v}'?"
                )
        except ValueError:
            logger.warning(f"chat_id '{v}' is not a valid numeric ID or @username")
        return v

    def get_chat_ids(self) -> list[str]:
        """Get all chat IDs (combines chat_id and chat_ids)"""
        ids = list(self.chat_ids)
        if self.chat_id:
            ids.insert(0, self.chat_id)
        return ids


class ServerConfig(BaseModel, EnvVarMixin):
    """Server configuration"""

    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    api_key: str | None = Field(default=None, description="API key for authentication")
    cors_origins: list[str] = Field(default=["*"], description="CORS allowed origins")


class LoggingConfig(BaseModel, EnvVarMixin):
    """Logging configuration"""

    level: str = Field(default="INFO", description="Log level")
    format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format",
    )


class CallbackConfig(BaseModel, EnvVarMixin):
    """Configuration for button callback handlers"""

    data: str = Field(..., description="Callback data to match")
    response: str | None = Field(default=None, description="Text response to send")
    url: str | None = Field(default=None, description="URL to POST callback to")


class CommandConfig(BaseModel, EnvVarMixin):
    """Configuration for bot command handlers"""

    command: str = Field(..., description="Command to match (e.g., /start, /help)")
    response: str | None = Field(default=None, description="Text response (supports Jinja2)")
    parse_mode: str | None = Field(default=None, description="Parse mode for response")
    buttons: list[list[ButtonConfig]] = Field(default_factory=list, description="Optional buttons")


class AppConfig(BaseModel, EnvVarMixin):
    """Root configuration model"""

    bot: BotConfig
    endpoints: list[EndpointConfig]
    templates: dict[str, str] = Field(default_factory=dict, description="Message templates")
    callbacks: list[CallbackConfig] = Field(
        default_factory=list, description="Button callback handlers"
    )
    commands: list[CommandConfig] = Field(default_factory=list, description="Bot command handlers")
    server: ServerConfig = Field(default_factory=ServerConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
