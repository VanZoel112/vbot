"""
VZ ASSISTANT v0.0.0.69
Alive Plugin - Bot Status Display

2025© Vzoel Fox's Lutpan
Founder & DEVELOPER : @VZLfxs
"""

from telethon import events, Button
import time
import os
import asyncio
import config
from helpers.inline import get_alive_buttons, KeyboardBuilder
from utils.animation import animate_loading

# Global variables (set by main.py)
vz_client = None
vz_emoji = None

# Global start time
START_TIME = time.time()

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def count_plugins():
    """Count total plugins."""
    plugins_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "plugins")
    count = 0

    if os.path.exists(plugins_dir):
        for filename in os.listdir(plugins_dir):
            if filename.endswith(".py") and not filename.startswith("_"):
                count += 1

    return count

def get_owner_username(event):
    """Get owner username."""
    if event.sender and event.sender.username:
        return event.sender.username
    return "Unknown"

# ============================================================================
# ALIVE COMMAND
# ============================================================================

@events.register(events.NewMessage(pattern=r'^\.alive$', outgoing=True))
async def alive_handler(event):
    """
    .alive - Show bot status and information

    Displays:
    - Founder information
    - Owner username
    - Bot version
    - Tech stack
    - Total plugins
    - Uptime

    With inline buttons:
    - HELP: Open help menu
    - DEV: Contact developer
    """
    global vz_client, vz_emoji

    # Run 12-phase animation
    msg = await animate_loading(vz_client, vz_emoji, event)

    # Get data
    uptime = vz_client.get_uptime() if vz_client else "0s"
    plugin_count = count_plugins()
    owner_username = get_owner_username(event)

    # Get premium emojis - more variety!
    main_emoji = vz_emoji.getemoji('utama')
    nyala_emoji = vz_emoji.getemoji('nyala')
    owner_emoji = vz_emoji.getemoji('owner')
    dev_emoji = vz_emoji.getemoji('developer')
    robot_emoji = vz_emoji.getemoji('robot')
    gear_emoji = vz_emoji.getemoji('gear')
    loading_emoji = vz_emoji.getemoji('loading')
    petir_emoji = vz_emoji.getemoji('petir')

    # Build alive message with varied premium emojis
    alive_text = f"""
{main_emoji} **Vz ASSISTANT** {nyala_emoji}


{dev_emoji} **Founder**         : Vzoel Fox's/t.me/VZLfxs
{owner_emoji} **Owner**            : @{owner_username}
{gear_emoji} **Versi**              : {config.BOT_VERSION}
{dev_emoji} **Telethon × Python 3+**
{loading_emoji} **Total Plugin**  : {plugin_count}
{nyala_emoji} **Waktu Nyala** : {uptime}

{gear_emoji} Plugins Digunakan: **ALIVE**
{petir_emoji} by {main_emoji} Vzoel Fox's Lutpan
"""

    # Create inline buttons with premium emojis
    telegram_emoji = vz_emoji.getemoji('telegram')

    buttons = [
        [
            Button.inline(f"{telegram_emoji} HELP", b"cmd_help"),
            Button.url(f"{dev_emoji} DEV", "https://t.me/VZLfxs")
        ]
    ]

    # Send or edit message with buttons using premium emoji method
    try:
        await vz_client.edit_with_premium_emoji(msg, alive_text, buttons=buttons)
    except Exception as e:
        # If inline buttons not supported, send without buttons
        await vz_client.edit_with_premium_emoji(msg, alive_text)
        print(f"⚠️  Inline buttons not available: {e}")

# ============================================================================
# ALIVE CALLBACK HANDLERS
# ============================================================================

@events.register(events.CallbackQuery(pattern=b"cmd_help"))
async def alive_help_callback(event):
    """Handle HELP button from alive."""
    # Trigger help command
    await event.answer("Opening HELP menu...")

    # Import help handler
    try:
        from .help import show_help_menu
        await show_help_menu(event)
    except ImportError:
        await event.answer("❌ Help plugin not loaded", alert=True)

# ============================================================================
# VZOEL COMMAND (Developer Profile)
# ============================================================================

@events.register(events.NewMessage(pattern=r'^\.vzoel$', outgoing=True))
async def vzoel_handler(event):
    """
    .vzoel - Show developer profile

    12 edit animation with 1.5s interval
    Final output shows developer profile information

    Only for developers!
    """
    global vz_client, vz_emoji

    # Check if user is developer
    user_id = event.sender_id
    if not config.is_developer(user_id):
        return

    # Run 12-phase animation
    msg = await animate_loading(vz_client, vz_emoji, event)

    main_emoji = vz_emoji.getemoji('utama')
    petir_emoji = vz_emoji.getemoji('petir')
    dev_emoji = vz_emoji.getemoji('developer')
    owner_emoji = vz_emoji.getemoji('owner')
    robot_emoji = vz_emoji.getemoji('robot')
    gear_emoji = vz_emoji.getemoji('gear')

    profile_text = f"""
{main_emoji} **VZOEL FOX'S - MAIN DEVELOPER**

{dev_emoji} **Developer Profile**
━━━━━━━━━━━━━━━━━━━━━━

{robot_emoji} **User ID:** {user_id}
{gear_emoji} **Role:** Main Developer
{petir_emoji} **Access Level:** Full Control
{gear_emoji} **Version:** {config.BOT_VERSION}

{owner_emoji} **Specialization:**
• Telegram Userbot Development
• Python × Telethon Expert
• Premium Feature Integration
• Multi-User Architecture

{gear_emoji} **Stats:**
• Total Plugins: {count_plugins()}
• Uptime: {vz_client.get_uptime() if vz_client else "0s"}
• Database: Multi-User SQLite
• Emoji Mapping: 17 Premium

{dev_emoji} **Contact:**
• Telegram: t.me/VZLfxs
• Username: @VZLfxs

{gear_emoji} Plugins Digunakan: **DEVELOPER PROFILE**
{petir_emoji} by {main_emoji} Vzoel Fox's Lutpan
"""

    buttons = [
        [Button.url("📱 Contact", "https://t.me/VZLfxs")]
    ]

    try:
        await vz_client.edit_with_premium_emoji(msg, profile_text, buttons=buttons)
    except:
        await vz_client.edit_with_premium_emoji(msg, profile_text)

print("✅ Plugin loaded: alive.py")
