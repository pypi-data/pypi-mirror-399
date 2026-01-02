"""Tests for new message types: documents, videos, audio, voice, and locations"""

import pytest

from fastbotty.core.bot import TelegramBot


@pytest.mark.asyncio
async def test_send_document_test_mode():
    """Test sending document in test mode"""
    bot = TelegramBot(token="test_token", test_mode=True)
    result = await bot.send_document(
        chat_id="123",
        document_url="https://example.com/report.pdf",
        caption="Monthly report",
        filename="report_dec_2024.pdf",
    )

    assert result["ok"] is True
    assert "result" in result


@pytest.mark.asyncio
async def test_send_document_with_reply_markup():
    """Test sending document with inline keyboard"""
    bot = TelegramBot(token="test_token", test_mode=True)
    reply_markup = {"inline_keyboard": [[{"text": "View", "url": "https://example.com"}]]}
    result = await bot.send_document(
        chat_id="123",
        document_url="https://example.com/doc.pdf",
        caption="Document",
        reply_markup=reply_markup,
    )

    assert result["ok"] is True


@pytest.mark.asyncio
async def test_send_video_test_mode():
    """Test sending video in test mode"""
    bot = TelegramBot(token="test_token", test_mode=True)
    result = await bot.send_video(
        chat_id="123",
        video_url="https://example.com/demo.mp4",
        caption="Product demo",
        thumbnail_url="https://example.com/thumb.jpg",
        width=1920,
        height=1080,
        duration=120,
        supports_streaming=True,
    )

    assert result["ok"] is True
    assert "result" in result


@pytest.mark.asyncio
async def test_send_video_minimal():
    """Test sending video with minimal parameters"""
    bot = TelegramBot(token="test_token", test_mode=True)
    result = await bot.send_video(
        chat_id="123",
        video_url="https://example.com/video.mp4",
    )

    assert result["ok"] is True


@pytest.mark.asyncio
async def test_send_audio_test_mode():
    """Test sending audio in test mode"""
    bot = TelegramBot(token="test_token", test_mode=True)
    result = await bot.send_audio(
        chat_id="123",
        audio_url="https://example.com/podcast.mp3",
        caption="Episode 42",
        title="Tech Talk",
        performer="TechTalk Podcast",
        duration=3600,
        thumbnail_url="https://example.com/thumb.jpg",
    )

    assert result["ok"] is True
    assert "result" in result


@pytest.mark.asyncio
async def test_send_audio_minimal():
    """Test sending audio with minimal parameters"""
    bot = TelegramBot(token="test_token", test_mode=True)
    result = await bot.send_audio(
        chat_id="123",
        audio_url="https://example.com/song.mp3",
    )

    assert result["ok"] is True


@pytest.mark.asyncio
async def test_send_voice_test_mode():
    """Test sending voice message in test mode"""
    bot = TelegramBot(token="test_token", test_mode=True)
    result = await bot.send_voice(
        chat_id="123",
        voice_url="https://example.com/voice.ogg",
        caption="Voice message",
        duration=30,
    )

    assert result["ok"] is True
    assert "result" in result


@pytest.mark.asyncio
async def test_send_voice_minimal():
    """Test sending voice with minimal parameters"""
    bot = TelegramBot(token="test_token", test_mode=True)
    result = await bot.send_voice(
        chat_id="123",
        voice_url="https://example.com/voice.ogg",
    )

    assert result["ok"] is True


@pytest.mark.asyncio
async def test_send_location_test_mode():
    """Test sending location in test mode"""
    bot = TelegramBot(token="test_token", test_mode=True)
    result = await bot.send_location(
        chat_id="123",
        latitude=40.7128,
        longitude=-74.0060,
    )

    assert result["ok"] is True
    assert "result" in result


@pytest.mark.asyncio
async def test_send_location_with_options():
    """Test sending location with optional parameters"""
    bot = TelegramBot(token="test_token", test_mode=True)
    result = await bot.send_location(
        chat_id="123",
        latitude=40.7128,
        longitude=-74.0060,
        horizontal_accuracy=50.0,
        live_period=3600,
        heading=90,
        proximity_alert_radius=100,
    )

    assert result["ok"] is True


@pytest.mark.asyncio
async def test_send_location_with_reply_markup():
    """Test sending location with reply markup"""
    bot = TelegramBot(token="test_token", test_mode=True)
    reply_markup = {"inline_keyboard": [[{"text": "Navigate", "url": "https://maps.google.com"}]]}
    result = await bot.send_location(
        chat_id="123",
        latitude=40.7128,
        longitude=-74.0060,
        reply_markup=reply_markup,
    )

    assert result["ok"] is True


@pytest.mark.asyncio
async def test_all_media_types_support_reply_markup():
    """Test that all new media types support reply_markup parameter"""
    bot = TelegramBot(token="test_token", test_mode=True)
    reply_markup = {"inline_keyboard": [[{"text": "Button", "url": "https://example.com"}]]}

    # Test document with reply_markup
    result = await bot.send_document(
        chat_id="123",
        document_url="https://example.com/doc.pdf",
        reply_markup=reply_markup,
    )
    assert result["ok"] is True

    # Test video with reply_markup
    result = await bot.send_video(
        chat_id="123",
        video_url="https://example.com/video.mp4",
        reply_markup=reply_markup,
    )
    assert result["ok"] is True

    # Test audio with reply_markup
    result = await bot.send_audio(
        chat_id="123",
        audio_url="https://example.com/audio.mp3",
        reply_markup=reply_markup,
    )
    assert result["ok"] is True

    # Test voice with reply_markup
    result = await bot.send_voice(
        chat_id="123",
        voice_url="https://example.com/voice.ogg",
        reply_markup=reply_markup,
    )
    assert result["ok"] is True

    # Test location with reply_markup
    result = await bot.send_location(
        chat_id="123",
        latitude=40.7128,
        longitude=-74.0060,
        reply_markup=reply_markup,
    )
    assert result["ok"] is True
