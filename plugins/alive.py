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

    # Get data
    uptime = vz_client.get_uptime() if vz_client else "0s"
    plugin_count = count_plugins()
    owner_username = get_owner_username(event)

    # Get premium emojis
    main_emoji = vz_emoji.getemoji('utama')
    nyala_emoji = vz_emoji.getemoji('nyala')
    checklist_emoji = vz_emoji.getemoji('centang')
    petir_emoji = vz_emoji.getemoji('petir')

    # Build alive message with premium emojis
    alive_text = f"""
{main_emoji} **Vz ASSISTANT** {nyala_emoji}


{checklist_emoji} **Founder**         : Vzoel Fox's/t.me/VZLfxs
{checklist_emoji} **Owner**            : @{owner_username}
{checklist_emoji} **Versi**              : {config.BOT_VERSION}
{checklist_emoji} **Telethon × Python 3+**
{checklist_emoji} **Total Plugin**  : {plugin_count}
{checklist_emoji} **Waktu Nyala** : {uptime}

{petir_emoji} ~Vzoel Fox's Lutpan
"""

    # Create inline buttons
    buttons = [
        [
            Button.inline("📚 HELP", b"cmd_help"),
            Button.url("👨‍💻 DEV", "https://t.me/VZLfxs")
        ]
    ]

    # Send or edit message with buttons
    try:
        await event.edit(alive_text, buttons=buttons)
    except Exception as e:
        # If inline buttons not supported, send without buttons
        await event.edit(alive_text)
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

    # Get premium emojis for animation
    loading_emoji = vz_emoji.getemoji('loading')
    gear_emoji = vz_emoji.getemoji('gear')
    proses1_emoji = vz_emoji.getemoji('proses1')
    proses2_emoji = vz_emoji.getemoji('proses2')
    proses3_emoji = vz_emoji.getemoji('proses3')
    checklist_emoji = vz_emoji.getemoji('centang')

    # Animation frames (12 edits) with premium emojis
    frames = [
        f"{loading_emoji} Loading...",
        f"{petir_emoji} Initializing...",
        f"{proses1_emoji} Processing...",
        f"{proses2_emoji} Gathering data...",
        f"{proses3_emoji} Compiling info...",
        f"{gear_emoji} Almost there...",
        f"{loading_emoji} Finalizing...",
        f"{gear_emoji} Configuring...",
        f"{proses1_emoji} Optimizing...",
        f"{proses2_emoji} Polishing...",
        f"{proses3_emoji} Rendering...",
        f"{checklist_emoji} Complete!"
    ]

    # Run animation
    msg = await event.edit(frames[0])

    for i, frame in enumerate(frames[1:], 1):
        await asyncio.sleep(config.ANIMATION_DELAY)
        await msg.edit(frame)

    # Final developer profile with premium emojis
    await asyncio.sleep(config.ANIMATION_DELAY)

    main_emoji = vz_emoji.getemoji('utama')
    petir_emoji = vz_emoji.getemoji('petir')

    profile_text = f"""
{main_emoji} **VZOEL FOX'S - MAIN DEVELOPER**

👨‍💻 **Developer Profile**
━━━━━━━━━━━━━━━━━━━━━━

🆔 **User ID:** {user_id}
🔑 **Role:** Main Developer
⚡ **Access Level:** Full Control
📦 **Version:** {config.BOT_VERSION}

🌟 **Specialization:**
• Telegram Userbot Development
• Python × Telethon Expert
• Premium Feature Integration
• Multi-User Architecture

📊 **Stats:**
• Total Plugins: {count_plugins()}
• Uptime: {vz_client.get_uptime() if vz_client else "0s"}
• Database: Multi-User SQLite
• Emoji Mapping: 17 Premium

🔗 **Contact:**
• Telegram: t.me/VZLfxs
• Username: @VZLfxs

{petir_emoji} {config.BRANDING_FOOTER} VZOEL
Founder & DEVELOPER : {config.FOUNDER_USERNAME}
"""

    buttons = [
        [Button.url("📱 Contact", "https://t.me/VZLfxs")]
    ]

    try:
        await msg.edit(profile_text, buttons=buttons)
    except:
        await msg.edit(profile_text)

print("✅ Plugin loaded: alive.py")
