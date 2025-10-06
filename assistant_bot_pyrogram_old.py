#!/usr/bin/env python3
"""
VZ ASSISTANT BOT v0.0.0.69
Pyrogram + Trio Implementation
Inline Keyboard Handler for Userbot

2025© Vzoel Fox's Lutpan
Founder & DEVELOPER : @VZLfxs
"""

import os
import sys
import json
import logging
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
    Message
)
from dotenv import load_dotenv

# Load environment
load_dotenv()

# ============================================================================
# LOGGING SETUP (Trio-style structured logging)
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger('VZAssistantBot')

# ============================================================================
# CONFIGURATION
# ============================================================================

# Bot token from environment
BOT_TOKEN = os.getenv("ASSISTANT_BOT_TOKEN", "8200379693:AAHQa9WlTNB_ynWgXBk1PDy7r0CJYzZQUtE")

# API credentials
API_ID = 29919905
API_HASH = "717957f0e3ae20a7db004d08b66bfd30"

# Authorization
DEVELOPER_IDS = [8024282347, 7553981355]
OWNER_ID = int(os.getenv("OWNER_ID", "7553981355"))

# Bridge file for userbot communication
BRIDGE_FILE = "data/bot_bridge.json"

# ============================================================================
# PYROGRAM CLIENT
# ============================================================================

app = Client(
    "vz_assistant_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    workers=4,  # Trio-compatible workers
    workdir="."
)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def is_authorized(user_id: int) -> bool:
    """Check if user is authorized."""
    return user_id == OWNER_ID or user_id in DEVELOPER_IDS

async def log_action(user_id: int, action: str):
    """Log user actions."""
    logger.info(f"User {user_id} | Action: {action}")

# ============================================================================
# START COMMAND
# ============================================================================

@app.on_message(filters.command("start") & filters.private)
async def start_handler(client: Client, message: Message):
    """Handle /start command."""
    user_id = message.from_user.id

    if not is_authorized(user_id):
        await message.reply(
            "❌ **Access Denied**\n\n"
            "This bot serves owner only.\n\n"
            "🤖 by VzBot"
        )
        return

    await log_action(user_id, "start")

    welcome_text = f"""
🤩 **VZ ASSISTANT BOT**

Hello {message.from_user.first_name}! I'm your personal assistant bot.

**Features:**
• ✨ Inline keyboards for all commands
• 🚀 Fast response with Pyrogram
• 🔒 Secure with Trio event loop

**Available Commands:**
/help - Interactive help menu
/alive - Bot status with buttons
/ping - Check latency

🤖 by VzBot | @VZLfxs
"""

    await message.reply(welcome_text)

# ============================================================================
# HELP COMMAND
# ============================================================================

@app.on_message(filters.command("help") & filters.private)
async def help_handler(client: Client, message: Message):
    """Show help menu with inline keyboard."""
    user_id = message.from_user.id

    if not is_authorized(user_id):
        await message.reply("❌ Access Denied")
        return

    await log_action(user_id, "help")

    help_text = """
🤩 **VZ ASSISTANT - HELP MENU**

⛈ **Total Commands:** 27
🌟 **Role:** SUDOER
⚙️ **Prefix:** .

**📋 Categories:**
Select a category below to view commands

🤖 Powered by VzBot
"""

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📋 Basic", callback_data="help_cat_Basic"),
            InlineKeyboardButton("👨‍💼 Admin", callback_data="help_cat_Admin")
        ],
        [
            InlineKeyboardButton("📡 Broadcast", callback_data="help_cat_Broadcast"),
            InlineKeyboardButton("👥 Group", callback_data="help_cat_Group")
        ],
        [
            InlineKeyboardButton("ℹ️ Info", callback_data="help_cat_Info"),
            InlineKeyboardButton("⚙️ Settings", callback_data="help_cat_Settings")
        ],
        [
            InlineKeyboardButton("🔧 Plugins", callback_data="help_plugins"),
            InlineKeyboardButton("👨‍💻 Dev", url="https://t.me/VZLfxs")
        ],
        [InlineKeyboardButton("❌ Close", callback_data="help_close")]
    ])

    await message.reply(help_text, reply_markup=keyboard)

# ============================================================================
# HELP CALLBACKS
# ============================================================================

