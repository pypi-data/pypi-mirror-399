"""
Unit tests for telegram_rag_bot.main.track_usage callback.

Tests cover:
- track_usage logs structured data correctly
- track_usage fail-silent behavior (doesn't crash on errors)
"""

import pytest
from unittest.mock import patch
from typing import TypedDict


# Type stub for UsageData (matches orchestrator v0.7.6)
class UsageData(TypedDict):
    """Usage data from Router (tokens, cost, latency, success status)."""

    provider_name: str
    model: str
    total_tokens: int
    prompt_tokens: int
    completion_tokens: int
    cost: float
    latency_ms: int
    success: bool


@pytest.mark.asyncio
async def test_track_usage_logs_correctly():
    """Test that track_usage logs structured data."""
    from telegram_rag_bot.main import track_usage

    data: UsageData = {
        "provider_name": "gigachat",
        "model": "GigaChat-Pro",
        "total_tokens": 150,
        "prompt_tokens": 100,
        "completion_tokens": 50,
        "cost": 0.45,
        "latency_ms": 1200,
        "success": True,
    }

    with patch("telegram_rag_bot.main.logger.info") as mock_logger:
        await track_usage(data)

        # Verify logger called with correct message
        mock_logger.assert_called_once()
        call_args = mock_logger.call_args
        assert call_args[0][0] == "llm_usage_tracked"

        # Verify structured data
        usage = call_args[1]["extra"]["usage"]
        assert usage["provider"] == "gigachat"
        assert usage["total_tokens"] == 150
        assert usage["cost_rub"] == 0.45
        assert usage["success"] is True


@pytest.mark.asyncio
async def test_track_usage_fail_silent():
    """Test that track_usage doesn't crash on errors."""
    from telegram_rag_bot.main import track_usage

    data: UsageData = {
        "provider_name": "gigachat",
        "model": "GigaChat-Pro",
        "total_tokens": 150,
        "prompt_tokens": 100,
        "completion_tokens": 50,
        "cost": 0.45,
        "latency_ms": 1200,
        "success": True,
    }

    with (
        patch("telegram_rag_bot.main.logger.info", side_effect=Exception("Test error")),
        patch("telegram_rag_bot.main.logger.warning") as mock_warning,
    ):
        # Should NOT raise exception
        await track_usage(data)

        # Verify warning was logged
        mock_warning.assert_called_once()
        assert "Usage tracking callback failed" in mock_warning.call_args[0][0]
