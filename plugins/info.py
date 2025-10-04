"""
VZ ASSISTANT v0.0.0.69
Info Plugin - User Info & File ID

2025© Vzoel Fox's Lutpan
Founder & DEVELOPER : @VZLfxs
"""

from telethon import events
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument
import config
from utils.animation import animate_loading

# Global variables (set by main.py)
vz_client = None
vz_emoji = None

# ============================================================================
# ID COMMAND
# ============================================================================

@events.register(events.NewMessage(pattern=r'^\.id(?: (.+))?$', outgoing=True))
async def id_handler(event):
    """
    .id - Get user information with animated display

    Usage:
        .id @username          (get info by username)
        .id (reply)            (get info from reply)
        .id                    (get your own info)

    Shows: ID, name, username with 4-phase animation
    """
    global vz_client, vz_emoji

    # Get target
    reply = await event.get_reply_message()
    args = event.pattern_match.group(1)

    target_user = None

    if reply:
        # Get user from reply
        if reply.sender:
            target_user = reply.sender
        else:
            error_emoji = vz_emoji.getemoji('merah')
            await vz_client.edit_with_premium_emoji(event, f"{error_emoji} Cannot get user from reply")
            return
    elif args:
        # Get user from username
        username = args.strip().replace('@', '')
        try:
            target_user = await event.client.get_entity(username)
        except Exception as e:
            error_emoji = vz_emoji.getemoji('merah')
            await vz_client.edit_with_premium_emoji(event, f"{error_emoji} Username @{username} not found")
            return
    else:
        # Get current user (self)
        target_user = await event.client.get_me()

    # Phase 1: Initial loading (vzl2 pattern)
    import asyncio
    utama_emoji = vz_emoji.getemoji('utama')
    initial_msg = f"{utama_emoji} sebentar....."
    message = await vz_client.edit_with_premium_emoji(event, initial_msg)

    # Phase 2: Initialize user
    await asyncio.sleep(1.5)
    edit1 = f"{utama_emoji} menginisialisasi user"
    await vz_client.edit_with_premium_emoji(message, edit1)

    # Phase 3: Finding ID
    await asyncio.sleep(1.5)
    proses_emoji = vz_emoji.getemoji('robot')
    edit2 = f"{proses_emoji} mencari angka user"
    await vz_client.edit_with_premium_emoji(message, edit2)

    # Phase 4: Finding info
    await asyncio.sleep(1.5)
    loading_emoji = vz_emoji.getemoji('loading')
    edit3 = f"{loading_emoji} menemukan informasi"
    await vz_client.edit_with_premium_emoji(message, edit3)

    # Delay before results
    await asyncio.sleep(2)

    # Extract user information (vzl2 pattern)
    user_id = target_user.id
    username = target_user.username or "No Username"
    first_name = target_user.first_name or ""
    last_name = target_user.last_name or ""
    full_name = f"{first_name} {last_name}".strip() or "No Name"

    # Get emojis for gradual reveal
    kuning_emoji = vz_emoji.getemoji('kuning')
    biru_emoji = vz_emoji.getemoji('camera')
    merah_emoji = vz_emoji.getemoji('merah')
    utama_emoji = vz_emoji.getemoji('utama')
    robot_emoji = vz_emoji.getemoji('robot')

    # Phase 5: Show ID (vzl2 pattern - gradual reveal)
    hasil1 = f"ID : {user_id} {kuning_emoji}"
    await vz_client.edit_with_premium_emoji(message, hasil1)

    await asyncio.sleep(1.5)
    # Phase 6: Show ID + Name
    hasil2 = f"""ID : {user_id} {kuning_emoji}
Nama User : {full_name} {biru_emoji}"""
    await vz_client.edit_with_premium_emoji(message, hasil2)

    await asyncio.sleep(1.5)
    # Phase 7: Show ID + Name + Username
    username_display = f"@{username}" if username != "No Username" else "No Username"
    hasil3 = f"""ID : {user_id} {kuning_emoji}
Nama User : {full_name} {biru_emoji}
Username : {robot_emoji} {username_display} {merah_emoji}"""
    await vz_client.edit_with_premium_emoji(message, hasil3)

    await asyncio.sleep(1.5)
    # Phase 8: Final result with signature (vzl2 pattern)
    hasil_final = f"""ID : {user_id} {kuning_emoji}
Nama User : {full_name} {biru_emoji}
Username : {robot_emoji} {username_display} {merah_emoji}
Info by. Vzoel Assistant {utama_emoji}"""
    await vz_client.edit_with_premium_emoji(message, hasil_final)

# ============================================================================
# GETFILEID COMMAND
# ============================================================================

