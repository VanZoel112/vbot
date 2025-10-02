"""
VZ ASSISTANT v0.0.0.69
Info Plugin - User Info & File ID

2025© Vzoel Fox's Lutpan
Founder & DEVELOPER : @VZLfxs
"""

from telethon import events
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument
import config

# ============================================================================
# ID COMMAND
# ============================================================================

@events.register(events.NewMessage(pattern=r'^\.id(@\w+)?$', outgoing=True))
async def id_handler(event):
    """
    .id - Get user information

    Usage:
        .id @username          (get info by username)
        .id (reply)            (get info from reply)
        .id                    (get current chat info)

    Shows: ID, name, username, group count
    """
    # Get target
    reply = await event.get_reply_message()
    username = event.pattern_match.group(1)

    if reply:
        target = await reply.get_sender()
        is_user = True
    elif username:
        try:
            username = username[1:]  # Remove @
            target = await event.client.get_entity(username)
            is_user = True
        except Exception as e:
            await event.edit(f"❌ Failed to get user: {str(e)}")
            return
    else:
        # Get current chat info
        target = await event.get_chat()
        is_user = False

    await event.edit("🔍 Fetching information...")

    # Build info text
    if is_user:
        # User info
        try:
            # Get common groups count
            try:
                common = await event.client.get_common_chats(target)
                group_count = len(common)
            except:
                group_count = "Unknown"

            info_text = f"""
👤 **USER INFORMATION**

**📋 Basic Info:**
├ **Name:** {target.first_name} {target.last_name if target.last_name else ''}
├ **Username:** @{target.username if target.username else 'None'}
├ **User ID:** `{target.id}`
├ **Bot:** {'✅ Yes' if target.bot else '❌ No'}
└ **Premium:** {'✅ Yes' if hasattr(target, 'premium') and target.premium else '❌ No'}

**📊 Statistics:**
├ **Common Groups:** {group_count}
└ **Profile Photo:** {'✅ Yes' if target.photo else '❌ No'}

**🔗 Permanent Link:**
[Click here](tg://user?id={target.id})

{config.BRANDING_FOOTER} INFO
Founder & DEVELOPER : {config.FOUNDER_USERNAME}
"""
        except Exception as e:
            await event.edit(f"❌ Error getting user info: {str(e)}")
            return
    else:
        # Chat/Group info
        info_text = f"""
💬 **CHAT INFORMATION**

**📋 Basic Info:**
├ **Title:** {target.title if hasattr(target, 'title') else 'Private Chat'}
├ **Chat ID:** `{target.id}`
├ **Type:** {target.__class__.__name__}
├ **Username:** @{target.username if hasattr(target, 'username') and target.username else 'None'}

**📊 Statistics:**
├ **Members:** {target.participants_count if hasattr(target, 'participants_count') else 'Unknown'}
└ **Photo:** {'✅ Yes' if target.photo else '❌ No'}

{config.BRANDING_FOOTER} INFO
Founder & DEVELOPER : {config.FOUNDER_USERNAME}
"""

    await event.edit(info_text)

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
    # Check if replying to media
    reply = await event.get_reply_message()

    if not reply:
        await event.edit("❌ Reply to a media message to get file ID!")
        return

    if not reply.media:
        await event.edit("❌ Replied message doesn't contain media!")
        return

    await event.edit("🔍 Extracting file ID...")

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
        await event.edit(f"❌ Failed to extract file ID: {str(e)}")
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
    result_text = f"""
📄 **FILE INFORMATION**

**📋 Details:**
├ **Type:** {media_type}
├ **File ID:** `{file_id}`
├ **File Size:** {size_str}
{'├ **MIME Type:** ' + mime_type if mime_type else ''}
{'└ **File Name:** ' + file_name if file_name else ''}

**💡 Usage:**
Use this file_id to send or manipulate this file.

{config.BRANDING_FOOTER} INFO
Founder & DEVELOPER : {config.FOUNDER_USERNAME}
"""

    await event.edit(result_text)

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
    await event.edit("🔍 Checking spam limit...")

    try:
        # Send /start to @SpamBot
        async with event.client.conversation('@SpamBot') as conv:
            # Send /start
            await conv.send_message('/start')

            # Wait for response
            response = await conv.get_response()

            # Get response text
            if response.text:
                limit_text = f"""
📊 **SPAM LIMIT CHECK**

**🤖 @SpamBot Response:**

{response.text}

**ℹ️ Info:**
This shows your current Telegram limits status.

{config.BRANDING_FOOTER} LIMIT
Founder & DEVELOPER : {config.FOUNDER_USERNAME}
"""
            else:
                limit_text = "❌ No response from @SpamBot"

            await event.edit(limit_text)

    except Exception as e:
        await event.edit(f"❌ Failed to check limit: {str(e)}\n\nTry messaging @SpamBot manually.")

print("✅ Plugin loaded: info.py")
