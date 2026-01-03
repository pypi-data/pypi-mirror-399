"""Tests for inline keyboard button types"""

from fastbotty.core.config import (
    ButtonConfig,
    CopyTextButton,
    LoginUrl,
    SwitchInlineQueryChosenChat,
    WebAppInfo,
)
from fastbotty.server.routes import build_inline_keyboard


class TestButtonConfig:
    """Tests for ButtonConfig model"""

    def test_url_button(self):
        """Test basic URL button"""
        btn = ButtonConfig(text="Click me", url="https://example.com")
        assert btn.text == "Click me"
        assert btn.url == "https://example.com"
        assert btn.callback_data is None

    def test_callback_data_button(self):
        """Test callback data button"""
        btn = ButtonConfig(text="Action", callback_data="action_1")
        assert btn.text == "Action"
        assert btn.callback_data == "action_1"
        assert btn.url is None

    def test_web_app_button(self):
        """Test web app button"""
        btn = ButtonConfig(text="Open App", web_app=WebAppInfo(url="https://app.example.com"))
        assert btn.text == "Open App"
        assert btn.web_app.url == "https://app.example.com"

    def test_login_url_button(self):
        """Test login URL button"""
        btn = ButtonConfig(
            text="Login",
            login_url=LoginUrl(
                url="https://login.example.com",
                forward_text="Continue",
                bot_username="my_bot",
                request_write_access=True,
            ),
        )
        assert btn.login_url.url == "https://login.example.com"
        assert btn.login_url.forward_text == "Continue"
        assert btn.login_url.bot_username == "my_bot"
        assert btn.login_url.request_write_access is True

    def test_switch_inline_query_button(self):
        """Test switch inline query button"""
        btn = ButtonConfig(text="Search", switch_inline_query="search term")
        assert btn.switch_inline_query == "search term"

    def test_switch_inline_query_empty_string(self):
        """Test switch inline query with empty string (valid)"""
        btn = ButtonConfig(text="Search", switch_inline_query="")
        assert btn.switch_inline_query == ""

    def test_switch_inline_query_current_chat_button(self):
        """Test switch inline query current chat button"""
        btn = ButtonConfig(text="Query here", switch_inline_query_current_chat="my query")
        assert btn.switch_inline_query_current_chat == "my query"

    def test_switch_inline_query_chosen_chat_button(self):
        """Test switch inline query chosen chat button"""
        btn = ButtonConfig(
            text="Choose chat",
            switch_inline_query_chosen_chat=SwitchInlineQueryChosenChat(
                query="default query",
                allow_user_chats=True,
                allow_bot_chats=False,
                allow_group_chats=True,
                allow_channel_chats=False,
            ),
        )
        assert btn.switch_inline_query_chosen_chat.query == "default query"
        assert btn.switch_inline_query_chosen_chat.allow_user_chats is True
        assert btn.switch_inline_query_chosen_chat.allow_bot_chats is False
        assert btn.switch_inline_query_chosen_chat.allow_group_chats is True
        assert btn.switch_inline_query_chosen_chat.allow_channel_chats is False

    def test_copy_text_button(self):
        """Test copy text button (Bot API 8.0+)"""
        btn = ButtonConfig(text="Copy", copy_text=CopyTextButton(text="Text to copy"))
        assert btn.copy_text.text == "Text to copy"

    def test_callback_game_button(self):
        """Test callback game button"""
        btn = ButtonConfig(text="Play Game", callback_game=True)
        assert btn.callback_game is True

    def test_pay_button(self):
        """Test pay button"""
        btn = ButtonConfig(text="Pay $10", pay=True)
        assert btn.pay is True


