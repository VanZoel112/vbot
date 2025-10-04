"""
VZ ASSISTANT v0.0.0.69
ShowJSON Plugin - Message to JSON Analyzer

2025© Vzoel Fox's Lutpan
Founder & DEVELOPER : @VZLfxs
"""

from telethon import events
from telethon.tl.types import (
    MessageEntityCustomEmoji, MessageMediaPhoto, MessageMediaDocument,
    DocumentAttributeSticker, DocumentAttributeVideo, DocumentAttributeAudio,
    DocumentAttributeAnimated, MessageMediaWebPage
)
import json
import re
import config
from datetime import datetime

# Global variables (set by main.py)
vz_client = None
vz_emoji = None

class MessageAnalyzer:
    """Message to JSON Converter - VZ ASSISTANT"""

    def __init__(self):
        self.emoji_pattern = re.compile(
            r'[\U0001F600-\U0001F64F'  # emoticons
            r'\U0001F300-\U0001F5FF'   # symbols & pictographs
            r'\U0001F680-\U0001F6FF'   # transport & map
            r'\U0001F1E0-\U0001F1FF'   # flags
            r'\U00002700-\U000027BF'   # dingbats
            r'\U0001F900-\U0001F9FF'   # supplemental symbols
            r'\U00002600-\U000026FF'   # miscellaneous symbols
            r'\U0001F100-\U0001F1FF]+' # enclosed characters
        )

    def detect_emojis(self, text: str) -> list:
        """Detect and analyze emojis in text"""
        emojis = []
        if not text:
            return emojis

        for match in self.emoji_pattern.finditer(text):
            emoji_char = match.group()
            emojis.append({
                "character": emoji_char,
                "position": match.start(),
                "end_position": match.end(),
                "unicode_codepoint": [f"U+{ord(c):04X}" for c in emoji_char],
                "category": "standard_emoji"
            })

        return emojis

    def analyze_custom_emojis(self, message) -> list:
        """Analyze custom/premium emojis from message entities"""
        custom_emojis = []

        if not message.entities:
            return custom_emojis

        for entity in message.entities:
            if isinstance(entity, MessageEntityCustomEmoji):
                custom_emojis.append({
                    "document_id": str(entity.document_id),
                    "offset": entity.offset,
                    "length": entity.length,
                    "type": "custom_emoji",
                    "is_premium": True
                })

        return custom_emojis

    def get_media_type(self, message) -> str:
        """Determine media type from message"""
        if not message.media:
            return "text"

        if isinstance(message.media, MessageMediaPhoto):
            return "photo"
        elif isinstance(message.media, MessageMediaDocument):
            document = message.media.document

            for attr in document.attributes:
                if isinstance(attr, DocumentAttributeSticker):
                    return "sticker"
                elif isinstance(attr, DocumentAttributeVideo):
                    if hasattr(attr, 'round_message') and attr.round_message:
                        return "video_note"
                    return "video"
                elif isinstance(attr, DocumentAttributeAudio):
                    if hasattr(attr, 'voice') and attr.voice:
                        return "voice"
                    return "audio"
                elif isinstance(attr, DocumentAttributeAnimated):
                    return "gif"

            return "document"
        elif isinstance(message.media, MessageMediaWebPage):
            return "webpage"

        return "other"

    def analyze_photo(self, photo) -> dict:
        """Analyze photo media"""
        return {
            "type": "photo",
            "id": str(photo.id),
            "access_hash": str(photo.access_hash),
            "file_reference": photo.file_reference.hex() if photo.file_reference else None,
            "date": photo.date.isoformat() if photo.date else None,
            "sizes": [
                {
                    "type": size.type,
                    "width": getattr(size, 'w', None),
                    "height": getattr(size, 'h', None),
                    "size": getattr(size, 'size', None)
                }
                for size in photo.sizes
            ],
            "dc_id": photo.dc_id
        }

    def analyze_document(self, document) -> dict:
        """Analyze document media"""
        doc_info = {
            "type": "document",
            "id": str(document.id),
            "access_hash": str(document.access_hash),
            "file_reference": document.file_reference.hex() if document.file_reference else None,
            "size": document.size,
            "mime_type": document.mime_type,
            "attributes": []
        }

        for attr in document.attributes:
            if isinstance(attr, DocumentAttributeSticker):
                doc_info["sticker_info"] = {
                    "alt": attr.alt,
                    "stickerset_id": str(attr.stickerset.id) if attr.stickerset else None,
                    "mask": attr.mask
                }
            elif isinstance(attr, DocumentAttributeVideo):
                doc_info["video_info"] = {
                    "duration": attr.duration,
                    "width": attr.w,
                    "height": attr.h,
                    "round_message": getattr(attr, 'round_message', False)
                }
            elif isinstance(attr, DocumentAttributeAudio):
                doc_info["audio_info"] = {
                    "duration": attr.duration,
                    "title": attr.title,
                    "performer": attr.performer,
                    "voice": getattr(attr, 'voice', False)
                }

        return doc_info

    async def analyze_message(self, message) -> dict:
        """Comprehensive message analysis to JSON"""

        # Basic message info
        message_data = {
            "message_id": message.id,
            "date": message.date.isoformat() if message.date else None,
            "chat_id": message.chat_id,
            "from_user": {
                "id": message.sender_id,
                "is_self": message.out,
                "username": None,
                "first_name": None,
                "last_name": None
            } if message.sender_id else None,
            "text": message.text or "",
            "text_length": len(message.text) if message.text else 0,
            "reply_to": message.reply_to_msg_id if message.reply_to_msg_id else None,
            "edit_date": message.edit_date.isoformat() if message.edit_date else None,
            "pinned": message.pinned,
            "views": message.views
        }

        # Get sender info if available
        if message.sender:
            sender = message.sender
            message_data["from_user"].update({
                "username": sender.username,
                "first_name": sender.first_name,
                "last_name": sender.last_name,
                "is_bot": getattr(sender, 'bot', False),
                "is_verified": getattr(sender, 'verified', False),
                "is_premium": getattr(sender, 'premium', False)
            })

        # Analyze emojis
        message_data["emojis"] = {
            "standard_emojis": self.detect_emojis(message.text),
            "custom_emojis": self.analyze_custom_emojis(message)
        }

        # Analyze media
        message_data["media"] = None
        media_type = self.get_media_type(message)
        message_data["media_type"] = media_type

        if message.media:
            if isinstance(message.media, MessageMediaPhoto):
                message_data["media"] = self.analyze_photo(message.media.photo)
            elif isinstance(message.media, MessageMediaDocument):
                message_data["media"] = self.analyze_document(message.media.document)
            elif isinstance(message.media, MessageMediaWebPage):
                message_data["media"] = {
                    "type": "webpage",
                    "url": getattr(message.media.webpage, 'url', None),
                    "title": getattr(message.media.webpage, 'title', None),
                    "description": getattr(message.media.webpage, 'description', None)
                }

        # Message entities analysis
        message_data["entities"] = []
        if message.entities:
            for entity in message.entities:
                entity_data = {
                    "type": type(entity).__name__,
                    "offset": entity.offset,
                    "length": entity.length
                }

                if hasattr(entity, 'url'):
                    entity_data["url"] = entity.url
                if hasattr(entity, 'user_id'):
                    entity_data["user_id"] = entity.user_id
                if hasattr(entity, 'document_id'):
                    entity_data["document_id"] = str(entity.document_id)

                message_data["entities"].append(entity_data)

        # Analytics summary
        message_data["analytics"] = {
            "has_text": bool(message.text),
            "has_media": bool(message.media),
            "has_emojis": bool(message_data["emojis"]["standard_emojis"] or message_data["emojis"]["custom_emojis"]),
            "total_emojis": len(message_data["emojis"]["standard_emojis"]) + len(message_data["emojis"]["custom_emojis"]),
            "has_entities": bool(message.entities),
            "total_entities": len(message.entities) if message.entities else 0,
            "is_forwarded": bool(message.forward),
            "is_reply": bool(message.reply_to_msg_id),
            "is_edited": bool(message.edit_date)
        }

        return message_data

