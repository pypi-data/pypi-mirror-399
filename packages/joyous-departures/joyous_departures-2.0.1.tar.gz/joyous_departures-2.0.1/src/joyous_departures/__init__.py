"""
Joyous Departures - Generate warm, heartfelt sign-off messages

This is a pure Python implementation with no native dependencies.
Works in all Python environments >= 3.10.

Example:
    >>> import asyncio
    >>> from joyous_departures import generate_goodbye
    >>>
    >>> async def main():
    ...     message = await generate_goodbye(template_args={"name": "Alice"})
    ...     print(message)
    >>>
    >>> asyncio.run(main())
"""

import random
import re
from datetime import datetime
from typing import Callable, Awaitable
from zoneinfo import ZoneInfo

from .corpus import CORPUS, CORPUS_SIZE

__version__ = "0.0.0"
__all__ = ["generate_goodbye", "generate_goodbye_sync", "CORPUS", "CORPUS_SIZE"]

# Default values for template variables
_DEFAULTS = {
    "name": "Good Soul",
    "location": "The World",
}

# Validation limits
_LIMITS = {
    "name": 50,
    "location": 100,
    "date": 20,
    "time": 10,
}

# Emoji regex pattern for stripping
_EMOJI_PATTERN = re.compile(
    "["
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F680-\U0001F6FF"  # transport & map symbols
    "\U0001F1E0-\U0001F1FF"  # flags
    "\U00002600-\U000026FF"  # misc symbols
    "\U00002700-\U000027BF"  # dingbats
    "\U0001F900-\U0001F9FF"  # supplemental symbols
    "\U0001FA00-\U0001FA6F"  # chess symbols
    "\U0001FA70-\U0001FAFF"  # symbols and pictographs extended-A
    "\U0000FE00-\U0000FE0F"  # variation selectors
    "\U0000200D"  # zero width joiner
    "\U00002764"  # heart
    "\U00002728"  # sparkles
    "]+",
    flags=re.UNICODE,
)


def _truncate(value: str | None, max_length: int) -> str | None:
    """Truncate string to max length."""
    if value is None:
        return None
    return value[:max_length] if len(value) > max_length else value


def _get_current_date(timezone: str, now: datetime | None = None) -> str:
    """Get current date in YYYY-MM-DD format for the specified timezone.
    
    Reuses a single datetime object for efficiency.
    """
    try:
        tz = ZoneInfo(timezone)
        if now is None:
            now = datetime.now(tz)
        else:
            # Convert naive datetime to timezone-aware if needed
            if now.tzinfo is None:
                now = datetime.now(tz)
            else:
                now = now.astimezone(tz)
        return now.strftime("%Y-%m-%d")
    except Exception:
        # Fallback if timezone is invalid
        dt = now if now is not None else datetime.now()
        return dt.strftime("%Y-%m-%d")


def _get_current_time(timezone: str, now: datetime | None = None) -> str:
    """Get current time in HH:MM format for the specified timezone.
    
    Reuses a single datetime object for efficiency.
    """
    try:
        tz = ZoneInfo(timezone)
        if now is None:
            now = datetime.now(tz)
        else:
            # Convert naive datetime to timezone-aware if needed
            if now.tzinfo is None:
                now = datetime.now(tz)
            else:
                now = now.astimezone(tz)
        return now.strftime("%H:%M")
    except Exception:
        # Fallback if timezone is invalid
        dt = now if now is not None else datetime.now()
        return dt.strftime("%H:%M")


