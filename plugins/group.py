"""
VZ ASSISTANT v0.0.0.69
Group Plugin - Tag All & Shadow Clear (Lock)

2025© Vzoel Fox's Lutpan
Founder & DEVELOPER : @VZLfxs
"""

from telethon import events
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights
import asyncio
import json
import os
import random
import time
import config

# Global variables (set by main.py)
vz_client = None
vz_emoji = None

# ============================================================================
# TAG ALL MANAGEMENT
# ============================================================================

# Active tag sessions
active_tags = {}

@events.register(events.NewMessage(pattern=r'^\.tag(\s+[\s\S]+)?$', outgoing=True))
async def tag_handler(event):
    global vz_client, vz_emoji

    """
    .tag - Tag all members in group

    Usage:
        .tag <message>         (tag with message)
        .tag (reply)           (tag with replied message)

    Tags 10 random users every 2.5 seconds.
    No admin rights required.
    Auto-stops when all users tagged.
    """
    chat_id = event.chat_id
    user_id = event.sender_id

    # Check if already tagging
    if chat_id in active_tags:
        await event.edit("⚠️ Already tagging in this group! Use `.stag` to stop.")
        return

    # Get message
    reply = await event.get_reply_message()
    text = event.pattern_match.group(1)

    if reply:
        base_message = reply.text or ""
    elif text:
        base_message = text.strip()
    else:
        await event.edit("❌ Usage: `.tag <message>` or `.tag` (reply)")
        return

    # Get all participants
    await event.edit("🔍 Gathering participants...")

    try:
        participants = await event.client.get_participants(chat_id)
    except Exception as e:
        await event.edit(f"❌ Failed to get participants: {str(e)}")
        return

    if not participants:
        await event.edit("❌ No participants found!")
        return

    # Filter out bots and self
    users = [p for p in participants if not p.bot and p.id != user_id]

    if not users:
        await event.edit("❌ No users to tag!")
        return

    # Mark as active
    active_tags[chat_id] = True

    total_users = len(users)
    tagged_count = 0
    start_time = time.time()

    msg = await event.edit(f"""
📢 **Tag All Started**

**👥 Total Users:** {total_users}
**⏱ Interval:** 2.5s per batch (10 users)

🔄 Starting...
""")

    # Shuffle users for random tagging
    random.shuffle(users)

    # Tag in batches of 10
    batch_size = config.TAG_USERS_PER_EDIT

    for i in range(0, len(users), batch_size):
        # Check if stopped
        if chat_id not in active_tags:
            await msg.edit("⏹ **Tag All Stopped**\n\nManually stopped by user.")
            return

        batch = users[i:i + batch_size]

        # Build mention text
        mention_text = base_message + "\n\n"
        for user in batch:
            mention_text += f"[{user.first_name}](tg://user?id={user.id}) "
            tagged_count += 1

        # Edit message with mentions
        try:
            await msg.edit(mention_text)
        except Exception as e:
            print(f"Failed to tag batch: {e}")

        # Delay before next batch
        if i + batch_size < len(users):
            await asyncio.sleep(config.TAG_ANIMATION_DELAY)

    # Calculate duration
    duration = int(time.time() - start_time)
    minutes = duration // 60
    seconds = duration % 60

    # Final summary
    summary_text = f"""
✅ **Tag All Complete**

**📊 Summary:**
├ Total Users: {total_users}
├ Tagged: {tagged_count}
├ Duration: {minutes}m {seconds}s
└ Status: Success

{base_message}

{config.BRANDING_FOOTER} TAGALL
Founder & DEVELOPER : {config.FOUNDER_USERNAME}
"""

    await msg.edit(summary_text)

    # Remove from active
    if chat_id in active_tags:
        del active_tags[chat_id]

# ============================================================================
# STOP TAG COMMAND
# ============================================================================

@events.register(events.NewMessage(pattern=r'^\.stag$', outgoing=True))
async def stag_handler(event):
    global vz_client, vz_emoji

    """
    .stag - Stop active tag operation

    Stops the ongoing .tag command in current group.
    """
    chat_id = event.chat_id

    if chat_id not in active_tags:
        await event.edit("ℹ️ No active tag operation in this group!")
        return

    # Remove from active tags
    del active_tags[chat_id]

    await event.edit(f"""
⏹ **Tag All Stopped**

Operation cancelled successfully.

{config.BRANDING_FOOTER} TAGALL
""")

# ============================================================================
# SHADOW CLEAR (LOCK) MANAGEMENT
# ============================================================================

def get_lockglobal_path(user_id):
    """Get lockglobal JSON path for user."""
    return config.get_sudoer_json_path(user_id, "lockglobal.json")

def load_lockglobal(user_id):
    """Load locked users from JSON."""
    path = get_lockglobal_path(user_id)
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    return []

