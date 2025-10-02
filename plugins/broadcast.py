"""
VZ ASSISTANT v0.0.0.69
Broadcast Plugin - Group Broadcast & Blacklist Management

2025© Vzoel Fox's Lutpan
Founder & DEVELOPER : @VZLfxs
"""

from telethon import events, Button
from telethon.tl.types import Channel, Chat
import asyncio
import json
import os
import config
from utils.animation import animate_loading

# Global variables (set by main.py)
vz_client = None
vz_emoji = None

# ============================================================================
# BLACKLIST MANAGEMENT
# ============================================================================

def get_blacklist_path(user_id):
    """Get blacklist JSON path for user."""
    return config.get_sudoer_json_path(user_id, "blgc.json")

def load_blacklist(user_id):
    """Load blacklist from JSON."""
    path = get_blacklist_path(user_id)
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    return []

def save_blacklist(user_id, blacklist):
    """Save blacklist to JSON."""
    path = get_blacklist_path(user_id)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        json.dump(blacklist, f, indent=2)

# ============================================================================
# BLACKLIST ADD COMMAND
# ============================================================================

@events.register(events.NewMessage(pattern=r'^\.bl(-?\d+)?$', outgoing=True))
async def bl_handler(event):
    global vz_client, vz_emoji

    """
    .bl - Add group to blacklist

    Usage:
        .bl                    (add current group)
        .bl -1001234567890     (add specific group ID)

    Blacklisted groups won't receive .gcast broadcasts.
    """
    user_id = event.sender_id

    # Get chat ID
    chat_id = event.pattern_match.group(1)

    if chat_id:
        chat_id = int(chat_id)
    else:
        chat_id = event.chat_id

    # Load blacklist
    blacklist = load_blacklist(user_id)

    # Check if already blacklisted
    if chat_id in blacklist:
        await vz_client.edit_with_premium_emoji(event, f"⚠️ Group `{chat_id}` is already blacklisted!")
        return

    # Add to blacklist
    blacklist.append(chat_id)
    save_blacklist(user_id, blacklist)

    # Get chat info
    try:
        chat = await event.client.get_entity(chat_id)
        chat_name = getattr(chat, 'title', 'Unknown')
    except:
        chat_name = 'Unknown'

    result_text = f"""
✅ **Blacklist Added**

**📁 Group:** {chat_name}
**🆔 ID:** `{chat_id}`
**📊 Total Blacklisted:** {len(blacklist)}

💡 This group will be skipped during .gcast

{gear_emoji} Plugins Digunakan: **BROADCAST**
{petir_emoji} by {main_emoji} Vzoel Fox's Lutpan
"""

    await vz_client.edit_with_premium_emoji(event, result_text)

# ============================================================================
# BLACKLIST REMOVE COMMAND
# ============================================================================

@events.register(events.NewMessage(pattern=r'^\.dbl(-?\d+)?$', outgoing=True))
async def dbl_handler(event):
    global vz_client, vz_emoji

    """
    .dbl - Remove group from blacklist

    Usage:
        .dbl                   (remove current group)
        .dbl -1001234567890    (remove specific group ID)
    """
    user_id = event.sender_id

    # Get chat ID
    chat_id = event.pattern_match.group(1)

    if chat_id:
        chat_id = int(chat_id)
    else:
        chat_id = event.chat_id

    # Load blacklist
    blacklist = load_blacklist(user_id)

    # Check if in blacklist
    if chat_id not in blacklist:
        await vz_client.edit_with_premium_emoji(event, f"⚠️ Group `{chat_id}` is not blacklisted!")
        return

    # Remove from blacklist
    blacklist.remove(chat_id)
    save_blacklist(user_id, blacklist)

    # Get chat info
    try:
        chat = await event.client.get_entity(chat_id)
        chat_name = getattr(chat, 'title', 'Unknown')
    except:
        chat_name = 'Unknown'

    result_text = f"""
✅ **Blacklist Removed**

**📁 Group:** {chat_name}
**🆔 ID:** `{chat_id}`
**📊 Total Blacklisted:** {len(blacklist)}

💡 This group will now receive .gcast broadcasts

{gear_emoji} Plugins Digunakan: **BROADCAST**
{petir_emoji} by {main_emoji} Vzoel Fox's Lutpan
"""

    await vz_client.edit_with_premium_emoji(event, result_text)

# ============================================================================
# BROADCAST COMMAND
# ============================================================================

