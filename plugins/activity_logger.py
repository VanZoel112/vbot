"""
VZ ASSISTANT v0.0.0.69
Activity Logger - Forward all userbot activity to assistant bot

Logs:
- Outgoing messages (sent by userbot)
- Incoming messages (received by userbot)
- Media sent/received
- Commands executed

Flow:
1. Userbot sends/receives message
2. Logger catches event
3. Send to assistant bot via PM
4. Bot forwards to log group
5. Bot auto-deletes message (no trace)

2025© Vzoel Fox's Lutpan
Founder & DEVELOPER : @VZLfxs
"""

from telethon import events
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument
import os
import config
from datetime import datetime

# Global variables (set by main.py)
vz_client = None
vz_emoji = None

# Get assistant bot username
ASSISTANT_BOT_USERNAME = os.getenv("ASSISTANT_BOT_USERNAME", "").lstrip("@")

# ============================================================================
# OUTGOING MESSAGE LOGGER
# ============================================================================

@events.register(events.NewMessage(outgoing=True))
async def log_outgoing_message(event):
    """
    Log all outgoing messages to assistant bot.

    Catches:
    - Regular messages sent by user
    - Commands executed
    - Media sent
    """
    global vz_client, vz_emoji

    # Skip if no assistant bot configured
    if not ASSISTANT_BOT_USERNAME:
        return

    # Skip messages to assistant bot itself (prevent loop)
    if event.is_private and event.chat:
        try:
            chat_entity = await event.get_chat()
            if hasattr(chat_entity, 'username') and chat_entity.username == ASSISTANT_BOT_USERNAME:
                return
        except:
            pass

    # Build log message
    try:
        # Get chat info
        chat = await event.get_chat()
        chat_name = getattr(chat, 'title', None) or getattr(chat, 'first_name', 'Unknown')
        chat_id = event.chat_id
        chat_type = "Group" if event.is_group else ("Channel" if event.is_channel else "Private")

        # Get message text
        message_text = event.text or "[Media/Sticker]"
        if len(message_text) > 200:
            message_text = message_text[:200] + "..."

        # Build log
        log_text = f"""
📤 **OUTGOING MESSAGE**

**Chat:** {chat_name}
**Type:** {chat_type}
**ID:** `{chat_id}`
**Time:** {datetime.now().strftime('%H:%M:%S')}

**Message:**
```
{message_text}
```
"""

        # Send to assistant bot
        bot_entity = await vz_client.client.get_entity(ASSISTANT_BOT_USERNAME)

        # If media, forward the whole message
        if event.media:
            await vz_client.client.send_message(
                bot_entity,
                log_text
            )
            # Forward media separately
            await vz_client.client.forward_messages(
                bot_entity,
                event.message
            )
        else:
            # Send text log only
            await vz_client.client.send_message(
                bot_entity,
                log_text
            )

    except Exception as e:
        # Silently fail - don't interrupt user experience
        pass

# ============================================================================
# INCOMING MESSAGE LOGGER
# ============================================================================

@events.register(events.NewMessage(incoming=True))
async def log_incoming_message(event):
    """
    Log all incoming messages to assistant bot.

    Catches:
    - Messages received from others
    - Media received
    - Replies received
    """
    global vz_client, vz_emoji

    # Skip if no assistant bot configured
    if not ASSISTANT_BOT_USERNAME:
        return

    # Skip messages from assistant bot itself (prevent loop)
    if event.is_private and event.sender:
        try:
            if hasattr(event.sender, 'username') and event.sender.username == ASSISTANT_BOT_USERNAME:
                return
        except:
            pass

    # Skip group messages (too noisy) - only log private chats
    if event.is_group or event.is_channel:
        return

    # Build log message
    try:
        # Get sender info
        sender = await event.get_sender()
        sender_name = getattr(sender, 'first_name', 'Unknown')
        sender_username = getattr(sender, 'username', None)
        sender_id = event.sender_id

        # Get message text
        message_text = event.text or "[Media/Sticker]"
        if len(message_text) > 200:
            message_text = message_text[:200] + "..."

        # Build log
        log_text = f"""
📥 **INCOMING MESSAGE**

**From:** {sender_name}
**Username:** @{sender_username or 'none'}
**ID:** `{sender_id}`
**Time:** {datetime.now().strftime('%H:%M:%S')}

**Message:**
```
{message_text}
```
"""

        # Send to assistant bot
        bot_entity = await vz_client.client.get_entity(ASSISTANT_BOT_USERNAME)

        # If media, forward the whole message
        if event.media:
            await vz_client.client.send_message(
                bot_entity,
                log_text
            )
            # Forward media separately
            await vz_client.client.forward_messages(
                bot_entity,
                event.message
            )
        else:
            # Send text log only
            await vz_client.client.send_message(
                bot_entity,
                log_text
            )

    except Exception as e:
        # Silently fail - don't interrupt user experience
        pass

print("✅ Plugin loaded: activity_logger.py")
