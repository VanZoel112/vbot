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

    # Get premium emojis
    gear_emoji = vz_emoji.getemoji('gear')
    petir_emoji = vz_emoji.getemoji('petir')
    main_emoji = vz_emoji.getemoji('utama')

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
        kuning_emoji = vz_emoji.getemoji('kuning')
        await vz_client.edit_with_premium_emoji(event, f"{kuning_emoji} Group `{chat_id}` is already blacklisted!")
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

    centang_emoji = vz_emoji.getemoji('centang')
    telegram_emoji = vz_emoji.getemoji('telegram')
    aktif_emoji = vz_emoji.getemoji('aktif')
    proses_emoji = vz_emoji.getemoji('proses')

    result_text = f"""
{centang_emoji} **Blacklist Added**

**{telegram_emoji} Group:** {chat_name}
**{aktif_emoji} ID:** `{chat_id}`
**{proses_emoji} Total Blacklisted:** {len(blacklist)}

{gear_emoji} This group will be skipped during .gcast

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

    # Get premium emojis
    gear_emoji = vz_emoji.getemoji('gear')
    petir_emoji = vz_emoji.getemoji('petir')
    main_emoji = vz_emoji.getemoji('utama')

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
        kuning_emoji = vz_emoji.getemoji('kuning')
        await vz_client.edit_with_premium_emoji(event, f"{kuning_emoji} Group `{chat_id}` is not blacklisted!")
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

    centang_emoji = vz_emoji.getemoji('centang')
    telegram_emoji = vz_emoji.getemoji('telegram')
    aktif_emoji = vz_emoji.getemoji('aktif')
    proses_emoji = vz_emoji.getemoji('proses')

    result_text = f"""
{centang_emoji} **Blacklist Removed**

**{telegram_emoji} Group:** {chat_name}
**{aktif_emoji} ID:** `{chat_id}`
**{proses_emoji} Total Blacklisted:** {len(blacklist)}

