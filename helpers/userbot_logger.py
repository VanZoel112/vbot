"""
VZ ASSISTANT v0.0.0.69
Userbot Logger - Send Activity Logs to Assistant Bot

Flow:
1. Userbot performs activity (send/receive messages, commands)
2. Logger sends log to assistant bot via PM
3. Bot receives → forwards to log group → deletes original
4. No trace left in bot's PM

2025© Vzoel Fox's Lutpan
Founder & DEVELOPER : @VZLfxs
"""

import os
import asyncio
from datetime import datetime
from telethon import TelegramClient
from telethon.tl.types import Message, MessageMediaPhoto, MessageMediaDocument

# Global variables
_bot_username = None
_user_info = None


def init_logger(bot_username: str, user_id: int, username: str, first_name: str):
    """
    Initialize userbot logger.

    Args:
        bot_username: Assistant bot username (without @)
        user_id: Userbot user ID
        username: Userbot username
        first_name: Userbot first name
    """
    global _bot_username, _user_info

    _bot_username = bot_username.lstrip("@") if bot_username else None
    _user_info = {
        "user_id": user_id,
        "username": username or "no_username",
        "first_name": first_name or "User"
    }


async def send_log_to_bot(client: TelegramClient, log_type: str, data: dict):
    """
    Send activity log to assistant bot.

    Args:
        client: Telethon client instance
        log_type: Type of log (command, outgoing, incoming, media_sent, media_received)
        data: Log data dictionary

    Log types:
    - command: {"cmd": ".ping", "chat": "GroupName", "chat_id": -123}
    - outgoing: {"text": "Hello", "chat": "GroupName", "chat_id": -123}
    - incoming: {"text": "Hi", "from": "UserName", "chat": "GroupName"}
    - media_sent: {"media_type": "photo", "chat": "GroupName", "message": Message}
    - media_received: {"media_type": "photo", "from": "UserName", "message": Message}
    """
    global _bot_username, _user_info

    if not _bot_username or not _user_info:
        return  # Logger not initialized

    try:
        # Build log message based on type
        if log_type == "command":
            log_text = f"""
⚡ **Command Executed**

👤 **User:** {_user_info['first_name']} (@{_user_info['username']})
🆔 **ID:** `{_user_info['user_id']}`
💬 **Chat:** {data.get('chat', 'Unknown')} (`{data.get('chat_id', 'N/A')}`)
⚡ **Command:** `{data.get('cmd', 'Unknown')}`
🕐 **Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🤖 #userbot_command
"""
            await client.send_message(_bot_username, log_text)

        elif log_type == "outgoing":
            log_text = f"""
📤 **Message Sent**

👤 **User:** {_user_info['first_name']} (@{_user_info['username']})
💬 **To:** {data.get('chat', 'Unknown')} (`{data.get('chat_id', 'N/A')}`)
📝 **Message:** {data.get('text', '')[:200]}{'...' if len(data.get('text', '')) > 200 else ''}
🕐 **Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🤖 #userbot_outgoing
"""
            await client.send_message(_bot_username, log_text)

        elif log_type == "incoming":
            log_text = f"""
📥 **Message Received**

👤 **User:** {_user_info['first_name']} (@{_user_info['username']})
👥 **From:** {data.get('from', 'Unknown')}
💬 **Chat:** {data.get('chat', 'Unknown')}
📝 **Message:** {data.get('text', '')[:200]}{'...' if len(data.get('text', '')) > 200 else ''}
🕐 **Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🤖 #userbot_incoming
"""
            await client.send_message(_bot_username, log_text)

        elif log_type == "media_sent":
            # Send caption first
            caption = f"""
📤 **Media Sent**

👤 **User:** {_user_info['first_name']} (@{_user_info['username']})
💬 **To:** {data.get('chat', 'Unknown')}
📁 **Type:** {data.get('media_type', 'unknown')}
🕐 **Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🤖 #userbot_media_sent
"""
            # Forward the actual media
            message = data.get('message')
            if message and message.media:
                await client.send_message(_bot_username, caption)
                await client.forward_messages(_bot_username, message)

        elif log_type == "media_received":
            # Send caption first
            caption = f"""
📥 **Media Received**

👤 **User:** {_user_info['first_name']} (@{_user_info['username']})
👥 **From:** {data.get('from', 'Unknown')}
📁 **Type:** {data.get('media_type', 'unknown')}
🕐 **Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🤖 #userbot_media_received
"""
            # Forward the actual media
            message = data.get('message')
            if message and message.media:
                await client.send_message(_bot_username, caption)
                await client.forward_messages(_bot_username, message)

    except Exception as e:
        # Silently fail - don't interrupt userbot operations
        print(f"⚠️  Logger error: {e}")


async def log_command(client: TelegramClient, event):
    """
    Log command execution.

    Args:
        client: Telethon client
        event: Command event
    """
    try:
        chat = await event.get_chat()
        chat_name = getattr(chat, 'title', None) or getattr(chat, 'first_name', 'Private')

        await send_log_to_bot(client, "command", {
            "cmd": event.text,
            "chat": chat_name,
            "chat_id": event.chat_id
        })
    except:
        pass


async def log_outgoing_message(client: TelegramClient, event):
    """
    Log outgoing message.

    Args:
        client: Telethon client
        event: Message event
    """
    try:
        # Skip if it's a command (already logged)
        if event.text and event.text.startswith('.'):
            return

        chat = await event.get_chat()
        chat_name = getattr(chat, 'title', None) or getattr(chat, 'first_name', 'Private')

        # Check if media
        if event.media:
            media_type = "unknown"
            if isinstance(event.media, MessageMediaPhoto):
                media_type = "photo"
            elif isinstance(event.media, MessageMediaDocument):
                media_type = "document/video/audio"

            await send_log_to_bot(client, "media_sent", {
                "media_type": media_type,
                "chat": chat_name,
                "message": event.message
            })
        elif event.text:
            await send_log_to_bot(client, "outgoing", {
                "text": event.text,
                "chat": chat_name,
                "chat_id": event.chat_id
            })
    except:
        pass


async def log_incoming_message(client: TelegramClient, event):
    """
    Log incoming message.

    Args:
        client: Telethon client
        event: Message event
    """
    try:
        sender = await event.get_sender()
        chat = await event.get_chat()

        sender_name = getattr(sender, 'first_name', 'Unknown')
        sender_username = getattr(sender, 'username', None)
        from_text = f"{sender_name} (@{sender_username})" if sender_username else sender_name

        chat_name = getattr(chat, 'title', None) or getattr(chat, 'first_name', 'Private')

        # Check if media
        if event.media:
            media_type = "unknown"
            if isinstance(event.media, MessageMediaPhoto):
                media_type = "photo"
            elif isinstance(event.media, MessageMediaDocument):
                media_type = "document/video/audio"

            await send_log_to_bot(client, "media_received", {
                "media_type": media_type,
                "from": from_text,
                "message": event.message
            })
        elif event.text:
            await send_log_to_bot(client, "incoming", {
                "text": event.text,
                "from": from_text,
                "chat": chat_name
            })
    except:
        pass


print("✅ Userbot Logger loaded")
