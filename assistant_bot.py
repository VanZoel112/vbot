#!/usr/bin/env python3
"""
VZ ASSISTANT BOT v0.0.0.69
Inline Keyboard Handler for Userbot

2025© Vzoel Fox's Lutpan
Founder & DEVELOPER : @VZLfxs
"""

import asyncio
import os
import sys
import json
from datetime import datetime
from telethon import TelegramClient, events, Button
from telethon.tl.types import User
from dotenv import load_dotenv

# Load environment
load_dotenv()

# ============================================================================
# CONFIGURATION
# ============================================================================

# Bot token from environment or use default
BOT_TOKEN = os.getenv("ASSISTANT_BOT_TOKEN", "8314911312:AAEZTrlru95_QNycAt4TlYH_k-7q2f_PQ9c")

# API credentials (same as userbot)
API_ID = 29919905
API_HASH = "717957f0e3ae20a7db004d08b66bfd30"

# Developer IDs (who can control the bot)
DEVELOPER_IDS = [8024282347, 7553981355]

# Userbot owner ID (who this assistant serves)
OWNER_ID = int(os.getenv("OWNER_ID", "7553981355"))

# Bridge file for userbot-bot communication
BRIDGE_FILE = "data/bot_bridge.json"

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def is_authorized(user_id):
    """Check if user is authorized to use bot."""
    return user_id == OWNER_ID or user_id in DEVELOPER_IDS