class TestBuildInlineKeyboard:
    """Tests for build_inline_keyboard function"""

    def test_empty_buttons(self):
        """Test empty button list returns None"""
        assert build_inline_keyboard([]) is None
        assert build_inline_keyboard(None) is None

    def test_url_button_keyboard(self):
        """Test building keyboard with URL button"""
        buttons = [[ButtonConfig(text="Visit", url="https://example.com")]]
        result = build_inline_keyboard(buttons)

        assert result == {"inline_keyboard": [[{"text": "Visit", "url": "https://example.com"}]]}

    def test_callback_data_button_keyboard(self):
        """Test building keyboard with callback data button"""
        buttons = [[ButtonConfig(text="Action", callback_data="do_action")]]
        result = build_inline_keyboard(buttons)

        assert result == {"inline_keyboard": [[{"text": "Action", "callback_data": "do_action"}]]}

    def test_web_app_button_keyboard(self):
        """Test building keyboard with web app button"""
        buttons = [[ButtonConfig(text="App", web_app=WebAppInfo(url="https://app.example.com"))]]
        result = build_inline_keyboard(buttons)

        assert result == {
            "inline_keyboard": [[{"text": "App", "web_app": {"url": "https://app.example.com"}}]]
        }

    def test_login_url_button_keyboard(self):
        """Test building keyboard with login URL button"""
        buttons = [
            [
                ButtonConfig(
                    text="Login",
                    login_url=LoginUrl(
                        url="https://login.example.com",
                        forward_text="Continue",
                        bot_username="test_bot",
                        request_write_access=True,
                    ),
                )
            ]
        ]
        result = build_inline_keyboard(buttons)

        assert result == {
            "inline_keyboard": [
                [
                    {
                        "text": "Login",
                        "login_url": {
                            "url": "https://login.example.com",
                            "forward_text": "Continue",
                            "bot_username": "test_bot",
                            "request_write_access": True,
                        },
                    }
                ]
            ]
        }

    def test_login_url_minimal_keyboard(self):
        """Test building keyboard with minimal login URL (only required field)"""
        buttons = [
            [ButtonConfig(text="Login", login_url=LoginUrl(url="https://login.example.com"))]
        ]
        result = build_inline_keyboard(buttons)

        assert result == {
            "inline_keyboard": [
                [{"text": "Login", "login_url": {"url": "https://login.example.com"}}]
            ]
        }

    def test_switch_inline_query_keyboard(self):
        """Test building keyboard with switch inline query button"""
        buttons = [[ButtonConfig(text="Search", switch_inline_query="search term")]]
        result = build_inline_keyboard(buttons)

        assert result == {
            "inline_keyboard": [[{"text": "Search", "switch_inline_query": "search term"}]]
        }

    def test_switch_inline_query_empty_keyboard(self):
        """Test building keyboard with empty switch inline query"""
        buttons = [[ButtonConfig(text="Search All", switch_inline_query="")]]
        result = build_inline_keyboard(buttons)

        assert result == {"inline_keyboard": [[{"text": "Search All", "switch_inline_query": ""}]]}

    def test_switch_inline_query_current_chat_keyboard(self):
        """Test building keyboard with switch inline query current chat button"""
        buttons = [[ButtonConfig(text="Query", switch_inline_query_current_chat="my query")]]
        result = build_inline_keyboard(buttons)

        assert result == {
            "inline_keyboard": [[{"text": "Query", "switch_inline_query_current_chat": "my query"}]]
        }

    def test_switch_inline_query_chosen_chat_keyboard(self):
        """Test building keyboard with switch inline query chosen chat button"""
        buttons = [
            [
                ButtonConfig(
                    text="Choose",
                    switch_inline_query_chosen_chat=SwitchInlineQueryChosenChat(
                        query="test",
                        allow_user_chats=True,
                        allow_group_chats=True,
                    ),
                )
            ]
        ]
        result = build_inline_keyboard(buttons)

        assert result == {
            "inline_keyboard": [
                [
                    {
                        "text": "Choose",
                        "switch_inline_query_chosen_chat": {
                            "query": "test",
                            "allow_user_chats": True,
                            "allow_group_chats": True,
                        },
                    }
                ]
            ]
        }

    def test_copy_text_button_keyboard(self):
        """Test building keyboard with copy text button"""
        buttons = [[ButtonConfig(text="Copy", copy_text=CopyTextButton(text="Copied text"))]]
        result = build_inline_keyboard(buttons)

        assert result == {
            "inline_keyboard": [[{"text": "Copy", "copy_text": {"text": "Copied text"}}]]
        }

    def test_callback_game_button_keyboard(self):
        """Test building keyboard with callback game button"""
        buttons = [[ButtonConfig(text="Play", callback_game=True)]]
        result = build_inline_keyboard(buttons)

        assert result == {"inline_keyboard": [[{"text": "Play", "callback_game": {}}]]}

    def test_pay_button_keyboard(self):
        """Test building keyboard with pay button"""
        buttons = [[ButtonConfig(text="Pay $10", pay=True)]]
        result = build_inline_keyboard(buttons)

        assert result == {"inline_keyboard": [[{"text": "Pay $10", "pay": True}]]}

    def test_pay_button_text_replacement(self):
        """Test pay button text with star icon replacement"""
        buttons = [[ButtonConfig(text="Pay 10 ⭐️", pay=True)]]
        result = build_inline_keyboard(buttons)

        assert result == {"inline_keyboard": [[{"text": "Pay 10 ⭐", "pay": True}]]}

    def test_pay_button_xtr_replacement(self):
        """Test pay button text with XTR replacement"""
        buttons = [[ButtonConfig(text="Pay 10 XTR", pay=True)]]
        result = build_inline_keyboard(buttons)

        assert result == {"inline_keyboard": [[{"text": "Pay 10 ⭐", "pay": True}]]}

    def test_pay_button_must_be_first(self):
        """Test that pay button must be first in first row"""
        import pytest

        # Pay button not in first position
        buttons = [
            [
                ButtonConfig(text="Other", callback_data="other"),
                ButtonConfig(text="Pay", pay=True),
            ]
        ]
        with pytest.raises(ValueError, match="Pay button must be the first button"):
            build_inline_keyboard(buttons)

    def test_pay_button_must_be_in_first_row(self):
        """Test that pay button must be in first row"""
        import pytest

        # Pay button in second row
        buttons = [
            [ButtonConfig(text="Other", callback_data="other")],
            [ButtonConfig(text="Pay", pay=True)],
        ]
        with pytest.raises(ValueError, match="Pay button must be the first button"):
            build_inline_keyboard(buttons)

    def test_callback_game_button_must_be_first(self):
        """Test that callback game button must be first in first row"""
        import pytest

        # Callback game button not in first position
        buttons = [
            [
                ButtonConfig(text="Other", callback_data="other"),
                ButtonConfig(text="Play", callback_game=True),
            ]
        ]
        with pytest.raises(ValueError, match="Callback game button must be the first button"):
            build_inline_keyboard(buttons)

    def test_multiple_rows_keyboard(self):
        """Test building keyboard with multiple rows"""
        buttons = [
            [
                ButtonConfig(text="Button 1", callback_data="btn1"),
                ButtonConfig(text="Button 2", callback_data="btn2"),
            ],
            [ButtonConfig(text="Link", url="https://example.com")],
        ]
        result = build_inline_keyboard(buttons)

        assert result == {
            "inline_keyboard": [
                [
                    {"text": "Button 1", "callback_data": "btn1"},
                    {"text": "Button 2", "callback_data": "btn2"},
                ],
                [{"text": "Link", "url": "https://example.com"}],
            ]
        }

    def test_mixed_button_types_keyboard(self):
        """Test building keyboard with different button types in same keyboard"""
        buttons = [
            [
                ButtonConfig(text="URL", url="https://example.com"),
                ButtonConfig(text="Callback", callback_data="action"),
            ],
            [
                ButtonConfig(text="Web App", web_app=WebAppInfo(url="https://app.example.com")),
                ButtonConfig(text="Copy", copy_text=CopyTextButton(text="Copy me")),
            ],
        ]
        result = build_inline_keyboard(buttons)

        assert result == {
            "inline_keyboard": [
                [
                    {"text": "URL", "url": "https://example.com"},
                    {"text": "Callback", "callback_data": "action"},
                ],
                [
                    {"text": "Web App", "web_app": {"url": "https://app.example.com"}},
                    {"text": "Copy", "copy_text": {"text": "Copy me"}},
                ],
            ]
        }