@events.register(events.NewMessage(pattern=r'^\.getfileid$', outgoing=True))
async def getfileid_handler(event):
    """
    .getfileid - Get file ID from media

    Usage:
        .getfileid (reply to media)

    Supported: Photos, Videos, Documents, Stickers, etc.
    Returns file_id for use in other commands.
    """
    global vz_client, vz_emoji

    # Check if replying to media
    reply = await event.get_reply_message()

    if not reply:
        error_emoji = vz_emoji.getemoji('merah')
        await vz_client.edit_with_premium_emoji(event, f"{error_emoji} Reply to a media message to get file ID!")
        return

    if not reply.media:
        error_emoji = vz_emoji.getemoji('merah')
        await vz_client.edit_with_premium_emoji(event, f"{error_emoji} Replied message doesn't contain media!")
        return

    loading_emoji = vz_emoji.getemoji('loading')
    # Run 12-phase animation
    msg = await animate_loading(vz_client, vz_emoji, event)

    # Get media info
    media = reply.media
    media_type = media.__class__.__name__

    file_id = None
    file_size = None
    mime_type = None
    file_name = None

    try:
        if isinstance(media, MessageMediaPhoto):
            # Photo
            file_id = media.photo.id
            file_size = max([size.size for size in media.photo.sizes if hasattr(size, 'size')], default=0)
            media_type = "Photo"

        elif isinstance(media, MessageMediaDocument):
            # Document (video, audio, file, sticker, etc.)
            file_id = media.document.id
            file_size = media.document.size
            mime_type = media.document.mime_type

            # Get file name from attributes
            for attr in media.document.attributes:
                if hasattr(attr, 'file_name'):
                    file_name = attr.file_name
                    break

            # Determine type
            if mime_type:
                if 'video' in mime_type:
                    media_type = "Video"
                elif 'audio' in mime_type:
                    media_type = "Audio"
                elif 'image' in mime_type and 'webp' in mime_type:
                    media_type = "Sticker"
                else:
                    media_type = "Document"
        else:
            media_type = "Other"

    except Exception as e:
        error_emoji = vz_emoji.getemoji('merah')
        await vz_client.edit_with_premium_emoji(event, f"{error_emoji} Failed to extract file ID: {str(e)}")
        return

    # Format file size
    if file_size:
        if file_size < 1024:
            size_str = f"{file_size} B"
        elif file_size < 1024 * 1024:
            size_str = f"{file_size / 1024:.2f} KB"
        elif file_size < 1024 * 1024 * 1024:
            size_str = f"{file_size / (1024 * 1024):.2f} MB"
        else:
            size_str = f"{file_size / (1024 * 1024 * 1024):.2f} GB"
    else:
        size_str = "Unknown"

    # Build result
    camera_emoji = vz_emoji.getemoji('camera')
    success_emoji = vz_emoji.getemoji('centang')
    petir_emoji = vz_emoji.getemoji('petir')
    gear_emoji = vz_emoji.getemoji('gear')
    main_emoji = vz_emoji.getemoji('utama')

    result_text = f"""
{camera_emoji} **FILE INFORMATION**

**📋 Details:**
├ **Type:** {media_type}
├ **File ID:** `{file_id}`
├ **File Size:** {size_str}
{'├ **MIME Type:** ' + mime_type if mime_type else ''}
{'└ **File Name:** ' + file_name if file_name else ''}

**💡 Usage:**
Use this file_id to send or manipulate this file.

{petir_emoji} {robot_emoji} Plugins Digunakan: **INFO**
{petir_emoji} by {main_emoji} Vzoel Fox's Lutpan
"""

    await vz_client.edit_with_premium_emoji(event, result_text)

# ============================================================================
# LIMIT COMMAND
# ============================================================================

@events.register(events.NewMessage(pattern=r'^\.limit$', outgoing=True))
async def limit_handler(event):
    """
    .limit - Check spam limit status

    Connects to @SpamBot to check if account is limited.
    Auto-presses start button and returns response.
    """
    global vz_client, vz_emoji

    loading_emoji = vz_emoji.getemoji('loading')
    # Run 12-phase animation
    msg = await animate_loading(vz_client, vz_emoji, event)

    try:
        # Send /start to @SpamBot
        async with event.client.conversation('@SpamBot') as conv:
            # Send /start
            await conv.send_message('/start')

            # Wait for response
            response = await conv.get_response()

            # Get response text
            if response.text:
                robot_emoji = vz_emoji.getemoji('robot')
                petir_emoji = vz_emoji.getemoji('petir')
                gear_emoji = vz_emoji.getemoji('gear')
                main_emoji = vz_emoji.getemoji('utama')

                limit_text = f"""
{robot_emoji} **SPAM LIMIT CHECK**

**🤖 @SpamBot Response:**

{response.text}

**ℹ️ Info:**
This shows your current Telegram limits status.

{petir_emoji} {robot_emoji} Plugins Digunakan: **INFO**
{petir_emoji} by {main_emoji} Vzoel Fox's Lutpan
"""
            else:
                error_emoji = vz_emoji.getemoji('merah')
                limit_text = f"{error_emoji} No response from @SpamBot"

            await vz_client.edit_with_premium_emoji(event, limit_text)

    except Exception as e:
        error_emoji = vz_emoji.getemoji('merah')
        await vz_client.edit_with_premium_emoji(event, f"{error_emoji} Failed to check limit: {str(e)}\n\nTry messaging @SpamBot manually.")

print("✅ Plugin loaded: info.py")
