"""Utility helpers for premium emoji conversion."""

from typing import Dict, List, Optional

from telethon.tl.types import MessageEntityCustomEmoji

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


def has_premium_mapping() -> bool:
    """Return ``True`` if premium emoji mapping data is available."""
    emoji_data = config.load_emoji_mapping()
    return bool(emoji_data.get("emoji_mapping"))