class TestButtonTemplateRendering:
    """Tests for Jinja2 template rendering in buttons"""

    def test_url_template_rendering(self):
        """Test URL field template rendering"""
        buttons = [[ButtonConfig(text="Order #{{ order_id }}", url="https://example.com/{{ id }}")]]
        payload = {"order_id": 123, "id": 456}
        result = build_inline_keyboard(buttons, payload)

        assert result == {
            "inline_keyboard": [[{"text": "Order #123", "url": "https://example.com/456"}]]
        }

    def test_callback_data_template_rendering(self):
        """Test callback_data field template rendering"""
        buttons = [[ButtonConfig(text="Confirm", callback_data="confirm_{{ order_id }}")]]
        payload = {"order_id": 789}
        result = build_inline_keyboard(buttons, payload)

        assert result == {
            "inline_keyboard": [[{"text": "Confirm", "callback_data": "confirm_789"}]]
        }

    def test_web_app_url_template_rendering(self):
        """Test web app URL template rendering"""
        buttons = [
            [
                ButtonConfig(
                    text="Open App",
                    web_app=WebAppInfo(url="https://app.example.com/user/{{ user_id }}"),
                )
            ]
        ]
        payload = {"user_id": "abc123"}
        result = build_inline_keyboard(buttons, payload)

        assert result == {
            "inline_keyboard": [
                [{"text": "Open App", "web_app": {"url": "https://app.example.com/user/abc123"}}]
            ]
        }

    def test_login_url_template_rendering(self):
        """Test login URL template rendering"""
        buttons = [
            [
                ButtonConfig(
                    text="Login",
                    login_url=LoginUrl(
                        url="https://login.example.com?user={{ user_id }}",
                        forward_text="Welcome {{ name }}",
                    ),
                )
            ]
        ]
        payload = {"user_id": 123, "name": "John"}
        result = build_inline_keyboard(buttons, payload)

        assert result == {
            "inline_keyboard": [
                [
                    {
                        "text": "Login",
                        "login_url": {
                            "url": "https://login.example.com?user=123",
                            "forward_text": "Welcome John",
                        },
                    }
                ]
            ]
        }

    def test_switch_inline_query_template_rendering(self):
        """Test switch inline query template rendering"""
        buttons = [[ButtonConfig(text="Search", switch_inline_query="{{ product_name }}")]]
        payload = {"product_name": "laptop"}
        result = build_inline_keyboard(buttons, payload)

        assert result == {
            "inline_keyboard": [[{"text": "Search", "switch_inline_query": "laptop"}]]
        }

    def test_switch_inline_query_chosen_chat_template_rendering(self):
        """Test switch inline query chosen chat template rendering"""
        buttons = [
            [
                ButtonConfig(
                    text="Share",
                    switch_inline_query_chosen_chat=SwitchInlineQueryChosenChat(
                        query="Check out {{ product }}",
                        allow_user_chats=True,
                    ),
                )
            ]
        ]
        payload = {"product": "awesome item"}
        result = build_inline_keyboard(buttons, payload)

        assert result == {
            "inline_keyboard": [
                [
                    {
                        "text": "Share",
                        "switch_inline_query_chosen_chat": {
                            "query": "Check out awesome item",
                            "allow_user_chats": True,
                        },
                    }
                ]
            ]
        }

    def test_copy_text_template_rendering(self):
        """Test copy text template rendering"""
        buttons = [
            [ButtonConfig(text="Copy Code", copy_text=CopyTextButton(text="CODE-{{ code }}"))]
        ]
        payload = {"code": "XYZ789"}
        result = build_inline_keyboard(buttons, payload)

        assert result == {
            "inline_keyboard": [[{"text": "Copy Code", "copy_text": {"text": "CODE-XYZ789"}}]]
        }

    def test_no_payload_no_rendering(self):
        """Test that buttons work without payload (no template rendering)"""
        buttons = [[ButtonConfig(text="Static {{ text }}", url="https://example.com/{{ id }}")]]
        result = build_inline_keyboard(buttons, None)

        # Without payload, templates are rendered with empty context
        # Jinja2 will treat undefined variables as empty strings in simple cases
        assert result is not None
        assert "inline_keyboard" in result
