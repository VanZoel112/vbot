"""
VZ ASSISTANT v0.0.0.69
Alive Plugin - Bot Status Display

2025© Vzoel Fox's Lutpan
Founder & DEVELOPER : @VZLfxs
"""

from telethon import events, Button
import time
import os
import config
from helpers.inline import get_alive_buttons, KeyboardBuilder

# Global start time
START_TIME = time.time()

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_uptime():
    """Get bot uptime."""
    uptime_seconds = int(time.time() - START_TIME)

    days = uptime_seconds // 86400
    hours = (uptime_seconds % 86400) // 3600
    minutes = (uptime_seconds % 3600) // 60
    seconds = uptime_seconds % 60

    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if seconds > 0 or not parts:
        parts.append(f"{seconds}s")

    return " ".join(parts)

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
    # Get data
    uptime = get_uptime()
    plugin_count = count_plugins()
    owner_username = get_owner_username(event)

    # Load emoji mapping for premium emojis
    emoji_map = config.load_emoji_mapping()

    # Build alive message
    alive_text = f"""
   **Vz ASSISTANT**



**Founder**         : Vzoel Fox's/t.me/VZLfxs
**Owner**            : @{owner_username}
**Versi**              : {config.BOT_VERSION}
**Telethon × Python 3+**
**Total Plugin**  : {plugin_count}
**Waktu Nyala** : {uptime}

~Vzoel Fox's Lutpan
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
    # Check if user is developer
    user_id = event.sender_id
    if not config.is_developer(user_id):
        return

    # Animation frames (12 edits)
    frames = [
        "🔄 Loading...",
        "⚡ Initializing...",
        "🔥 Processing...",
        "💫 Gathering data...",
        "🌟 Compiling info...",
        "✨ Almost there...",
        "🚀 Finalizing...",
        "⚙️ Configuring...",
        "🎯 Optimizing...",
        "💎 Polishing...",
        "🎨 Rendering...",
        "✅ Complete!"
    ]

    # Run animation
    msg = await event.edit(frames[0])

    for i, frame in enumerate(frames[1:], 1):
        await asyncio.sleep(1.5)  # 1.5 second delay
        await msg.edit(frame)

    # Final developer profile
    await asyncio.sleep(1.5)

    profile_text = f"""
🤩 **VZOEL FOX'S - MAIN DEVELOPER**

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
• Uptime: {get_uptime()}
• Database: Multi-User SQLite
• Emoji Mapping: 17 Premium

🔗 **Contact:**
• Telegram: t.me/VZLfxs
• Username: @VZLfxs

{config.BRANDING_FOOTER} VZOEL
Founder & DEVELOPER : {config.FOUNDER_USERNAME}
"""

    buttons = [
        [Button.url("📱 Contact", "https://t.me/VZLfxs")]
    ]

    try:
        await msg.edit(profile_text, buttons=buttons)
    except:
        await msg.edit(profile_text)

# Import asyncio for vzoel animation
import asyncio

print("✅ Plugin loaded: alive.py")