def _substitute_templates(
    message: str,
    template_args: dict[str, str] | None,
    timezone: str,
) -> str:
    """Substitute template variables in a message.
    
    Optimized with lazy date/time evaluation and single datetime object reuse.
    """
    args = template_args or {}

    # Check if date/time are needed before computing
    needs_date = "{date}" in message
    needs_time = "{time}" in message

    # Reuse single datetime object if both date and time are needed
    now = datetime.now() if (needs_date or needs_time) else None

    # Get values with defaults and validation (lazy evaluation)
    name = _truncate(args.get("name"), _LIMITS["name"]) or _DEFAULTS["name"]
    location = _truncate(args.get("location"), _LIMITS["location"]) or _DEFAULTS["location"]
    date = _truncate(args.get("date"), _LIMITS["date"]) or (_get_current_date(timezone, now) if needs_date else "")
    time = _truncate(args.get("time"), _LIMITS["time"]) or (_get_current_time(timezone, now) if needs_time else "")

    # Replace all template variables (single pass)
    result = message
    result = result.replace("{name}", name)
    result = result.replace("{location}", location)
    result = result.replace("{date}", date)
    result = result.replace("{time}", time)

    return result


def _strip_emojis(text: str) -> str:
    """Strip emojis from a string."""
    result = _EMOJI_PATTERN.sub("", text)
    # Normalize whitespace
    result = re.sub(r"\s+", " ", result).strip()
    return result


def generate_goodbye_sync(
    *,
    language_code: str | None = None,
    template_args: dict[str, str] | None = None,
    use_emojis: bool = True,
    strip_emojis: bool = False,
    timezone: str = "Europe/London",
) -> str:
    """
    Generate a warm, heartfelt goodbye message (synchronous).

    This is the core function that performs message generation without any async operations.
    Use this when you don't need the translator callback.

    Args:
        language_code: Language code (reserved for future use)
        template_args: Template variable values (name, location, date, time)
        use_emojis: Include emojis in output. Default: True (v1.x compatibility)
        strip_emojis: Remove emoji characters from output. Default: False
        timezone: IANA timezone for date/time formatting. Default: "Europe/London"

    Returns:
        The generated message

    Example:
        >>> from joyous_departures import generate_goodbye_sync
        >>> message = generate_goodbye_sync(template_args={"name": "Alice"})
        >>> print(message)
        "Wishing you a joyous day, Alice ❤️"
    """
    # Random message selection
    message = random.choice(CORPUS)

    # Template substitution
    result = _substitute_templates(message, template_args, timezone)

    # Emoji handling: support both use_emojis (v1.x) and strip_emojis (v2.x)
    # use_emojis=False OR strip_emojis=True → strip emojis
    should_strip_emojis = strip_emojis or not use_emojis
    if should_strip_emojis:
        result = _strip_emojis(result)

    return result


async def generate_goodbye(
    *,
    language_code: str | None = None,
    template_args: dict[str, str] | None = None,
    use_emojis: bool = True,
    strip_emojis: bool = False,
    timezone: str = "Europe/London",
    translator: Callable[[str, str], Awaitable[str]] | None = None,
) -> str:
    """
    Generate a warm, heartfelt goodbye message (async).

    This async wrapper maintains backward compatibility with v1.x API.
    The core generation is synchronous; async is only used for the optional translator.

    Args:
        language_code: Language code for translation. Default: None (uses en-GB)
        template_args: Template variable values (name, location, date, time)
        use_emojis: Include emojis in output. Default: True (v1.x compatibility)
        strip_emojis: Remove emoji characters from output. Default: False
        timezone: IANA timezone for date/time formatting. Default: "Europe/London"
        translator: Optional async translator callback

    Returns:
        The generated message (optionally translated)

    Example:
        >>> import asyncio
        >>> from joyous_departures import generate_goodbye
        >>>
        >>> async def main():
        ...     message = await generate_goodbye(template_args={"name": "Alice"})
        ...     print(message)
        >>>
        >>> asyncio.run(main())
    """
    # Generate message synchronously
    result = generate_goodbye_sync(
        language_code=language_code,
        template_args=template_args,
        use_emojis=use_emojis,
        strip_emojis=strip_emojis,
        timezone=timezone,
    )

    # Apply translator if provided
    if translator and language_code and language_code != "en-GB":
        try:
            result = await translator(language_code, result)
        except Exception:
            # Fallback to original message if translation fails
            pass

    return result