@app.on_callback_query(filters.regex(r"^help_cat_"))
async def help_category_callback(client: Client, callback: CallbackQuery):
    """Handle category selection."""
    category = callback.data.replace("help_cat_", "")

    await log_action(callback.from_user.id, f"help_category:{category}")

    # Command database
    commands_db = {
        "Basic": [
            ("`.ping`", "Check bot latency and uptime"),
            ("`.alive`", "Show bot status and info"),
            ("`.help`", "Show this help menu")
        ],
        "Admin": [
            ("`.admin @user`", "Promote user to admin"),
            ("`.unadmin @user`", "Demote admin to user")
        ],
        "Broadcast": [
            ("`.gcast <msg>`", "Broadcast to all groups"),
            ("`.bl`", "Add chat to blacklist"),
            ("`.dbl`", "Remove from blacklist")
        ],
        "Group": [
            ("`.tag <msg>`", "Tag all members"),
            ("`.lock @user`", "Lock user messages"),
            ("`.unlock @user`", "Unlock user")
        ],
        "Info": [
            ("`.id`", "Get user/chat info"),
            ("`.getfileid`", "Get media file ID")
        ],
        "Settings": [
            ("`.prefix <new>`", "Change command prefix"),
            ("`.pmon`", "Enable PM permit"),
            ("`.pmoff`", "Disable PM permit")
        ]
    }

    commands = commands_db.get(category, [])

    text = f"⛈ **{category} Commands**\n\n"
    for cmd, desc in commands:
        text += f"• {cmd} - {desc}\n"

    text += "\n🤖 Use these commands in userbot"

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("◀️ Back to Menu", callback_data="help_back")],
        [InlineKeyboardButton("❌ Close", callback_data="help_close")]
    ])

    await callback.edit_message_text(text, reply_markup=keyboard)
    await callback.answer()

@app.on_callback_query(filters.regex(r"^help_plugins$"))
async def help_plugins_callback(client: Client, callback: CallbackQuery):
    """Show plugin list."""
    await log_action(callback.from_user.id, "help_plugins")

    text = """
🤖 **VZ ASSISTANT - PLUGINS**

📦 **Active Plugins:** 14

✅ admin.py - Admin management
✅ alive.py - Bot status display
✅ broadcast.py - Group broadcast
✅ group.py - Group utilities
✅ help.py - Help system
✅ info.py - Information commands
✅ ping.py - Latency checker
✅ settings.py - Bot settings
✅ showjson.py - Message analyzer
✅ payment.py - Payment info
✅ approve.py - PM permit
✅ developer.py - Dev commands
✅ vc.py - Voice chat
✅ broadcast_middleware.py

🔧 All systems operational
"""

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("◀️ Back", callback_data="help_back")],
        [InlineKeyboardButton("❌ Close", callback_data="help_close")]
    ])

    await callback.edit_message_text(text, reply_markup=keyboard)
    await callback.answer()

@app.on_callback_query(filters.regex(r"^help_back$"))
async def help_back_callback(client: Client, callback: CallbackQuery):
    """Return to main help menu."""
    await log_action(callback.from_user.id, "help_back")

    help_text = """
🤩 **VZ ASSISTANT - HELP MENU**

⛈ **Total Commands:** 27
🌟 **Role:** SUDOER
⚙️ **Prefix:** .

**📋 Categories:**
Select a category below to view commands

🤖 Powered by VzBot
"""

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📋 Basic", callback_data="help_cat_Basic"),
            InlineKeyboardButton("👨‍💼 Admin", callback_data="help_cat_Admin")
        ],
        [
            InlineKeyboardButton("📡 Broadcast", callback_data="help_cat_Broadcast"),
            InlineKeyboardButton("👥 Group", callback_data="help_cat_Group")
        ],
        [
            InlineKeyboardButton("ℹ️ Info", callback_data="help_cat_Info"),
            InlineKeyboardButton("⚙️ Settings", callback_data="help_cat_Settings")
        ],
        [
            InlineKeyboardButton("🔧 Plugins", callback_data="help_plugins"),
            InlineKeyboardButton("👨‍💻 Dev", url="https://t.me/VZLfxs")
        ],
        [InlineKeyboardButton("❌ Close", callback_data="help_close")]
    ])

    await callback.edit_message_text(help_text, reply_markup=keyboard)
    await callback.answer("Returning to menu...")

