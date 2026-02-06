"""Tests for UserPreference model."""

from datetime import datetime, timezone

from expenses_ai_agent.storage.models import Currency, UserPreference


def test_user_preference_defaults() -> None:
    """Test UserPreference default values."""
    pref = UserPreference(telegram_user_id=12345)
    assert pref.preferred_currency == Currency.EUR
    assert pref.telegram_user_id == 12345


def test_user_preference_custom_currency() -> None:
    """Test UserPreference with custom currency."""
    pref = UserPreference(telegram_user_id=12345, preferred_currency=Currency.USD)
    assert pref.preferred_currency == Currency.USD


def test_user_preference_str() -> None:
    """Test UserPreference string representation."""
    pref = UserPreference(telegram_user_id=12345, preferred_currency=Currency.GBP)
    assert "12345" in str(pref)
    assert "GBP" in str(pref)


def test_user_preference_timestamps() -> None:
    """Test UserPreference timestamps are set."""
    pref = UserPreference(telegram_user_id=12345)
    assert pref.created_at is not None
    assert pref.updated_at is not None
    # Timestamps should be recent (within last minute)
    now = datetime.now(timezone.utc)
    assert (now - pref.created_at).total_seconds() < 60
    assert (now - pref.updated_at).total_seconds() < 60