@events.register(events.NewMessage(pattern=r'^\.gcast(\s+[\s\S]+)?$', outgoing=True))
async def gcast_handler(event):
    global vz_client, vz_emoji

    """
    .gcast - Broadcast message to all groups

    Usage:
        .gcast <message>       (broadcast text)
        .gcast (reply)         (broadcast replied message)

    Skips blacklisted groups automatically.
    """
    user_id = event.sender_id

    # Get message to broadcast
    reply = await event.get_reply_message()
    text_to_send = event.pattern_match.group(1)

    if reply:
        message_to_broadcast = reply
        is_reply = True
    elif text_to_send:
        text_to_send = text_to_send.strip()
        message_to_broadcast = text_to_send
        is_reply = False
    else:
        await vz_client.edit_with_premium_emoji(event, "❌ Usage: `.gcast <message>` or `.gcast` (reply to message)")
        return

    # Load blacklist
    blacklist = load_blacklist(user_id)

    # Run 12-phase animation
    msg = await animate_loading(vz_client, vz_emoji, event)

    # Get all dialogs (groups/channels)
    dialogs = await event.client.get_dialogs()

    # Filter for groups and channels only
    groups = []
    for dialog in dialogs:
        entity = dialog.entity
        if isinstance(entity, (Channel, Chat)):
            # Skip blacklisted
            if entity.id not in blacklist and -entity.id not in blacklist:
                groups.append(dialog)

    total_groups = len(groups)

    if total_groups == 0:
        await vz_client.edit_with_premium_emoji(event, "❌ No groups to broadcast to!")
        return

    # Confirm broadcast
    await vz_client.edit_with_premium_emoji(event, f"""
📢 **Broadcast Ready**

**📊 Statistics:**
├ Total Groups: {len(dialogs)}
├ Blacklisted: {len(blacklist)}
└ Will Broadcast: {total_groups}

🔄 Starting broadcast in 3 seconds...
""")

    await asyncio.sleep(3)

    # Start broadcasting
    success = 0
    failed = 0
    msg = await vz_client.edit_with_premium_emoji(event, f"📡 Broadcasting... 0/{total_groups}")

    for i, dialog in enumerate(groups, 1):
        try:
            if is_reply:
                # Forward the message
                await event.client.send_message(
                    dialog.entity,
                    message_to_broadcast
                )
            else:
                # Send text
                await event.client.send_message(
                    dialog.entity,
                    message_to_broadcast
                )

            success += 1

            # Update progress every 5 groups
            if i % 5 == 0 or i == total_groups:
                await msg.edit(f"📡 Broadcasting... {i}/{total_groups}\n✅ Success: {success} | ❌ Failed: {failed}")

            # Delay to avoid flood
            await asyncio.sleep(config.GCAST_DELAY)

        except Exception as e:
            failed += 1
            print(f"Failed to broadcast to {dialog.name}: {e}")

    # Final report
    result_text = f"""
✅ **Broadcast Complete**

**📊 Results:**
├ Total Groups: {total_groups}
├ Success: {success} ✅
├ Failed: {failed} ❌
└ Blacklisted: {len(blacklist)} 🚫

**⏱ Duration:** ~{total_groups * config.GCAST_DELAY:.1f}s

{gear_emoji} Plugins Digunakan: **BROADCAST**
{petir_emoji} by {main_emoji} Vzoel Fox's Lutpan
"""

    await msg.edit(result_text)

# ============================================================================
# VIEW BLACKLIST COMMAND
# ============================================================================

@events.register(events.NewMessage(pattern=r'^\.bllist$', outgoing=True))
async def bllist_handler(event):
    global vz_client, vz_emoji

    """
    .bllist - View blacklisted groups

    Shows all groups in blacklist with names.
    """
    user_id = event.sender_id

    # Load blacklist
    blacklist = load_blacklist(user_id)

    if not blacklist:
        await vz_client.edit_with_premium_emoji(event, "ℹ️ Blacklist is empty!")
        return

    # Run 12-phase animation
    msg = await animate_loading(vz_client, vz_emoji, event)

    # Get group names
    bl_text = f"""
🚫 **Blacklist - {len(blacklist)} Groups**

"""

    for i, chat_id in enumerate(blacklist, 1):
        try:
            chat = await event.client.get_entity(chat_id)
            chat_name = getattr(chat, 'title', 'Unknown')
            bl_text += f"{i}. **{chat_name}**\n   `{chat_id}`\n\n"
        except:
            bl_text += f"{i}. Unknown Group\n   `{chat_id}`\n\n"

        # Limit to 20 groups
        if i >= 20:
            bl_text += f"... and {len(blacklist) - 20} more\n\n"
            break

    bl_text += f"""
💡 Use `.dbl <id>` to remove from blacklist

{gear_emoji} Plugins Digunakan: **BROADCAST**
{petir_emoji} by {main_emoji} Vzoel Fox's Lutpan"""

    await vz_client.edit_with_premium_emoji(event, bl_text)

print("✅ Plugin loaded: broadcast.py")