# Initialize analyzer
analyzer = MessageAnalyzer()

# ============================================================================
# SHOWJSON COMMAND (.sj alias)
# ============================================================================

@events.register(events.NewMessage(pattern=r'^\.sj$', outgoing=True))
async def sj_handler(event):
    """
    .sj - Show JSON (message analyzer)

    Usage:
        .sj (reply to message)  - Analyze replied message
        .sj                     - Analyze current message

    Converts message to detailed JSON with emoji/media/entity analysis
    """
    global vz_client, vz_emoji

    loading_emoji = vz_emoji.getemoji('loading')
    proses_emoji = vz_emoji.getemoji('robot')

    processing_msg = await vz_client.edit_with_premium_emoji(event,
        f"{loading_emoji} Analyzing Message...\n\n"
        f"{proses_emoji} Processing message data to JSON..."
    )

    try:
        target_message = None

        if event.reply_to_msg_id:
            target_message = await event.get_reply_message()
        else:
            target_message = event

        if not target_message:
            error_emoji = vz_emoji.getemoji('merah')
            kuning_emoji = vz_emoji.getemoji('kuning')
            telegram_emoji = vz_emoji.getemoji('telegram')

            await vz_client.edit_with_premium_emoji(processing_msg,
                f"{error_emoji} No Message to Analyze!\n\n"
                f"{kuning_emoji} Reply to a message to analyze it\n\n"
                f"{telegram_emoji} VZ ASSISTANT JSON Analyzer"
            )
            return

        # Analyze message
        json_data = await analyzer.analyze_message(target_message)
        json_str = json.dumps(json_data, indent=2, ensure_ascii=False)

        # Get emojis
        utama_emoji = vz_emoji.getemoji('utama')
        aktif_emoji = vz_emoji.getemoji('aktif')
        proses_emoji = vz_emoji.getemoji('robot')
        loading_emoji = vz_emoji.getemoji('loading')
        centang_emoji = vz_emoji.getemoji('centang')
        kuning_emoji = vz_emoji.getemoji('kuning')
        telegram_emoji = vz_emoji.getemoji('telegram')
        gear_emoji = vz_emoji.getemoji('gear')
        petir_emoji = vz_emoji.getemoji('petir')
        main_emoji = vz_emoji.getemoji('utama')

        # Check if JSON is too long
        if len(json_str) > 3500:
            # Split into chunks
            chunks = []
            chunk_size = 3500
            for i in range(0, len(json_str), chunk_size):
                chunks.append(json_str[i:i + chunk_size])

            # Send first chunk with header
            header_text = f"{utama_emoji} **MESSAGE JSON ANALYSIS**\n\n"
            header_text += f"{aktif_emoji} Message ID: `{json_data['message_id']}`\n"
            header_text += f"{proses_emoji} Total Size: `{len(json_str)} chars`\n"
            header_text += f"{loading_emoji} Parts: `{len(chunks)} chunks`\n\n"
            header_text += f"{centang_emoji} Part 1/{len(chunks)}:\n\n"
            header_text += f"```json\n{chunks[0]}\n```\n\n"
            header_text += f"{gear_emoji} Plugins Digunakan: **SHOWJSON**\n"
            header_text += f"{petir_emoji} by {main_emoji} Vzoel Fox's Lutpan"

            await vz_client.edit_with_premium_emoji(processing_msg, header_text)

            # Send remaining chunks
            for i, chunk in enumerate(chunks[1:], 2):
                chunk_text = f"{kuning_emoji} Part {i}/{len(chunks)}:\n\n"
                chunk_text += f"```json\n{chunk}\n```"
                await event.reply(chunk_text)

        else:
            # Single message output
            analytics = json_data['analytics']

            result_text = f"{utama_emoji} **MESSAGE JSON ANALYSIS**\n\n"
            result_text += f"{aktif_emoji} Message ID: `{json_data['message_id']}`\n"
            result_text += f"{proses_emoji} Chat ID: `{json_data['chat_id']}`\n"
            result_text += f"{loading_emoji} Date: `{json_data['date'][:19] if json_data['date'] else 'N/A'}`\n\n"

            result_text += f"{centang_emoji} **Analytics:**\n"
            result_text += f"  • Text: `{'Yes' if analytics['has_text'] else 'No'}` (`{json_data['text_length']}` chars)\n"
            result_text += f"  • Media: `{'Yes' if analytics['has_media'] else 'No'}` (`{json_data['media_type']}`)\n"
            result_text += f"  • Emojis: `{analytics['total_emojis']}` total\n"
            result_text += f"  • Entities: `{analytics['total_entities']}` total\n\n"

            result_text += f"{kuning_emoji} **Full JSON Data:**\n\n"
            result_text += f"```json\n{json_str}\n```\n\n"
            result_text += f"{gear_emoji} Plugins Digunakan: **SHOWJSON**\n"
            result_text += f"{petir_emoji} by {main_emoji} Vzoel Fox's Lutpan"

            await vz_client.edit_with_premium_emoji(processing_msg, result_text)

    except Exception as e:
        error_emoji = vz_emoji.getemoji('merah')
        kuning_emoji = vz_emoji.getemoji('kuning')
        telegram_emoji = vz_emoji.getemoji('telegram')

        await vz_client.edit_with_premium_emoji(processing_msg,
            f"{error_emoji} **Analysis Failed!**\n\n"
            f"{error_emoji} Error: `{str(e)[:100]}`\n\n"
            f"{kuning_emoji} **Possible Issues:**\n"
            f"  • Message too complex to analyze\n"
            f"  • Media access restrictions\n"
            f"  • Network connectivity issues\n\n"
            f"{telegram_emoji} VZ ASSISTANT JSON Analyzer"
        )

@events.register(events.NewMessage(pattern=r'^\.showjson$', outgoing=True))
async def showjson_handler(event):
    """
    .showjson - Show JSON (alias for .sj)

    Alias command for message to JSON analyzer
    """
    await sj_handler(event)

print("✅ Plugin loaded: showjson.py")