{gear_emoji} This group will now receive .gcast broadcasts

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

    # Get premium emojis
    gear_emoji = vz_emoji.getemoji('gear')
    petir_emoji = vz_emoji.getemoji('petir')
    main_emoji = vz_emoji.getemoji('utama')
    loading_emoji = vz_emoji.getemoji('loading')
    proses_emoji = vz_emoji.getemoji('proses')
    aktif_emoji = vz_emoji.getemoji('nyala')
    centang_emoji = vz_emoji.getemoji('centang')
    merah_emoji = vz_emoji.getemoji('merah')
    kuning_emoji = vz_emoji.getemoji('kuning')
    biru_emoji = vz_emoji.getemoji('biru')
    telegram_emoji = vz_emoji.getemoji('telegram')
    adder1_emoji = vz_emoji.getemoji('adder1')
    adder2_emoji = vz_emoji.getemoji('adder2')

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
        await vz_client.edit_with_premium_emoji(event, f"{merah_emoji} Usage: `.gcast <message>` or `.gcast` (reply to message)")
        return

    # Load blacklist
    blacklist = load_blacklist(user_id)

    # Animation phase 1: Process setup (vzl2 style)
    setup_frames = [
        f"{loading_emoji} Memulai persiapan...",
        f"{proses_emoji} Memuat sistem broadcast...",
        f"{aktif_emoji} Menghitung target chat...",
        f"{petir_emoji} Menyiapkan pesan..."
    ]

    msg = event
    for frame in setup_frames:
        msg = await vz_client.edit_with_premium_emoji(msg, frame)
        await asyncio.sleep(0.8)

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
        await vz_client.edit_with_premium_emoji(msg, f"{kuning_emoji} No groups/channels available for broadcast")
        return

    # Animation phase 2: Starting broadcast (vzl2 style)
    signature = f"{main_emoji}{adder1_emoji}{petir_emoji}"

    startup_frames = [
        f"{signature} MEMULAI BROADCAST\n\n{centang_emoji} Target Chat: `{total_groups}`\n{merah_emoji} Blacklist: `{len(blacklist)}`\n{loading_emoji} Menyiapkan engine...",
        f"{signature} VZOEL BROADCAST ENGINE\n\n{aktif_emoji} Target Chat: `{total_groups}`\n{kuning_emoji} Blacklist: `{len(blacklist)}`\n{proses_emoji} Mengaktifkan sistem...",
        f"{signature} BROADCAST DIMULAI!\n\n{petir_emoji} Target Chat: `{total_groups}`\n{biru_emoji} Blacklist: `{len(blacklist)}`\n{telegram_emoji} Status: ACTIVE"
    ]

    for frame in startup_frames:
        msg = await vz_client.edit_with_premium_emoji(msg, frame)
        await asyncio.sleep(1.2)

    # Start broadcasting with progress tracking
    success = 0
    failed = 0
    start_time = asyncio.get_event_loop().time()

    for i, dialog in enumerate(groups, 1):
        try:
            # Update progress with animated bar (vzl2 style)
            if i % 3 == 0 or i == total_groups:
                progress_percentage = int((i / total_groups) * 100)
                progress_bar = "█" * (progress_percentage // 10) + "░" * (10 - (progress_percentage // 10))

                # Dynamic emoji based on progress
                if progress_percentage < 30:
                    status_emoji = loading_emoji
                    status_text = "MEMULAI"
                elif progress_percentage < 70:
                    status_emoji = proses_emoji
                    status_text = "PROSES"
                else:
                    status_emoji = aktif_emoji
                    status_text = "HAMPIR SELESAI"

                progress_msg = f"""{signature} VZOEL BROADCAST {status_text}

{status_emoji} Progress: [{progress_bar}] {progress_percentage}%
{centang_emoji} Berhasil: `{success}`
{merah_emoji} Gagal: `{failed}`
{telegram_emoji} Sedang: `{dialog.name[:25] if hasattr(dialog, 'name') else 'Unknown'}...`
{petir_emoji} Status: `{i}/{total_groups}` chat"""
                msg = await vz_client.edit_with_premium_emoji(msg, progress_msg)

            # Send message
            if is_reply:
                await event.client.send_message(
                    dialog.entity,
                    message_to_broadcast
                )
            else:
                await event.client.send_message(
                    dialog.entity,
                    message_to_broadcast
                )

            success += 1
            await asyncio.sleep(config.GCAST_DELAY)

        except Exception as e:
            failed += 1
            print(f"Failed to broadcast to {dialog.name if hasattr(dialog, 'name') else 'Unknown'}: {e}")

    # Calculate final stats
    end_time = asyncio.get_event_loop().time()
    duration = end_time - start_time
    success_rate = (success / total_groups * 100) if total_groups > 0 else 0

    # Animation phase 3: Process completed (vzl2 style)
    completion_frames = [
        f"{signature} MENYELESAIKAN BROADCAST...\n\n{loading_emoji} Menghitung hasil akhir...",
        f"{signature} MENGANALISA HASIL...\n\n{proses_emoji} Processing statistics...",
        f"{signature} BROADCAST SELESAI!\n\n{centang_emoji} Analisa hasil berhasil!"
    ]

    for frame in completion_frames:
        msg = await vz_client.edit_with_premium_emoji(msg, frame)
        await asyncio.sleep(1)

    # Final result (vzl2 style formatting)
    final_progress_bar = "█" * 10  # Full bar
    success_emoji_final = centang_emoji if success_rate >= 70 else kuning_emoji if success_rate >= 40 else merah_emoji

    complete_msg = f"""{signature} VZOEL BROADCAST COMPLETED!

{success_emoji_final} HASIL BROADCAST:
├ Progress: [{final_progress_bar}] 100%
├ Berhasil: `{success}` chat
├ Gagal: `{failed}` chat
├ Total Target: `{total_groups}` chat
└ Success Rate: `{success_rate:.1f}%`

{aktif_emoji} STATISTIK WAKTU:
├ Durasi: `{duration:.1f}` detik
├ Rata-rata: `{(duration/total_groups):.2f}s` per chat
└ Speed: {petir_emoji} VZOEL ENGINE

{adder2_emoji} Ready for next broadcast!
{telegram_emoji} by Vzoel Fox's Assistant"""

    await vz_client.edit_with_premium_emoji(msg, complete_msg)

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

    # Get premium emojis
    gear_emoji = vz_emoji.getemoji('gear')
    petir_emoji = vz_emoji.getemoji('petir')
    main_emoji = vz_emoji.getemoji('utama')

    # Load blacklist
    blacklist = load_blacklist(user_id)

    if not blacklist:
        telegram_emoji = vz_emoji.getemoji('telegram')
        await vz_client.edit_with_premium_emoji(event, f"{telegram_emoji} Blacklist is empty!")
        return

    # Run 12-phase animation
    msg = await animate_loading(vz_client, vz_emoji, event)

    # Get group names
    merah_emoji = vz_emoji.getemoji('merah')
    bl_text = f"""
{merah_emoji} **Blacklist - {len(blacklist)} Groups**

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
{gear_emoji} Use `.dbl <id>` to remove from blacklist

{gear_emoji} Plugins Digunakan: **BROADCAST**
{petir_emoji} by {main_emoji} Vzoel Fox's Lutpan"""

    await vz_client.edit_with_premium_emoji(event, bl_text)

# ============================================================================
# GCAST INFO COMMAND
# ============================================================================

@events.register(events.NewMessage(pattern=r'^\.ginfo$', outgoing=True))
async def ginfo_handler(event):
    global vz_client, vz_emoji

    """
    .ginfo - Show gcast information and statistics

    Displays available groups/channels and blacklist status
    """
    user_id = event.sender_id

    # Get premium emojis
    loading_emoji = vz_emoji.getemoji('loading')
    proses_emoji = vz_emoji.getemoji('proses')
    aktif_emoji = vz_emoji.getemoji('nyala')
    petir_emoji = vz_emoji.getemoji('petir')
    main_emoji = vz_emoji.getemoji('utama')
    adder1_emoji = vz_emoji.getemoji('adder1')
    adder2_emoji = vz_emoji.getemoji('adder2')
    telegram_emoji = vz_emoji.getemoji('telegram')
    merah_emoji = vz_emoji.getemoji('merah')
    centang_emoji = vz_emoji.getemoji('centang')

    # Animation phase 1: Loading info (vzl2 style)
    loading_frames = [
        f"{loading_emoji} Memuat informasi gcast...",
        f"{proses_emoji} Menghitung chat tersedia...",
        f"{aktif_emoji} Menganalisa blacklist...",
        f"{petir_emoji} Menyiapkan statistik..."
    ]

    msg = event
    for frame in loading_frames:
        msg = await vz_client.edit_with_premium_emoji(msg, frame)
        await asyncio.sleep(0.8)

    # Load blacklist
    blacklist = load_blacklist(user_id)

    # Count available chats
    total_groups = 0
    total_channels = 0

    dialogs = await event.client.get_dialogs()
    for dialog in dialogs:
        entity = dialog.entity
        if isinstance(entity, Chat):
            if entity.id not in blacklist and -entity.id not in blacklist:
                total_groups += 1
        elif isinstance(entity, Channel):
            if entity.id not in blacklist and -entity.id not in blacklist:
                if entity.broadcast:
                    total_channels += 1
                else:
                    total_groups += 1

    total_available = total_groups + total_channels
    blacklisted_count = len(blacklist)

    # Animation phase 2: Show complete info (vzl2 style)
    signature = f"{main_emoji}{adder1_emoji}{petir_emoji}"

    info_text = f"""{signature} VZOEL GCAST INFORMATION

{telegram_emoji} TARGETS TERSEDIA:
├ Groups: `{total_groups}` chat
├ Channels: `{total_channels}` chat
└ Total Available: `{total_available}` chat

{merah_emoji} BLACKLIST STATUS:
├ Blacklisted: `{blacklisted_count}` chat
├ Will Broadcast: `{total_available}` chat
└ Protection: {centang_emoji} ACTIVE

{petir_emoji} COMMAND LIST:
├ .gcast <text> - Broadcast pesan text
├ .gcast (reply) - Broadcast dari reply
├ .bl <id> - Tambah ke blacklist
├ .dbl <id> - Hapus dari blacklist
├ .bllist - Lihat daftar blacklist
└ .ginfo - Info sistem gcast

{aktif_emoji} ENGINE STATUS:
├ System: VZOEL BROADCAST ENGINE
├ Speed: {petir_emoji} OPTIMIZED
├ Safety: {centang_emoji} BLACKLIST PROTECTED
└ Version: 1.0.0 PREMIUM

{adder2_emoji} Powered by Vzoel Fox's Technology"""

    await vz_client.edit_with_premium_emoji(msg, info_text)

print("✅ Plugin loaded: broadcast.py")
