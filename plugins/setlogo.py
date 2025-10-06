"""
VZ ASSISTANT v0.0.0.69
Set Logo Plugin - Custom Logo for Help/Alive

2025© Vzoel Fox's Lutpan
Founder & DEVELOPER : @VZLfxs
"""

from telethon import events
from telethon.tl.types import MessageMediaPhoto
import os
import config
from utils.animation import animate_loading

# Global variables (set by main.py)
vz_client = None
vz_emoji = None

# Logo configuration
LOGO_DIR = os.path.join(config.BASE_DIR, "assets", "logos")
DEFAULT_LOGO_URL = "https://raw.githubusercontent.com/VanZoel112/vzoelupgrade/main/assets/branding/vbot_branding.png"
LOGO_FILE_PATH = os.path.join(LOGO_DIR, "custom_logo.jpg")

# Ensure logo directory exists
os.makedirs(LOGO_DIR, exist_ok=True)

# ============================================================================
# SETLOGO COMMAND
# ============================================================================

@events.register(events.NewMessage(pattern=r'^\.setlogo$', outgoing=True))
async def setlogo_handler(event):
    """
    .setlogo - Set custom logo for help/alive

    Usage:
        .setlogo (reply to image)

    Sets a custom logo image to be shown in .help and .alive commands.
    """
    global vz_client, vz_emoji

    # Run animation
    msg = await animate_loading(vz_client, vz_emoji, event)

    # Check if replying to media
    reply = await event.get_reply_message()

    if not reply:
        error_emoji = vz_emoji.getemoji('merah')
        petir_emoji = vz_emoji.getemoji('petir')
        gear_emoji = vz_emoji.getemoji('gear')
        main_emoji = vz_emoji.getemoji('utama')

        await vz_client.edit_with_premium_emoji(msg, f"""
{error_emoji} **No Image Replied**

**Usage:**
Reply to an image with `.setlogo`

**Example:**
1. Send/forward an image
2. Reply with `.setlogo`
3. Logo will be set for .help and .alive

{petir_emoji} {gear_emoji} Plugins Digunakan: **SETLOGO**
{petir_emoji} by {main_emoji} Vzoel Fox's Lutpan""")
        return

    if not reply.media or not isinstance(reply.media, MessageMediaPhoto):
        error_emoji = vz_emoji.getemoji('merah')
        await vz_client.edit_with_premium_emoji(msg, f"{error_emoji} **Please reply to an image!**")
        return

    # Download the image
    try:
        loading_emoji = vz_emoji.getemoji('loading')
        await vz_client.edit_with_premium_emoji(msg, f"{loading_emoji} **Downloading logo...**")

        # Download to logo directory
        downloaded_path = await reply.download_media(file=LOGO_FILE_PATH)

        # Save file_id to database for quick access
        user_id = event.sender_id
        db_path = config.get_sudoer_db_path(user_id) if not config.is_developer(user_id) else config.DEVELOPER_DB_PATH

        from database.models import DatabaseManager
        db = DatabaseManager(db_path)

        # Store logo path in settings
        db.execute("""
            CREATE TABLE IF NOT EXISTS logo_settings (
                user_id INTEGER PRIMARY KEY,
                logo_path TEXT,
                file_id TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Get file_id for faster sending
        file_id = None
        if hasattr(reply.media.photo, 'id'):
            file_id = str(reply.media.photo.id)

        db.execute("""
            INSERT OR REPLACE INTO logo_settings (user_id, logo_path, file_id)
            VALUES (?, ?, ?)
        """, (user_id, LOGO_FILE_PATH, file_id))

        db.session.commit()
        db.close()

        success_emoji = vz_emoji.getemoji('centang')
        petir_emoji = vz_emoji.getemoji('petir')
        camera_emoji = vz_emoji.getemoji('camera')
        gear_emoji = vz_emoji.getemoji('gear')
        main_emoji = vz_emoji.getemoji('utama')

        result_text = f"""
{success_emoji} **Logo Updated Successfully!**

{camera_emoji} **Logo Path:** `{LOGO_FILE_PATH}`

**💡 Usage:**
Logo will now be shown in:
• `.help` command
• `.alive` command
• Inline help menu

**🔄 Reset to Default:**
Use `.resetlogo` to restore default logo

{petir_emoji} {gear_emoji} Plugins Digunakan: **SETLOGO**
{petir_emoji} by {main_emoji} {config.RESULT_FOOTER}
"""

        await vz_client.edit_with_premium_emoji(msg, result_text)

    except Exception as e:
        error_emoji = vz_emoji.getemoji('merah')
        await vz_client.edit_with_premium_emoji(msg, f"{error_emoji} **Failed to set logo:** {str(e)}")

# ============================================================================
# RESETLOGO COMMAND
# ============================================================================

@events.register(events.NewMessage(pattern=r'^\.resetlogo$', outgoing=True))
async def resetlogo_handler(event):
    """
    .resetlogo - Reset logo to default

    Resets the logo to the default VBot branding image.
    """
    global vz_client, vz_emoji

    # Run animation
    msg = await animate_loading(vz_client, vz_emoji, event)

    user_id = event.sender_id
    db_path = config.get_sudoer_db_path(user_id) if not config.is_developer(user_id) else config.DEVELOPER_DB_PATH

    from database.models import DatabaseManager
    db = DatabaseManager(db_path)

    # Remove custom logo
    db.execute("DELETE FROM logo_settings WHERE user_id = ?", (user_id,))
    db.session.commit()
    db.close()

    # Remove file if exists
    if os.path.exists(LOGO_FILE_PATH):
        os.remove(LOGO_FILE_PATH)

    success_emoji = vz_emoji.getemoji('centang')
    petir_emoji = vz_emoji.getemoji('petir')
    gear_emoji = vz_emoji.getemoji('gear')
    main_emoji = vz_emoji.getemoji('utama')

    result_text = f"""
{success_emoji} **Logo Reset to Default**

Default VBot branding will be used in:
• `.help` command
• `.alive` command
• Inline help menu

{petir_emoji} {gear_emoji} Plugins Digunakan: **SETLOGO**
{petir_emoji} by {main_emoji} {config.RESULT_FOOTER}
"""

    await vz_client.edit_with_premium_emoji(msg, result_text)

# ============================================================================
# GETLOGO COMMAND
# ============================================================================

@events.register(events.NewMessage(pattern=r'^\.getlogo$', outgoing=True))
async def getlogo_handler(event):
    """
    .getlogo - Get current logo

    Shows the current logo being used.
    """
    global vz_client, vz_emoji

    user_id = event.sender_id
    db_path = config.get_sudoer_db_path(user_id) if not config.is_developer(user_id) else config.DEVELOPER_DB_PATH

    from database.models import DatabaseManager
    db = DatabaseManager(db_path)

    # Check if custom logo exists
    result = db.execute("SELECT logo_path, file_id FROM logo_settings WHERE user_id = ?", (user_id,)).fetchone()
    db.close()

    camera_emoji = vz_emoji.getemoji('camera')
    petir_emoji = vz_emoji.getemoji('petir')
    gear_emoji = vz_emoji.getemoji('gear')
    main_emoji = vz_emoji.getemoji('utama')

    if result and result[0] and os.path.exists(result[0]):
        # Send custom logo
        await event.delete()
        await vz_client.client.send_file(
            event.chat_id,
            result[0],
            caption=f"""
{camera_emoji} **Current Custom Logo**

**Status:** Custom logo active
**Path:** `{result[0]}`

{petir_emoji} {gear_emoji} Plugins Digunakan: **SETLOGO**
{petir_emoji} by {main_emoji} {config.RESULT_FOOTER}
"""
        )
    else:
        # Show default logo info
        await vz_client.edit_with_premium_emoji(event, f"""
{camera_emoji} **Current Logo: Default**

**Status:** Using default VBot branding
**Source:** {DEFAULT_LOGO_URL}

**💡 Set Custom Logo:**
Reply to an image with `.setlogo`

{petir_emoji} {gear_emoji} Plugins Digunakan: **SETLOGO**
{petir_emoji} by {main_emoji} {config.RESULT_FOOTER}
""")

# ============================================================================
# HELPER FUNCTION
# ============================================================================

def get_user_logo(user_id: int):
    """Get user's custom logo path or None for default."""
    db_path = config.get_sudoer_db_path(user_id) if not config.is_developer(user_id) else config.DEVELOPER_DB_PATH

    from database.models import DatabaseManager
    db = DatabaseManager(db_path)

    try:
        result = db.execute("SELECT logo_path FROM logo_settings WHERE user_id = ?", (user_id,)).fetchone()
        db.close()

        if result and result[0] and os.path.exists(result[0]):
            return result[0]
        return None
    except:
        db.close()
        return None

print("✅ Plugin loaded: setlogo.py")