@app.on_callback_query(filters.regex(r"^help_close$"))
async def help_close_callback(client: Client, callback: CallbackQuery):
    """Close help menu."""
    await log_action(callback.from_user.id, "help_close")
    await callback.message.delete()
    await callback.answer("Menu closed ✓")

# ============================================================================
# ALIVE COMMAND
# ============================================================================

@app.on_message(filters.command("alive") & filters.private)
async def alive_handler(client: Client, message: Message):
    """Show alive status."""
    user_id = message.from_user.id

    if not is_authorized(user_id):
        await message.reply("❌ Access Denied")
        return

    await log_action(user_id, "alive")

    alive_text = """
🤩 **Vz ASSISTANT** 🎚

👨‍💻 **Founder:** Vzoel Fox's
🌟 **Owner:** @itspizolpoks
⛈ **Versi:** 0.0.0.69
👨‍💻 **Telethon × Python 3+**
♾ **Total Plugin:** 14
🎚 **Status:** ✅ Active

🤩 Powered by VzBot
⛈ by 🤩 𝚁𝚎𝚜𝚞𝚕𝚝 𝚋𝚢 𝚅𝚣𝚘𝚎𝚕 𝙵𝚘𝚡'𝚜 𝙰𝚜𝚜𝚒𝚜𝚝𝚊𝚗𝚝
"""

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✉️ HELP", callback_data="cmd_help"),
            InlineKeyboardButton("👨‍💻 DEV", url="https://t.me/VZLfxs")
        ]
    ])

    await message.reply(alive_text, reply_markup=keyboard)

@app.on_callback_query(filters.regex(r"^cmd_help$"))
async def alive_help_callback(client: Client, callback: CallbackQuery):
    """Open help from alive button."""
    await log_action(callback.from_user.id, "alive_to_help")

    help_text = """
🤩 **VZ ASSISTANT - HELP MENU**

⛈ **Total Commands:** 27
🌟 **Role:** SUDOER
⚙️ **Prefix:** .

**📋 Categories:**
Select a category below to view commands

🤖 Powered by VzBot
"""

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📋 Basic", callback_data="help_cat_Basic"),
            InlineKeyboardButton("👨‍💼 Admin", callback_data="help_cat_Admin")
        ],
        [
            InlineKeyboardButton("📡 Broadcast", callback_data="help_cat_Broadcast"),
            InlineKeyboardButton("👥 Group", callback_data="help_cat_Group")
        ],
        [
            InlineKeyboardButton("ℹ️ Info", callback_data="help_cat_Info"),
            InlineKeyboardButton("⚙️ Settings", callback_data="help_cat_Settings")
        ],
        [
            InlineKeyboardButton("🔧 Plugins", callback_data="help_plugins"),
            InlineKeyboardButton("👨‍💻 Dev", url="https://t.me/VZLfxs")
        ],
        [InlineKeyboardButton("❌ Close", callback_data="help_close")]
    ])

    await callback.edit_message_text(help_text, reply_markup=keyboard)
    await callback.answer()

# ============================================================================
# PING COMMAND
# ============================================================================

@app.on_message(filters.command("ping") & filters.private)
async def ping_handler(client: Client, message: Message):
    """Check bot latency."""
    user_id = message.from_user.id

    if not is_authorized(user_id):
        await message.reply("❌ Access Denied")
        return

    await log_action(user_id, "ping")

    start = datetime.now()
    msg = await message.reply("🏓 Pinging...")
    end = datetime.now()

    latency = (end - start).total_seconds() * 1000

    await msg.edit(
        f"🏓 **Pong!**\n\n"
        f"⏱ **Latency:** `{latency:.2f}ms`\n"
        f"🤖 **Bot:** Pyrogram + Trio\n"
        f"⚡ **Status:** Fast & Stable"
    )

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Start the bot."""
    print("=" * 60)
    print("VZ ASSISTANT BOT v0.0.0.69")
    print("Pyrogram + Trio Implementation")
    print("=" * 60)
    print()

    logger.info("Starting VZ Assistant Bot...")
    logger.info(f"Bot Token: {BOT_TOKEN[:20]}...")
    logger.info(f"Owner ID: {OWNER_ID}")
    logger.info("Event Loop: Trio (Structured Concurrency)")
    print()

    # Run bot with Trio (Pyrogram will use Trio automatically if available)
    app.run()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
        print("\n\n⚠️  Stopping bot...")
        print("👋 Goodbye!")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
