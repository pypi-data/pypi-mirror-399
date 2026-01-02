"""Tests for reply keyboard markup functionality"""

from fastbotty.core.config import (
    ForceReply,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    WebAppInfo,
)
from fastbotty.server.routes import (
    build_force_reply,
    build_reply_keyboard_markup,
    build_reply_keyboard_remove,
)


def test_build_reply_keyboard_markup_simple():
    """Test building simple reply keyboard with text buttons"""
    config = ReplyKeyboardMarkup(
        keyboard=[
            ["👍 Good", "👎 Bad"],
            ["📝 Feedback"],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

    result = build_reply_keyboard_markup(config)

    assert result["keyboard"] == [
        [{"text": "👍 Good"}, {"text": "👎 Bad"}],
        [{"text": "📝 Feedback"}],
    ]
    assert result["resize_keyboard"] is True
    assert result["one_time_keyboard"] is True


def test_build_reply_keyboard_markup_with_template():
    """Test building reply keyboard with Jinja2 template rendering"""
    config = ReplyKeyboardMarkup(
        keyboard=[
            ["Order #{{ order_id }}", "Cancel #{{ order_id }}"],
        ],
        resize_keyboard=True,
    )

    payload = {"order_id": "12345"}
    result = build_reply_keyboard_markup(config, payload)

    assert result["keyboard"] == [
        [{"text": "Order #12345"}, {"text": "Cancel #12345"}],
    ]


def test_build_reply_keyboard_markup_with_keyboard_buttons():
    """Test building reply keyboard with KeyboardButton objects"""
    config = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📞 Share Contact", request_contact=True),
                KeyboardButton(text="📍 Share Location", request_location=True),
            ],
            [
                KeyboardButton(
                    text="🚀 Open App",
                    web_app=WebAppInfo(url="https://example.com/app"),
                ),
            ],
        ],
        resize_keyboard=True,
    )

    result = build_reply_keyboard_markup(config)

    assert result["keyboard"][0][0] == {
        "text": "📞 Share Contact",
        "request_contact": True,
    }
    assert result["keyboard"][0][1] == {
        "text": "📍 Share Location",
        "request_location": True,
    }
    assert result["keyboard"][1][0] == {
        "text": "🚀 Open App",
        "web_app": {"url": "https://example.com/app"},
    }


def test_build_reply_keyboard_markup_with_placeholder():
    """Test reply keyboard with input field placeholder"""
    config = ReplyKeyboardMarkup(
        keyboard=[["Yes", "No"]],
        input_field_placeholder="Choose an option...",
        resize_keyboard=True,
    )

    result = build_reply_keyboard_markup(config)

    assert result["input_field_placeholder"] == "Choose an option..."


def test_build_reply_keyboard_markup_selective():
    """Test reply keyboard with selective option"""
    config = ReplyKeyboardMarkup(
        keyboard=[["Option 1", "Option 2"]],
        selective=True,
    )

    result = build_reply_keyboard_markup(config)

    assert result["selective"] is True


def test_build_reply_keyboard_markup_persistent():
    """Test reply keyboard with persistent option"""
    config = ReplyKeyboardMarkup(
        keyboard=[["Menu", "Help"]],
        is_persistent=True,
    )

    result = build_reply_keyboard_markup(config)

    assert result["is_persistent"] is True


def test_build_reply_keyboard_remove():
    """Test building reply keyboard remove markup"""
    config = ReplyKeyboardRemove(remove_keyboard=True)

    result = build_reply_keyboard_remove(config)

    assert result["remove_keyboard"] is True


def test_build_reply_keyboard_remove_selective():
    """Test reply keyboard remove with selective option"""
    config = ReplyKeyboardRemove(remove_keyboard=True, selective=True)

    result = build_reply_keyboard_remove(config)

    assert result["remove_keyboard"] is True
    assert result["selective"] is True


def test_build_force_reply():
    """Test building force reply markup"""
    config = ForceReply(force_reply=True)

    result = build_force_reply(config)

    assert result["force_reply"] is True


def test_build_force_reply_with_placeholder():
    """Test force reply with input field placeholder"""
    config = ForceReply(
        force_reply=True,
        input_field_placeholder="Type your answer...",
    )

    result = build_force_reply(config)

    assert result["force_reply"] is True
    assert result["input_field_placeholder"] == "Type your answer..."


def test_build_force_reply_with_template():
    """Test force reply with template rendering"""
    config = ForceReply(
        force_reply=True,
        input_field_placeholder="Enter {{ field_name }}...",
    )

    payload = {"field_name": "your email"}
    result = build_force_reply(config, payload)

    assert result["input_field_placeholder"] == "Enter your email..."


def test_build_force_reply_selective():
    """Test force reply with selective option"""
    config = ForceReply(force_reply=True, selective=True)

    result = build_force_reply(config)

    assert result["force_reply"] is True
    assert result["selective"] is True


def test_reply_keyboard_mixed_buttons():
    """Test reply keyboard with mixed string and KeyboardButton objects"""
    config = ReplyKeyboardMarkup(
        keyboard=[
            ["Simple Text"],
            [KeyboardButton(text="📞 Contact", request_contact=True)],
        ],
    )

    result = build_reply_keyboard_markup(config)

    assert result["keyboard"][0][0] == {"text": "Simple Text"}
    assert result["keyboard"][1][0] == {
        "text": "📞 Contact",
        "request_contact": True,
    }


def test_reply_keyboard_with_poll_request():
    """Test reply keyboard with request_poll option"""
    config = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="📊 Create Poll",
                    request_poll={"type": "quiz"},
                )
            ],
        ],
    )

    result = build_reply_keyboard_markup(config)

    assert result["keyboard"][0][0] == {
        "text": "📊 Create Poll",
        "request_poll": {"type": "quiz"},
    }


def test_reply_keyboard_web_app_with_template():
    """Test reply keyboard with web_app URL template"""
    config = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="Open Dashboard",
                    web_app=WebAppInfo(url="https://example.com/user/{{ user_id }}"),
                )
            ],
        ],
    )

    payload = {"user_id": "123"}
    result = build_reply_keyboard_markup(config, payload)

    assert result["keyboard"][0][0] == {
        "text": "Open Dashboard",
        "web_app": {"url": "https://example.com/user/123"},
    }
