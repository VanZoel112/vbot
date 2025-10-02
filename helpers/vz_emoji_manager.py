"""Premium emoji manager compatible with VZ_EMOJI.md documentation.

This module mirrors the behaviour expected by the VZ emoji usage guides
from the `vzl2` reference implementation while sourcing its data from the
local ``emojiprime.json`` file.  The goal is to offer a single entrypoint
(`VZEmojiManager`) that can be used by plugins to fetch emoji characters,
resolve premium IDs, assemble entity payloads, and expose helper routines
for command/status presets.

The helper intentionally keeps the public API close to the original
``vzoel_emoji`` object so that documentation and examples remain valid.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence

from telethon.tl.types import MessageEntityCustomEmoji

import config
from utils.emoji import build_premium_emoji_entities

# ---------------------------------------------------------------------------
# Alias registry (emoji mapping only) — disesuaikan sesuai instruksi
# ---------------------------------------------------------------------------

_DEFAULT_ALIAS_OVERRIDES: Mapping[str, Sequence[str]] = {
    "MAIN_VZOEL": ("utama", "signature_main"),
    "DEVELOPER": ("developer", "owner_dev"),
    "OWNER": ("owner", "founder"),
    "GEAR": ("loading", "gear"),
    "CHECKLIST": ("centang", "success"),
    "PETIR": ("petir", "storm"),
    "HIJAU": ("hijau", "latency_good"),
    "KUNING": ("kuning", "latency_warn"),
    "MERAH": ("merah", "latency_bad"),
    "TELEGRAM": ("telegram", "inbox"),
    "CAMERA": ("camera", "photo"),
    "PROSES_1": ("proses1", "anim_stage_1"),
    "PROSES_2": ("proses2", "anim_stage_2"),
    "PROSES_3": ("proses3", "anim_stage_3"),
    "ROBOT": ("robot", "space"),
    "LOADING": ("infinite", "loading_loop"),
    "NYALA": ("nyala", "active"),
}

_DEFAULT_SIGNATURE_SEQUENCE: Sequence[str] = (
    "MAIN_VZOEL",
    "PETIR",
    "PROSES_1",
)

_DEFAULT_COMMAND_PRESETS: Mapping[str, Sequence[str]] = {
    "alive": ("MAIN_VZOEL", "NYALA", "CHECKLIST"),
    "ping": ("GEAR", "HIJAU", "KUNING", "MERAH"),
    "vz": ("MAIN_VZOEL", "PETIR", "PROSES_1"),
}

_FALLBACK_EMOJI = "🔸"


@dataclass(frozen=True)
class EmojiInfo:
    """Resolved emoji information used by :class:`VZEmojiManager`."""

    canonical: str
    alias: str
    emoji: str
    custom_id: Optional[str]


class VZEmojiManager:
    """Manage premium emoji lookups and entity helpers.

    Parameters
    ----------
    emoji_data:
        Pre-loaded mapping dictionary. When omitted the manager will read
        from :func:`config.load_emoji_mapping` on instantiation.
    alias_overrides:
        Additional alias definitions to merge with the canonical JSON
        aliases. Keys must match the uppercase entries from
        ``emojiprime.json``'s ``emoji_names`` section, while the values are
        snake_case aliases exposed to plugins/documentation.
    """

    def __init__(
        self,
        emoji_data: Optional[Dict[str, Any]] = None,
        *,
        alias_overrides: Optional[Mapping[str, Sequence[str]]] = None,
    ) -> None:
        self._raw_data: Dict[str, Any] = emoji_data or config.load_emoji_mapping()
        self._alias_overrides = dict(_DEFAULT_ALIAS_OVERRIDES)
        if alias_overrides:
            for key, values in alias_overrides.items():
                self._alias_overrides[key] = tuple(values)

        self._emoji_mapping: Dict[str, str] = {}
        self._emoji_names: Dict[str, str] = {}
        self._categories: Dict[str, Any] = {}
        self._usage_mapping: Dict[str, Any] = {}
        self._alias_to_canonical: Dict[str, str] = {}
        self._preferred_alias: Dict[str, str] = {}
        self._char_to_canonical: Dict[str, str] = {}
        self._signature_sequence: Sequence[str] = _DEFAULT_SIGNATURE_SEQUENCE
        self._command_presets: Dict[str, Sequence[str]] = dict(
            _DEFAULT_COMMAND_PRESETS
        )
        self._status_aliases: Dict[str, List[str]] = {}
        self._process_sequence: List[str] = []

        self._hydrate()

    # ------------------------------------------------------------------
    # Internal preparation
    # ------------------------------------------------------------------

    def _hydrate(self) -> None:
        data = self._raw_data or {}
        self._emoji_mapping = dict(data.get("emoji_mapping", {}))
        self._emoji_names = dict(data.get("emoji_names", {}))
        self._categories = dict(data.get("categories", {}))
        self._usage_mapping = dict(data.get("usage_mapping", {}))

        self._alias_to_canonical.clear()
        self._preferred_alias.clear()
        self._char_to_canonical = {
            emoji: canonical for canonical, emoji in self._emoji_names.items()
        }

        for canonical, emoji in self._emoji_names.items():
            self._register_alias(canonical, canonical)
            self._register_alias(canonical.lower(), canonical)
            self._preferred_alias.setdefault(canonical, canonical.lower())
            self._register_alias(emoji, canonical)

            overrides = self._alias_overrides.get(canonical, ())
            if overrides:
                for alias in overrides:
                    self._register_alias(alias, canonical)
                self._preferred_alias[canonical] = overrides[0]

        self._prepare_signature_sequence()
        self._prepare_status_aliases()
        self._prepare_process_sequence()

    def _prepare_signature_sequence(self) -> None:
        sequence: List[str] = []
        for canonical in _DEFAULT_SIGNATURE_SEQUENCE:
            if canonical in self._emoji_names:
                sequence.append(canonical)
        self._signature_sequence = tuple(sequence)

    def _prepare_status_aliases(self) -> None:
        status_map = self._usage_mapping.get("system_status", {})
        self._status_aliases = {}
        for status_key, emoji_char in status_map.items():
            canonical = self._char_to_canonical.get(emoji_char)
            if not canonical:
                continue
            alias = self._preferred_alias.get(canonical)
            if not alias:
                continue
            self._status_aliases[status_key] = [alias]

    def _prepare_process_sequence(self) -> None:
        process_map = self._usage_mapping.get("process_animation", {})
        sequence: List[str] = []
        for stage_key in ("stage_1", "stage_2", "stage_3"):
            emoji_char = process_map.get(stage_key)
            if not emoji_char:
                continue
            canonical = self._char_to_canonical.get(emoji_char)
            if not canonical:
                continue
            alias = self._preferred_alias.get(canonical)
            if alias:
                sequence.append(alias)
        loading_char = process_map.get("loading")
        if loading_char:
            canonical = self._char_to_canonical.get(loading_char)
            if canonical:
                alias = self._preferred_alias.get(canonical)
                if alias:
                    sequence.append(alias)
        self._process_sequence = sequence

    def _register_alias(self, alias: str, canonical: str) -> None:
        if not alias:
            return
        self._alias_to_canonical[alias] = canonical
        self._alias_to_canonical[alias.lower()] = canonical

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def available(self) -> bool:
        """Return ``True`` when premium emoji data is available."""

        return bool(self._emoji_mapping)

    def refresh(self) -> None:
        """Reload emoji data from disk."""

        self._raw_data = config.load_emoji_mapping()
        self._hydrate()

    # ------------------------------------------------------------------
    # Lookup helpers
    # ------------------------------------------------------------------

    def _resolve_canonical(self, name: Optional[str]) -> Optional[str]:
        if not name:
            return None
        canonical = self._alias_to_canonical.get(name)
        if canonical:
            return canonical
        return self._alias_to_canonical.get(name.lower())

    def get_emoji(self, name: str) -> Optional[str]:
        """Return the raw emoji character for ``name`` if available."""

        canonical = self._resolve_canonical(name)
        if not canonical:
            return None
        return self._emoji_names.get(canonical)

    def getemoji(self, name: str) -> str:
        """Convenience wrapper with fallback emoji."""

        emoji = self.get_emoji(name)
        return emoji if emoji else _FALLBACK_EMOJI

    def get_custom_emoji_id(self, name: str) -> Optional[str]:
        """Return the Telegram custom emoji ID for ``name``."""

        emoji = self.get_emoji(name)
        if not emoji:
            return None
        return self._emoji_mapping.get(emoji)

    def get_markdown(self, name: str) -> Optional[str]:
        """Return emoji formatted as Telegram Markdown premium reference."""

        emoji = self.get_emoji(name)
        custom_id = self.get_custom_emoji_id(name)
        if not emoji or not custom_id:
            return None
        return f"[{emoji}](emoji/{custom_id})"

    def get_html(self, name: str) -> Optional[str]:
        """Return emoji formatted as Telegram HTML premium reference."""

        emoji = self.get_emoji(name)
        custom_id = self.get_custom_emoji_id(name)
        if not emoji or not custom_id:
            return None
        return f'<tg-emoji emoji-id="{custom_id}">{emoji}</tg-emoji>'

    def format_emoji_response(
        self, emoji_names: Iterable[str], text: str = ""
    ) -> str:
        """Join multiple emojis followed by ``text``."""

        emojis = [self.getemoji(name) for name in emoji_names]
        if text:
            return f"{''.join(emojis)} {text}" if emojis else text
        return "".join(emojis)

    def format_template(self, template: str, mapping: Mapping[str, str]) -> str:
        """Replace placeholders in ``template`` using ``mapping`` keys.

        ``mapping`` maps placeholders such as ``"{utama}"`` to emoji aliases
        understood by the manager. Unknown aliases fall back to the raw
        placeholder so templates remain readable during development.
        """

        result = template
        for placeholder, alias in mapping.items():
            emoji = self.getemoji(alias)
            result = result.replace(placeholder, emoji)
        return result

    def get_command_emojis(self, command: str) -> List[str]:
        """Return preferred alias list for a command preset."""

        preset = self._command_presets.get(command.lower())
        if not preset:
            return []
        return [
            self._preferred_alias.get(canonical, canonical.lower())
            for canonical in preset
            if canonical in self._emoji_names
        ]

    def get_status_emojis(self, status: str) -> List[str]:
        """Return aliases associated with a status keyword."""

        return list(self._status_aliases.get(status, []))

    def get_latency_indicator(self, latency_ms: float) -> EmojiInfo:
        """Return the emoji info representing ``latency_ms``."""

        mapping = self._usage_mapping.get("ping_latency", {})
        thresholds = (
            (150.0, "1-150ms"),
            (200.0, "151-200ms"),
            (float("inf"), "200+ms"),
        )
        for limit, key in thresholds:
            if latency_ms <= limit:
                emoji_char = mapping.get(key)
                if emoji_char:
                    canonical = self._char_to_canonical.get(emoji_char)
                    if canonical:
                        alias = self._preferred_alias.get(
                            canonical, canonical.lower()
                        )
                        return EmojiInfo(
                            canonical=canonical,
                            alias=alias,
                            emoji=emoji_char,
                            custom_id=self._emoji_mapping.get(emoji_char),
                        )
                break
        # Fallback when mapping missing or latency is negative.
        fallback_alias = self._preferred_alias.get("HIJAU", "hijau")
        fallback_emoji = self.getemoji(fallback_alias)
        return EmojiInfo(
            canonical="HIJAU",
            alias=fallback_alias,
            emoji=fallback_emoji,
            custom_id=self.get_custom_emoji_id(fallback_alias),
        )

    def get_process_sequence(self) -> List[str]:
        """Return aliases representing the process animation order."""

        return list(self._process_sequence)

    def get_category_emojis(self, category: str) -> List[str]:
        """Return preferred aliases for a given category name."""

        category_data = self._categories.get(category, {})
        emojis = []
        for emoji_char in category_data.get("emojis", []):
            canonical = self._char_to_canonical.get(emoji_char)
            if not canonical:
                continue
            alias = self._preferred_alias.get(canonical)
            if alias:
                emojis.append(alias)
        return emojis

    def get_all_aliases(self) -> List[str]:
        """Return a sorted list of unique snake_case aliases."""

        aliases = {alias for alias in self._alias_to_canonical if alias.islower()}
        return sorted(aliases)

    def get_vzoel_signature(self) -> str:
        """Return the concatenated signature emoji string."""

        emojis = [self.getemoji(alias) for alias in self._signature_sequence]
        return "".join(emojis)

    # ------------------------------------------------------------------
    # Premium entity helpers
    # ------------------------------------------------------------------

    def build_entities(self, text: str) -> List[MessageEntityCustomEmoji]:
        """Return premium emoji entities for ``text``."""

        if not text or not self.available:
            return []
        return build_premium_emoji_entities(text, self._raw_data)

    async def safe_send_premium(
        self,
        client: Any,
        entity: Any,
        text: str,
        **kwargs: Any,
    ) -> Any:
        """Send a message ensuring premium emoji entities are preserved."""

        entities = self.build_entities(text)
        send_kwargs = dict(kwargs)
        if entities:
            send_kwargs.setdefault("formatting_entities", entities)
        try:
            return await client.send_message(entity, text, **send_kwargs)
        except Exception:
            if "formatting_entities" in send_kwargs:
                send_kwargs.pop("formatting_entities", None)
            return await client.send_message(entity, text, **send_kwargs)

    async def safe_edit_premium(
        self,
        target: Any,
        text: str,
        **kwargs: Any,
    ) -> Any:
        """Edit a message while attempting to keep premium entities."""

        entities = self.build_entities(text)
        edit_kwargs = dict(kwargs)
        if entities:
            edit_kwargs.setdefault("formatting_entities", entities)
        try:
            return await target.edit(text, **edit_kwargs)
        except Exception:
            if "formatting_entities" in edit_kwargs:
                edit_kwargs.pop("formatting_entities", None)
            return await target.edit(text, **edit_kwargs)

    async def safe_reply_premium(
        self,
        event: Any,
        text: str,
        **kwargs: Any,
    ) -> Any:
        """Reply to an event using premium emoji entities when available."""

        entities = self.build_entities(text)
        reply_kwargs = dict(kwargs)
        if entities:
            reply_kwargs.setdefault("formatting_entities", entities)
        try:
            return await event.reply(text, **reply_kwargs)
        except Exception:
            if "formatting_entities" in reply_kwargs:
                reply_kwargs.pop("formatting_entities", None)
            return await event.reply(text, **reply_kwargs)


# Global instance (renamed): vz_emoji
vz_emoji = VZEmojiManager()

__all__ = ["VZEmojiManager", "vz_emoji", "EmojiInfo"]
