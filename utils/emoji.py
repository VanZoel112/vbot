"""Utility helpers for premium emoji conversion."""

from typing import Dict, List, Optional, Tuple
import re

from telethon.tl.types import (
    MessageEntityCustomEmoji,
    MessageEntityBold,
    MessageEntityItalic,
    MessageEntityCode,
    MessageEntityPre,
)

import config


def _sorted_emoji_keys(emoji_mapping: Dict[str, str]) -> List[str]:
    """Return emoji keys sorted by UTF-16 length (descending)."""
    return sorted(
        emoji_mapping.keys(),
        key=lambda emoji: len(emoji.encode("utf-16-le")),
        reverse=True,
    )


def build_premium_emoji_entities(
    text: str,
    emoji_data: Optional[Dict] = None,
) -> List[MessageEntityCustomEmoji]:
    """Generate custom emoji entities for premium emojis found in ``text``.

    Args:
        text: The message text to scan for premium emoji replacements.
        emoji_data: Optional pre-loaded emoji mapping dictionary from
            :func:`config.load_emoji_mapping`.

    Returns:
        A list of :class:`~telethon.tl.types.MessageEntityCustomEmoji` objects
        covering each premium emoji found in the text. If the mapping is not
        available or no emojis are found, an empty list is returned.
    """
    if emoji_data is None:
        emoji_data = config.load_emoji_mapping()

    emoji_mapping = emoji_data.get("emoji_mapping", {})
    if not emoji_mapping or not text:
        return []

    sorted_emojis = _sorted_emoji_keys(emoji_mapping)
    emoji_lengths = {
        emoji: len(emoji.encode("utf-16-le")) // 2 for emoji in sorted_emojis
    }

    entities: List[MessageEntityCustomEmoji] = []
    offset = 0
    index = 0
    text_length = len(text)

    while index < text_length:
        matched_emoji = None

        for emoji in sorted_emojis:
            if text.startswith(emoji, index):
                matched_emoji = emoji
                break

        if matched_emoji:
            length = emoji_lengths[matched_emoji]
            entities.append(
                MessageEntityCustomEmoji(
                    offset=offset,
                    length=length,
                    document_id=int(emoji_mapping[matched_emoji]),
                )
            )
            index += len(matched_emoji)
            offset += length
        else:
            char = text[index]
            offset += len(char.encode("utf-16-le")) // 2
            index += 1

    return entities


def parse_markdown_entities(text: str) -> Tuple[str, List]:
    """
    Parse markdown syntax and convert to Telegram entities.

    Supports:
    - **bold** -> MessageEntityBold
    - __italic__ -> MessageEntityItalic
    - `code` -> MessageEntityCode
    - ```language\ncode``` -> MessageEntityPre

    Returns:
        Tuple of (cleaned_text, entities)
    """
    entities = []
    cleaned_text = text
    offset_adjustment = 0

    # Pattern: **bold**
    bold_pattern = r'\*\*(.+?)\*\*'
    for match in re.finditer(bold_pattern, text):
        start = match.start() - offset_adjustment
        content = match.group(1)
        length = len(content.encode('utf-16-le')) // 2

        entities.append(MessageEntityBold(
            offset=start,
            length=length
        ))

        # Remove markdown syntax from text
        cleaned_text = cleaned_text.replace(match.group(0), content, 1)
        offset_adjustment += 4  # **..** = 4 chars removed

    # Recalculate for italic (on cleaned text)
    offset_adjustment = 0
    temp_text = cleaned_text

    # Pattern: __italic__
    italic_pattern = r'__(.+?)__'
    for match in re.finditer(italic_pattern, temp_text):
        start = match.start() - offset_adjustment
        content = match.group(1)
        length = len(content.encode('utf-16-le')) // 2

        entities.append(MessageEntityItalic(
            offset=start,
            length=length
        ))

        # Remove markdown syntax from text
        cleaned_text = cleaned_text.replace(match.group(0), content, 1)
        offset_adjustment += 4  # __..__ = 4 chars removed

    # Recalculate for code
    offset_adjustment = 0
    temp_text = cleaned_text

    # Pattern: `code`
    code_pattern = r'`([^`]+)`'
    for match in re.finditer(code_pattern, temp_text):
        start = match.start() - offset_adjustment
        content = match.group(1)
        length = len(content.encode('utf-16-le')) // 2

        entities.append(MessageEntityCode(
            offset=start,
            length=length
        ))

        # Remove markdown syntax from text
        cleaned_text = cleaned_text.replace(match.group(0), content, 1)
        offset_adjustment += 2  # `..` = 2 chars removed

    return cleaned_text, entities


def build_combined_entities(text: str, emoji_data: Optional[Dict] = None) -> Tuple[str, List]:
    """
    Build combined entities: markdown formatting + premium emojis.

    Args:
        text: Message text with markdown syntax
        emoji_data: Optional emoji mapping

    Returns:
        Tuple of (cleaned_text, combined_entities)
    """
    # Parse markdown first
    cleaned_text, markdown_entities = parse_markdown_entities(text)

    # Build emoji entities on cleaned text
    emoji_entities = build_premium_emoji_entities(cleaned_text, emoji_data)

    # Combine and sort by offset
    all_entities = markdown_entities + emoji_entities
    all_entities.sort(key=lambda e: e.offset)

    return cleaned_text, all_entities


def has_premium_mapping() -> bool:
    """Return ``True`` if premium emoji mapping data is available."""
    emoji_data = config.load_emoji_mapping()
    return bool(emoji_data.get("emoji_mapping"))
