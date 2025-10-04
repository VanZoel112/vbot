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
from utils.animation import animate_loading
from helpers.error_handler import ErrorFormatter

# Global variables (set by main.py)
vz_client = None
vz_emoji = None
error_fmt = None

# ============================================================================
# TAG ALL MANAGEMENT
# ============================================================================

# Active tag sessions
active_tags = {}

@events.register(events.NewMessage(pattern=r'^\.tag(\s+[\s\S]+)?$', outgoing=True))
async def tag_handler(event):
    global vz_client, vz_emoji, error_fmt

    """
    .tag - Tag all members in group

    Usage:
        .tag <message>         (tag with message)
        .tag (reply)           (tag with replied message)

    Tags 10 random users every 2.5 seconds.
    No admin rights required.
    Auto-stops when all users tagged.
    """
    # Initialize error formatter if needed
    if error_fmt is None:
        error_fmt = ErrorFormatter(vz_emoji)

    chat_id = event.chat_id
    user_id = event.sender_id

    # Check if already tagging
    if chat_id in active_tags:
        await vz_client.edit_with_premium_emoji(
            event,
            error_fmt.warning("Already tagging in this group! Use `.stag` to stop.")
        )
        return

    # Run 12-phase animation
    msg = await animate_loading(vz_client, vz_emoji, event)

    # Get message
    reply = await event.get_reply_message()
    text = event.pattern_match.group(1)

    if reply:
        base_message = reply.text or ""
    elif text:
        base_message = text.strip()
    else:
        await vz_client.edit_with_premium_emoji(
            event,
            error_fmt.usage_error(
                "tag",
                ".tag <message> or .tag (reply)",
                ".tag Hello everyone!"
            )
        )
        return

    # Get all participants
    await vz_client.edit_with_premium_emoji(event, f"{vz_emoji.getemoji('gear')} Gathering participants...")

    try:
        participants = await event.client.get_participants(chat_id)
    except Exception as e:
        await vz_client.edit_with_premium_emoji(
            event,
            f"{error_fmt.error_emoji} **Failed to get participants:** `{str(e)}`"
        )
        return

    if not participants:
        await vz_client.edit_with_premium_emoji(
            event,
            f"{error_fmt.error_emoji} **No participants found!**"
        )
        return

    # Filter out bots and self
    users = [p for p in participants if not p.bot and p.id != user_id]

    if not users:
        await vz_client.edit_with_premium_emoji(
            event,
            f"{error_fmt.error_emoji} **No users to tag!**"
        )
        return

    # Mark as active
    active_tags[chat_id] = True

    total_users = len(users)
    tagged_count = 0
    start_time = time.time()

    msg = await vz_client.edit_with_premium_emoji(event, f"""
{vz_emoji.getemoji('petir')} **Tag All Started**

**{vz_emoji.getemoji('owner')} Total Users:** {total_users}
**{vz_emoji.getemoji('gear')} Interval:** 2.5s per batch (10 users)

{vz_emoji.getemoji('loading')} Starting...
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

    # Get emojis for footer
    gear_emoji = vz_emoji.getemoji('gear')
    petir_emoji = vz_emoji.getemoji('petir')
    main_emoji = vz_emoji.getemoji('utama')

    # Get success emoji
    success_emoji = vz_emoji.getemoji('centang')

    # Final summary
    summary_text = f"""
{success_emoji} **Tag All Complete**

**{gear_emoji} Summary:**
├ Total Users: {total_users}
├ Tagged: {tagged_count}
├ Duration: {minutes}m {seconds}s
└ Status: Success

{base_message}

{gear_emoji} Plugins Digunakan: **GROUP**
{petir_emoji} by {main_emoji} Vzoel Fox's Lutpan
"""

    await msg.edit(summary_text)

    # Remove from active
    if chat_id in active_tags:
        del active_tags[chat_id]

# Note: .stag handler moved to end of file to handle both .tag and .tagall

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

@events.register(events.NewMessage(pattern=r'^\.lock( (.+))?$', outgoing=True))
async def lock_handler(event):
    global vz_client, vz_emoji, error_fmt

    """
    .lock - Auto-delete messages from user (Shadow Clear)

    Usage:
        .lock @username        (lock by username)
        .lock (reply)          (lock by reply)

    Requires admin rights to delete messages.
    Auto-deletes all messages from locked user.
    """
    # Initialize error formatter if needed
    if error_fmt is None:
        error_fmt = ErrorFormatter(vz_emoji)

    user_id = event.sender_id

    # Get target user
    reply = await event.get_reply_message()
    args = event.pattern_match.group(2)

    if reply:
        target = await reply.get_sender()
        target_id = target.id
    elif args:
        try:
            username = args.strip().replace('@', '')
            target = await event.client.get_entity(username)
            target_id = target.id
        except Exception as e:
            await vz_client.edit_with_premium_emoji(event, error_fmt.failed_to_get_user(str(e)))
            return
    else:
        await vz_client.edit_with_premium_emoji(
            event,
            error_fmt.usage_error(
                "lock",
                ".lock @username or .lock (reply)",
                ".lock @spammer"
            )
        )
        return

    # Check admin rights
    try:
        perms = await event.client.get_permissions(event.chat_id, event.sender_id)
        if not perms.is_admin or not perms.delete_messages:
            await vz_client.edit_with_premium_emoji(
                event,
                error_fmt.permission_denied("admin rights with delete messages")
            )
            return
    except:
        await vz_client.edit_with_premium_emoji(
            event,
            f"{error_fmt.error_emoji} **Failed to check permissions!**"
        )
        return

    # Load lock list
    lockglobal = load_lockglobal(user_id)

    # Check if already locked
    if target_id in lockglobal:
        await vz_client.edit_with_premium_emoji(
            event,
            error_fmt.warning(f"User {target.first_name} is already locked!")
        )
        return

    # Add to lock list
    lockglobal.append(target_id)
    save_lockglobal(user_id, lockglobal)

    # Get emojis for footer
    gear_emoji = vz_emoji.getemoji('gear')
    petir_emoji = vz_emoji.getemoji('petir')
    main_emoji = vz_emoji.getemoji('utama')

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

{gear_emoji} Plugins Digunakan: **GROUP**
{petir_emoji} by {main_emoji} Vzoel Fox's Lutpan
"""

    await vz_client.edit_with_premium_emoji(event, result_text)

# ============================================================================
# UNLOCK COMMAND
# ============================================================================

@events.register(events.NewMessage(pattern=r'^\.unlock( (.+))?$', outgoing=True))
async def unlock_handler(event):
    global vz_client, vz_emoji, error_fmt

    """
    .unlock - Remove user from auto-delete list

    Usage:
        .unlock @username      (unlock by username)
        .unlock (reply)        (unlock by reply)
    """
    # Initialize error formatter if needed
    if error_fmt is None:
        error_fmt = ErrorFormatter(vz_emoji)

    user_id = event.sender_id

    # Get target user
    reply = await event.get_reply_message()
    args = event.pattern_match.group(2)

    if reply:
        target = await reply.get_sender()
        target_id = target.id
    elif args:
        try:
            username = args.strip().replace('@', '')
            target = await event.client.get_entity(username)
            target_id = target.id
        except Exception as e:
            await vz_client.edit_with_premium_emoji(event, error_fmt.failed_to_get_user(str(e)))
            return
    else:
        await vz_client.edit_with_premium_emoji(
            event,
            error_fmt.usage_error(
                "unlock",
                ".unlock @username or .unlock (reply)",
                ".unlock @user123"
            )
        )
        return

    # Load lock list
    lockglobal = load_lockglobal(user_id)

    # Check if locked
    if target_id not in lockglobal:
        await vz_client.edit_with_premium_emoji(
            event,
            error_fmt.warning(f"User {target.first_name} is not locked!")
        )
        return

    # Remove from lock list
    lockglobal.remove(target_id)
    save_lockglobal(user_id, lockglobal)

    # Get emojis for footer
    gear_emoji = vz_emoji.getemoji('gear')
    petir_emoji = vz_emoji.getemoji('petir')
    main_emoji = vz_emoji.getemoji('utama')

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

{gear_emoji} Plugins Digunakan: **GROUP**
{petir_emoji} by {main_emoji} Vzoel Fox's Lutpan
"""

    await vz_client.edit_with_premium_emoji(event, result_text)

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
    # Skip if it's our own message
    try:
        me = await event.client.get_me()
        if event.sender_id == me.id:
            return
    except:
        return

    # Only work in groups
    if event.is_private:
        return

    sender_id = event.sender_id

    # Get owner's user ID from the client
    # In multi-client setup, each client has its own lock list
    try:
        me = await event.client.get_me()
        my_id = me.id

        # Load lock list for this client owner
        lockglobal = load_lockglobal(my_id)

        # Check if sender is locked
        if sender_id in lockglobal:
            try:
                await event.delete()
            except Exception as e:
                # Can't delete (no permission or other error)
                pass
    except Exception as e:
        # Log error but don't break
        print(f"Auto-delete error: {e}")

# ============================================================================
# SMART BATCH TAGALL (vzl2 pattern)
# ============================================================================

# Global variables for tagall state
tagall_tasks = {}
tagall_active = {}
tagall_messages = {}  # Store tagall messages for editing
tagall_progress = {}  # Track progress per chat

@events.register(events.NewMessage(pattern=r'^\.tagall( (.+))?$', outgoing=True))
async def tagall_handler(event):
    """
    .tagall - Smart batch tag all members (vzl2 pattern)

    Usage:
        .tagall <message>      (tag with message)
        .tagall (reply)        (tag with replied message)

    Smart batch editing: 5 users per edit
    Premium emoji mapping for visual appeal
    """
    global vz_client, vz_emoji, error_fmt, tagall_tasks, tagall_active, tagall_messages, tagall_progress

    # Initialize error formatter if needed
    if error_fmt is None:
        error_fmt = ErrorFormatter(vz_emoji)

    # Check if we're in a group
    if event.is_private:
        await vz_client.edit_with_premium_emoji(
            event,
            error_fmt.error("Tagall hanya bisa digunakan di grup")
        )
        return

    chat_id = event.chat_id
    user_id = event.sender_id

    # Stop any existing tagall in this chat
    if chat_id in tagall_tasks and not tagall_tasks[chat_id].done():
        tagall_tasks[chat_id].cancel()
        tagall_active[chat_id] = False

    # Get message content
    message_text = ""
    reply = await event.get_reply_message()
    args = event.pattern_match.group(2)

    if reply:
        message_text = reply.text or ""
    elif args:
        message_text = args.strip()

    # Start tagall process
    tagall_active[chat_id] = True

    # Initial process message
    loading_emoji = vz_emoji.getemoji('loading')
    proses_emoji = vz_emoji.getemoji('proses')
    centang_emoji = vz_emoji.getemoji('centang')

    process_msg = f"{loading_emoji} Memulai proses tagall..."
    msg = await vz_client.edit_with_premium_emoji(event, process_msg)

    # Get chat info
    try:
        chat = await event.get_chat()
        chat_title = chat.title

        # Get all members
        import asyncio
        await asyncio.sleep(1)
        await vz_client.edit_with_premium_emoji(msg, f"{proses_emoji} Mengambil daftar member dari {chat_title}...")

        participants = []
        async for user in event.client.iter_participants(chat_id):
            if not user.bot and not user.deleted and user.id != user_id:
                participants.append(user)

        if not participants:
            await vz_client.edit_with_premium_emoji(
                msg,
                error_fmt.warning("Tidak ada member yang bisa di-tag")
            )
            return

        await asyncio.sleep(1)
        await vz_client.edit_with_premium_emoji(msg, f"{centang_emoji} Ditemukan {len(participants)} member. Memulai tagall...")

        # Initialize tagall tracking
        tagall_progress[chat_id] = {'total': len(participants), 'processed': 0}

        # Start tagall task
        tagall_tasks[chat_id] = asyncio.create_task(
            perform_smart_batch_tagall(event, msg, participants, message_text, chat_title)
        )

        # Wait for task completion
        try:
            await tagall_tasks[chat_id]
        except asyncio.CancelledError:
            kuning_emoji = vz_emoji.getemoji('kuning')
            await vz_client.edit_with_premium_emoji(msg, f"{kuning_emoji} Tagall dihentikan oleh pengguna")

    except Exception as e:
        await vz_client.edit_with_premium_emoji(msg, error_fmt.error(f"Error saat tagall: {str(e)}"))
    finally:
        tagall_active[chat_id] = False
        # Clean up tracking data
        if chat_id in tagall_progress:
            del tagall_progress[chat_id]
        if chat_id in tagall_messages:
            del tagall_messages[chat_id]

async def perform_smart_batch_tagall(event, status_msg, participants, message_text, chat_title):
    """Perform tagall with smart batch editing system - 5 users per message edit (vzl2 pattern)"""
    global vz_client, vz_emoji, tagall_active, tagall_messages, tagall_progress

    chat_id = event.chat_id
    total_users = len(participants)
    processed_count = 0
    batch_size = 5

    # Premium emoji mapping for visual appeal (vzl2 pattern)
    emoji_mapping = {
        0: 'utama',    # Main emoji
        1: 'centang',  # Success
        2: 'petir',    # Power
        3: 'aktif',    # Active
        4: 'adder1'    # Special
    }

    # Status emojis for different phases
    status_emojis = ['loading', 'proses', 'kuning', 'biru', 'merah']

    # Create initial tagall message that will be edited with user batches
    initial_emoji = vz_emoji.getemoji('loading')
    initial_msg = f"{initial_emoji} Memulai smart batch tagall..."
    tagall_msg = await event.client.send_message(chat_id, initial_msg)
    tagall_messages[chat_id] = tagall_msg

    # Process users in batches of 5
    for i in range(0, total_users, batch_size):
        if not tagall_active.get(chat_id, False):
            break

        try:
            batch = participants[i:i + batch_size]
            batch_mentions = []
            batch_display = []

            # Process each user in the current batch
            for idx, participant in enumerate(batch):
                if not tagall_active.get(chat_id, False):
                    break

                # Get user info
                username = f"@{participant.username}" if participant.username else "User"
                full_name = f"{participant.first_name or ''} {participant.last_name or ''}".strip()
                if not full_name:
                    full_name = "Unknown User"

                # Create mention link
                mention = f"[{full_name}](tg://user?id={participant.id})"
                batch_mentions.append(mention)

                # Get emoji for this position in batch
                emoji_key = emoji_mapping.get(idx, 'telegram')
                emoji_char = vz_emoji.getemoji(emoji_key)

                # Create display info
                batch_display.append(f"{emoji_char} {full_name}")
                processed_count += 1

            # Create batch message with mentions and message text
            if batch_mentions:
                mention_text = " ".join(batch_mentions)
                if message_text:
                    batch_message = f"{mention_text} {message_text}"
                else:
                    batch_message = mention_text

                # Edit the tagall message with current batch info
                batch_number = (i // batch_size) + 1
                total_batches = (total_users + batch_size - 1) // batch_size

                petir_emoji = vz_emoji.getemoji('petir')
                centang_emoji = vz_emoji.getemoji('centang')
                aktif_emoji = vz_emoji.getemoji('aktif')
                telegram_emoji = vz_emoji.getemoji('telegram')
                progress_emoji = vz_emoji.getemoji(random.choice(status_emojis))

                status_display = f"""{petir_emoji} **VZ ASSISTANT SMART BATCH TAGALL**

{centang_emoji} Batch {batch_number}/{total_batches} - Target Users:

""" + "\n".join(batch_display) + f"""

{progress_emoji} Progress: {processed_count}/{total_users} users
{aktif_emoji} Pesan: {message_text or 'Default tagall'}
{telegram_emoji} Grup: {chat_title}

By Vzoel Fox's Assistant"""

                # Edit the main tracking message
                await vz_client.edit_with_premium_emoji(status_msg, status_display)

                # Edit the tagall message with the actual mentions
                await tagall_msg.edit(batch_message)

                # Update progress tracking
                tagall_progress[chat_id]['processed'] = processed_count

                # Delay between batches to avoid flood
                await asyncio.sleep(3)

        except Exception as e:
            # Skip problematic batch and continue
            print(f"[Tagall] Error in batch {i//batch_size + 1}: {e}")
            continue

    # Final completion message with success summary
    if tagall_active.get(chat_id, False):
        centang_emoji = vz_emoji.getemoji('centang')
        utama_emoji = vz_emoji.getemoji('utama')
        petir_emoji = vz_emoji.getemoji('petir')
        aktif_emoji = vz_emoji.getemoji('aktif')
        adder1_emoji = vz_emoji.getemoji('adder1')
        proses_emoji = vz_emoji.getemoji('proses')
        telegram_emoji = vz_emoji.getemoji('telegram')

        success_emojis = f"{centang_emoji} {utama_emoji} {petir_emoji} {aktif_emoji} {adder1_emoji}"

        completion_msg = f"""{success_emojis} **TAGALL COMPLETED**

{centang_emoji} Total Tagged: {processed_count} users
{utama_emoji} Batches Processed: {(processed_count + batch_size - 1) // batch_size}
{aktif_emoji} Message: {message_text or 'Default tagall'}
{petir_emoji} Group: {chat_title}
{adder1_emoji} Method: Smart Batch Editing

{proses_emoji} Status: Successfully Completed
{telegram_emoji} System: VZ ASSISTANT Premium Tagall

By Vzoel Fox's Assistant"""

        await vz_client.edit_with_premium_emoji(status_msg, completion_msg)

        # Clean up tracking data
        if chat_id in tagall_progress:
            del tagall_progress[chat_id]
        if chat_id in tagall_messages:
            del tagall_messages[chat_id]

@events.register(events.NewMessage(pattern=r'^\.stag$', outgoing=True))
async def stop_tagall_handler(event):
    """
    .stag - Stop ongoing tagall process

    Stops both .tag and .tagall operations
    """
    global vz_client, vz_emoji, tagall_tasks, tagall_active, tagall_progress, tagall_messages, active_tags

    chat_id = event.chat_id

    # Check .tagall first
    if chat_id in tagall_tasks and not tagall_tasks[chat_id].done():
        # Cancel the tagall task
        tagall_tasks[chat_id].cancel()
        tagall_active[chat_id] = False

        # Clean up tracking data
        if chat_id in tagall_progress:
            del tagall_progress[chat_id]
        if chat_id in tagall_messages:
            del tagall_messages[chat_id]

        centang_emoji = vz_emoji.getemoji('centang')
        kuning_emoji = vz_emoji.getemoji('kuning')
        telegram_emoji = vz_emoji.getemoji('telegram')

        await vz_client.edit_with_premium_emoji(
            event,
            f"{centang_emoji} Smart Batch Tagall Stopped\n\n{kuning_emoji} Cleanup completed\n{telegram_emoji} VZ ASSISTANT Tagall"
        )
        return

    # Check .tag (original implementation)
    if chat_id in active_tags:
        # Remove from active tags
        del active_tags[chat_id]

        gear_emoji = vz_emoji.getemoji('gear')
        petir_emoji = vz_emoji.getemoji('petir')
        main_emoji = vz_emoji.getemoji('utama')

        await vz_client.edit_with_premium_emoji(event, f"""
⏹ **Tag All Stopped**

Operation cancelled successfully.

{gear_emoji} Plugins Digunakan: **GROUP**
{petir_emoji} by {main_emoji} Vzoel Fox's Lutpan""")
        return

    # No active tag operation
    kuning_emoji = vz_emoji.getemoji('kuning')
    await vz_client.edit_with_premium_emoji(
        event,
        f"{kuning_emoji} Tidak ada proses tag/tagall yang sedang berjalan"
    )

print("✅ Plugin loaded: group.py")