def load_bridge_data():
    """Load data from bridge file."""
    if os.path.exists(BRIDGE_FILE):
        try:
            with open(BRIDGE_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_bridge_data(data):
    """Save data to bridge file."""
    os.makedirs(os.path.dirname(BRIDGE_FILE), exist_ok=True)
    with open(BRIDGE_FILE, 'w') as f:
        json.dump(data, f, indent=2)

# ============================================================================
# BOT CLIENT
# ============================================================================

bot = TelegramClient('assistant_bot', API_ID, API_HASH)

# ============================================================================
# START COMMAND
# ============================================================================

@bot.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    """Handle /start command."""
    user = await event.get_sender()
    user_id = event.sender_id

    if not is_authorized(user_id):
        await event.respond(
            "❌ **Access Denied**\n\n"
            f"This bot serves @{bot.me.username}'s owner only.\n\n"
            "🤖 by VzBot"
        )
        return

    welcome_text = f"""
🤩 **VZ ASSISTANT BOT**

Hello {user.first_name}! I'm your personal assistant bot.

**Features:**
• Inline keyboards for userbot commands
• Remote command execution
• Menu navigation

**Available Commands:**
/help - Show help menu
/alive - Bot status
/ping - Check latency

🤖 by VzBot | @VZLfxs
"""

    await event.respond(welcome_text)

# ============================================================================
# HELP COMMAND (WITH INLINE KEYBOARD)
# ============================================================================

@bot.on(events.NewMessage(pattern='/help'))
async def help_handler(event):
    """Show help menu with inline keyboard."""
    user_id = event.sender_id

    if not is_authorized(user_id):
        await event.respond("❌ Access Denied")
        return

    # Build inline keyboard
    buttons = [
        [
            Button.inline("📋 Basic Commands", b"help_cat_Basic"),
            Button.inline("👨‍💼 Admin", b"help_cat_Admin")
        ],
        [
            Button.inline("📡 Broadcast", b"help_cat_Broadcast"),
            Button.inline("👥 Group", b"help_cat_Group")
        ],
        [
            Button.inline("ℹ️ Info", b"help_cat_Info"),
            Button.inline("⚙️ Settings", b"help_cat_Settings")
        ],
        [
            Button.inline("🔧 Plugin Info", b"help_plugins"),
            Button.url("👨‍💻 Developer", "https://t.me/VZLfxs")
        ],
        [Button.inline("❌ Close", b"help_close")]
    ]

    help_text = """
🤩 **VZ ASSISTANT - HELP MENU**

⛈ **Total Commands:** 27
🌟 **Role:** SUDOER
⚙️ **Prefix:** .

**📋 Categories:**
Select a category to view commands

🤖 Powered by VzBot
"""

    await event.respond(help_text, buttons=buttons)

# ============================================================================
# HELP CALLBACK HANDLERS
# ============================================================================

@bot.on(events.CallbackQuery(pattern=b"help_cat_.*"))
async def help_category_callback(event):
    """Handle category selection."""
    await event.answer("Loading category...")

    # Parse category
    category = event.data.decode('utf-8').replace("help_cat_", "")

    # Sample commands (will be loaded from userbot later)
    commands_data = {
        "Basic": {
            "ping": ".ping - Check latency",
            "alive": ".alive - Bot status",
            "help": ".help - This menu"
        },
        "Admin": {
            "admin": ".admin @user - Promote user",
            "unadmin": ".unadmin @user - Demote user"
        },
        "Broadcast": {
            "gcast": ".gcast <msg> - Broadcast message",
            "bl": ".bl - Blacklist chat"
        },
        "Group": {
            "tag": ".tag <msg> - Tag all members",
            "lock": ".lock @user - Lock user messages"
        },
        "Info": {
            "id": ".id - Get user info",
            "getfileid": ".getfileid - Get file ID"
        },
        "Settings": {
            "prefix": ".prefix <new> - Change prefix",
            "pmon": ".pmon - Enable PM permit"
        }
    }

    commands = commands_data.get(category, {})

    if not commands:
        await event.edit("❌ Category not found")
        return

    # Build response
    text = f"⛈ **{category} Commands**\n\n"
    for cmd_name, cmd_desc in commands.items():
        text += f"• `{cmd_desc}`\n"

    text += "\n🤖 Use commands in userbot"

    # Back button
    buttons = [
        [Button.inline("◀️ Back to Menu", b"help_back")],
        [Button.inline("❌ Close", b"help_close")]
    ]

    await event.edit(text, buttons=buttons)

@bot.on(events.CallbackQuery(pattern=b"help_plugins"))
async def help_plugins_callback(event):
    """Show plugin list."""
    await event.answer("Loading plugins...")

    text = """
🤖 **VZ ASSISTANT - PLUGINS**

📦 **Loaded Plugins:** 14

• admin.py - Admin management
• alive.py - Bot status
• broadcast.py - Group broadcast
• group.py - Group utilities
• help.py - Help system
• info.py - Information commands
• ping.py - Latency checker
• settings.py - Bot settings
... and 6 more

🔧 All plugins active
"""

    buttons = [
        [Button.inline("◀️ Back", b"help_back")],
        [Button.inline("❌ Close", b"help_close")]
    ]

    await event.edit(text, buttons=buttons)

@bot.on(events.CallbackQuery(pattern=b"help_back"))
async def help_back_callback(event):
    """Go back to main help menu."""
    await event.answer("Returning to menu...")

    buttons = [
        [
            Button.inline("📋 Basic Commands", b"help_cat_Basic"),
            Button.inline("👨‍💼 Admin", b"help_cat_Admin")
        ],
        [
            Button.inline("📡 Broadcast", b"help_cat_Broadcast"),
            Button.inline("👥 Group", b"help_cat_Group")
        ],
        [
            Button.inline("ℹ️ Info", b"help_cat_Info"),
            Button.inline("⚙️ Settings", b"help_cat_Settings")
        ],
        [
            Button.inline("🔧 Plugin Info", b"help_plugins"),
            Button.url("👨‍💻 Developer", "https://t.me/VZLfxs")
        ],
        [Button.inline("❌ Close", b"help_close")]
    ]

    help_text = """
🤩 **VZ ASSISTANT - HELP MENU**

⛈ **Total Commands:** 27
🌟 **Role:** SUDOER
⚙️ **Prefix:** .

**📋 Categories:**
Select a category to view commands

🤖 Powered by VzBot
"""

    await event.edit(help_text, buttons=buttons)

@bot.on(events.CallbackQuery(pattern=b"help_close"))
async def help_close_callback(event):
    """Close help menu."""
    await event.answer("Closing menu...")
    await event.delete()

# ============================================================================
# ALIVE COMMAND (WITH INLINE KEYBOARD)
# ============================================================================

@bot.on(events.NewMessage(pattern='/alive'))
async def alive_handler(event):
    """Show alive status with inline keyboard."""
    user_id = event.sender_id

    if not is_authorized(user_id):
        await event.respond("❌ Access Denied")
        return

    alive_text = """
🤩 **Vz ASSISTANT** 🎚

👨‍💻 **Founder:** Vzoel Fox's
🌟 **Owner:** @itspizolpoks
⛈ **Versi:** 0.0.0.69
👨‍💻 **Telethon × Python 3+**
♾ **Total Plugin:** 14
🎚 **Waktu Nyala:** Active

🤩 Powered by VzBot
⛈ by 🤩 𝚁𝚎𝚜𝚞𝚕𝚝 𝚋𝚢 𝚅𝚣𝚘𝚎𝚕 𝙵𝚘𝚡'𝚜 𝙰𝚜𝚜𝚒𝚜𝚝𝚊𝚗𝚝
"""

    buttons = [
        [
            Button.inline("✉️ HELP", b"cmd_help"),
            Button.url("👨‍💻 DEV", "https://t.me/VZLfxs")
        ]
    ]

    await event.respond(alive_text, buttons=buttons)

@bot.on(events.CallbackQuery(pattern=b"cmd_help"))
async def alive_help_callback(event):
    """Handle HELP button from alive."""
    await help_handler(event)

# ============================================================================
# PING COMMAND
# ============================================================================

@bot.on(events.NewMessage(pattern='/ping'))
async def ping_handler(event):
    """Show ping/latency."""
    user_id = event.sender_id

    if not is_authorized(user_id):
        await event.respond("❌ Access Denied")
        return

    start = datetime.now()
    msg = await event.respond("🏓 Pinging...")
    end = datetime.now()
    latency = (end - start).total_seconds() * 1000

    await msg.edit(f"🏓 **Pong!**\n⏱ Latency: `{latency:.2f}ms`")

# ============================================================================
# ERROR HANDLER
# ============================================================================

@bot.on(events.Raw)
async def error_handler(event):
    """Handle errors."""
    pass

# ============================================================================
# MAIN
# ============================================================================

async def main():
    """Start the bot."""
    print("="*60)
    print("VZ ASSISTANT BOT v0.0.0.69")
    print("="*60)
    print()

    # Start bot
    await bot.start(bot_token=BOT_TOKEN)

    # Get bot info
    me = await bot.get_me()
    print(f"✅ Bot started: @{me.username}")
    print(f"🆔 Bot ID: {me.id}")
    print(f"👤 Owner: {OWNER_ID}")
    print()
    print("🤖 Bot is now running...")
    print("Press Ctrl+C to stop")
    print("="*60)

    # Keep running
    await bot.run_until_disconnected()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Stopping bot...")
        print("👋 Goodbye!")