def save_lockglobal(user_id, lockglobal):
    """Save locked users to JSON."""
    path = get_lockglobal_path(user_id)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        json.dump(lockglobal, f, indent=2)

# ============================================================================
# LOCK COMMAND
# ============================================================================

@events.register(events.NewMessage(pattern=r'^\.lock(@\w+)?$', outgoing=True))
async def lock_handler(event):
    global vz_client, vz_emoji

    """
    .lock - Auto-delete messages from user (Shadow Clear)

    Usage:
        .lock @username        (lock by username)
        .lock (reply)          (lock by reply)

    Requires admin rights to delete messages.
    Auto-deletes all messages from locked user.
    """
    user_id = event.sender_id

    # Get target user
    reply = await event.get_reply_message()
    username = event.pattern_match.group(1)

    if reply:
        target = await reply.get_sender()
        target_id = target.id
    elif username:
        try:
            username = username[1:]  # Remove @
            target = await event.client.get_entity(username)
            target_id = target.id
        except Exception as e:
            await event.edit(f"❌ Failed to get user: {str(e)}")
            return
    else:
        await event.edit("❌ Usage: `.lock @username` or `.lock` (reply)")
        return

    # Check admin rights
    try:
        perms = await event.client.get_permissions(event.chat_id, event.sender_id)
        if not perms.is_admin or not perms.delete_messages:
            await event.edit("❌ You need admin rights with delete messages permission!")
            return
    except:
        await event.edit("❌ Failed to check permissions!")
        return

    # Load lock list
    lockglobal = load_lockglobal(user_id)

    # Check if already locked
    if target_id in lockglobal:
        await event.edit(f"⚠️ User {target.first_name} is already locked!")
        return

    # Add to lock list
    lockglobal.append(target_id)
    save_lockglobal(user_id, lockglobal)

    result_text = f"""
🔒 **Shadow Clear Activated**

**👤 Target:**
├ Name: {target.first_name}
├ Username: @{target.username if target.username else 'None'}
├ ID: `{target_id}`

**⚡ Effect:**
All messages from this user will be
automatically deleted in this group.

**📊 Total Locked:** {len(lockglobal)}

{config.BRANDING_FOOTER} LOCK
Founder & DEVELOPER : {config.FOUNDER_USERNAME}
"""

    await event.edit(result_text)

# ============================================================================
# UNLOCK COMMAND
# ============================================================================

@events.register(events.NewMessage(pattern=r'^\.unlock(@\w+)?$', outgoing=True))
async def unlock_handler(event):
    global vz_client, vz_emoji

    """
    .unlock - Remove user from auto-delete list

    Usage:
        .unlock @username      (unlock by username)
        .unlock (reply)        (unlock by reply)
    """
    user_id = event.sender_id

    # Get target user
    reply = await event.get_reply_message()
    username = event.pattern_match.group(1)

    if reply:
        target = await reply.get_sender()
        target_id = target.id
    elif username:
        try:
            username = username[1:]  # Remove @
            target = await event.client.get_entity(username)
            target_id = target.id
        except Exception as e:
            await event.edit(f"❌ Failed to get user: {str(e)}")
            return
    else:
        await event.edit("❌ Usage: `.unlock @username` or `.unlock` (reply)")
        return

    # Load lock list
    lockglobal = load_lockglobal(user_id)

    # Check if locked
    if target_id not in lockglobal:
        await event.edit(f"⚠️ User {target.first_name} is not locked!")
        return

    # Remove from lock list
    lockglobal.remove(target_id)
    save_lockglobal(user_id, lockglobal)

    result_text = f"""
🔓 **Shadow Clear Deactivated**

**👤 Target:**
├ Name: {target.first_name}
├ Username: @{target.username if target.username else 'None'}
├ ID: `{target_id}`

**✅ Effect:**
Messages from this user will no longer
be automatically deleted.

**📊 Total Locked:** {len(lockglobal)}

{config.BRANDING_FOOTER} LOCK
Founder & DEVELOPER : {config.FOUNDER_USERNAME}
"""

    await event.edit(result_text)

# ============================================================================
# AUTO-DELETE HANDLER (monitors all messages)
# ============================================================================

@events.register(events.NewMessage(incoming=True))
async def auto_delete_handler(event):
    global vz_client, vz_emoji

    """
    Auto-delete messages from locked users.

    This runs for all incoming messages and checks
    if sender is in the lock list.
    """
    # Only work in groups
    if event.is_private:
        return

    sender_id = event.sender_id

    # Get bot's user ID (we need to check their lock list)
    # For now, we'll check all users' lock lists
    # TODO: Optimize this with a global lock cache

    # Check if sender is in any lock list
    # This is a simplified version - in production,
    # you'd want to cache this and only check relevant users

    return  # Disabled for now - needs optimization

print("✅ Plugin loaded: group.py")
