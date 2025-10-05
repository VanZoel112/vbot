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
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
    Message
)
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import plugin loader
from helpers.plugin_loader import load_plugins_info, chunk_list

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

# Pagination settings
PLUGINS_PER_PAGE = 9  # 3x3 grid

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

# Global plugins cache
PLUGINS_CACHE = None

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def is_authorized(user_id: int) -> bool:
    """Check if user is authorized."""
    return user_id == OWNER_ID or user_id in DEVELOPER_IDS

async def log_action(user_id: int, action: str):
    """Log user actions."""
    logger.info(f"User {user_id} | Action: {action}")

def get_plugins():
    """Get plugins list (cached)."""
    global PLUGINS_CACHE
    if PLUGINS_CACHE is None:
        PLUGINS_CACHE = load_plugins_info("plugins")
    return PLUGINS_CACHE

def build_plugins_keyboard(page: int = 0):
    """
    Build inline keyboard for plugins list.

    Args:
        page: Current page number (0-indexed)

    Returns:
        InlineKeyboardMarkup
    """
    plugins = get_plugins()

    # Calculate pagination
    total_plugins = len(plugins)
    total_pages = (total_plugins + PLUGINS_PER_PAGE - 1) // PLUGINS_PER_PAGE
    start_idx = page * PLUGINS_PER_PAGE
    end_idx = min(start_idx + PLUGINS_PER_PAGE, total_plugins)

    # Get plugins for current page
    page_plugins = plugins[start_idx:end_idx]

    # Build keyboard rows (3 plugins per row)
    buttons = []
    for i in range(0, len(page_plugins), 3):
        row = []
        for plugin in page_plugins[i:i+3]:
            emoji = plugin.get("emoji", "🔧")
            name = plugin.get("display_name", plugin["name"])
            row.append(
                InlineKeyboardButton(
                    f"{emoji} {name}",
                    callback_data=f"plugin:{plugin['name']}"
                )
            )
        buttons.append(row)

    # Pagination row
    pagination_row = []
    if page > 0:
        pagination_row.append(
            InlineKeyboardButton("◀️ Sebelumnya", callback_data=f"page:{page-1}")
        )
    if page < total_pages - 1:
        pagination_row.append(
            InlineKeyboardButton("Selanjutnya ▶️", callback_data=f"page:{page+1}")
        )

    if pagination_row:
        buttons.append(pagination_row)

    # VBot button
    buttons.append([
        InlineKeyboardButton("🎵 VBot", url="https://t.me/vmusic_vbot")
    ])

    # Developer button
    buttons.append([
        InlineKeyboardButton("👨‍💻 Developer", url="https://t.me/VZLfxs")
    ])

    return InlineKeyboardMarkup(buttons)

def build_plugin_detail_keyboard():
    """Build keyboard for plugin detail view."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("◀️ Kembali", callback_data="back_to_plugins")]
    ])


def build_help_text(user_id: int, total_plugins: int, page: int = 0, total_pages: int = 1) -> str:
    """Build the help text message for inline and command responses."""
    role = 'DEVELOPER' if user_id in DEVELOPER_IDS else 'SUDOER'
    help_text = (
        "🤩 **VZ ASSISTANT - HELP MENU**\n\n"
        f"⛈ **Total Plugins:** {total_plugins}\n"
        f"🌟 **Role:** {role}\n"
        "⚙️ **Prefix:** .\n\n"
        "**📋 Pilih Plugin:**\n"
        "Click plugin dibawah untuk melihat commands\n\n"
        "🤖 Powered by VzBot"
    )

    if total_pages > 1:
        help_text += f"\n\n📄 **Halaman:** {page + 1}/{total_pages}"

    return help_text

def get_plugin_by_name(name: str):
    """Get plugin info by name."""
    plugins = get_plugins()
    for plugin in plugins:
        if plugin["name"] == name:
            return plugin
    return None

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
• ✨ Inline keyboards for plugin help
• 🚀 Fast response with Pyrogram + Trio
• 🔒 Secure & authorized access

**Available Commands:**
/help - Interactive plugin help menu
/alive - Bot status with buttons
/ping - Check latency

🤖 by VzBot | @VZLfxs
"""

    await message.reply(welcome_text)

# ============================================================================
# HELP COMMAND WITH INLINE PLUGINS
# ============================================================================

@app.on_message(filters.command("help") & filters.private)
async def help_handler(client: Client, message: Message):
    """Show help menu with inline keyboard plugins."""
    user_id = message.from_user.id

    if not is_authorized(user_id):
        await message.reply("❌ Access Denied")
        return

    await log_action(user_id, "help")

    # Get total plugins count
    plugins = get_plugins()
    total_plugins = len(plugins)
    total_pages = max((total_plugins + PLUGINS_PER_PAGE - 1) // PLUGINS_PER_PAGE, 1)

    help_text = build_help_text(user_id, total_plugins, page=0, total_pages=total_pages)
    keyboard = build_plugins_keyboard(page=0)
    await message.reply(help_text, reply_markup=keyboard)

# ============================================================================
# INLINE QUERY HANDLER
# ============================================================================

@app.on_inline_query()
async def inline_help_query(client: Client, inline_query: InlineQuery):
    """Provide inline help result for authorized users."""
    user_id = inline_query.from_user.id

    if not is_authorized(user_id):
        await inline_query.answer([], cache_time=5, is_personal=True)
        return

    query = (inline_query.query or "").strip().lower()
    page = 0

    if query.startswith("page:"):
        try:
            page = max(int(query.split(":", 1)[1]), 0)
        except ValueError:
            page = 0

    plugins = get_plugins()
    total_plugins = len(plugins)
    total_pages = max((total_plugins + PLUGINS_PER_PAGE - 1) // PLUGINS_PER_PAGE, 1)
    page = min(page, total_pages - 1)

    await log_action(user_id, f"inline_help:{query or 'default'}")

    help_text = build_help_text(user_id, total_plugins, page=page, total_pages=total_pages)
    keyboard = build_plugins_keyboard(page=page)

    result = InlineQueryResultArticle(
        title=f"VZ Assistant Help (Halaman {page + 1})",
        description="Buka menu bantuan plugin interaktif",
        input_message_content=InputTextMessageContent(
            help_text,
            parse_mode="markdown",
        ),
        reply_markup=keyboard,
    )

    await inline_query.answer([result], cache_time=0, is_personal=True)

# ============================================================================
# CALLBACK HANDLERS
# ============================================================================

@app.on_callback_query(filters.regex(r"^page:\d+$"))
async def page_callback(client: Client, callback: CallbackQuery):
    """Handle pagination callback."""
    page = int(callback.data.split(":")[1])

    await log_action(callback.from_user.id, f"page:{page}")

    # Get total plugins count
    plugins = get_plugins()
    total_plugins = len(plugins)
    total_pages = max((total_plugins + PLUGINS_PER_PAGE - 1) // PLUGINS_PER_PAGE, 1)

    help_text = build_help_text(callback.from_user.id, total_plugins, page=page, total_pages=total_pages)
    keyboard = build_plugins_keyboard(page=page)
    await callback.edit_message_text(help_text, reply_markup=keyboard)
    await callback.answer()

@app.on_callback_query(filters.regex(r"^plugin:"))
async def plugin_callback(client: Client, callback: CallbackQuery):
    """Handle plugin detail callback."""
    plugin_name = callback.data.split(":", 1)[1]

    await log_action(callback.from_user.id, f"plugin:{plugin_name}")

    # Get plugin info
    plugin = get_plugin_by_name(plugin_name)

    if not plugin:
        await callback.answer("Plugin not found", show_alert=True)
        return

    # Build detail text
    emoji = plugin.get("emoji", "🔧")
    display_name = plugin.get("display_name", plugin["name"])
    description = plugin.get("description", "No description available")
    commands = plugin.get("commands", [])

    detail_text = f"""{emoji} **{display_name}**

📝 **Description:**
{description}

⚡ **Commands:**
"""

    if commands:
        formatted_commands = "\n".join(f"• {cmd}" for cmd in commands)
        detail_text += f"{formatted_commands}\n"
    else:
        detail_text += "No commands documented\n"

    detail_text += f"\n🤖 Use these commands in userbot"

    keyboard = build_plugin_detail_keyboard()
    await callback.edit_message_text(detail_text, reply_markup=keyboard)
    await callback.answer()

@app.on_callback_query(filters.regex(r"^back_to_plugins$"))
async def back_callback(client: Client, callback: CallbackQuery):
    """Handle back to plugins list."""
    await log_action(callback.from_user.id, "back_to_plugins")

    # Return to help menu
    plugins = get_plugins()
    total_plugins = len(plugins)
    total_pages = max((total_plugins + PLUGINS_PER_PAGE - 1) // PLUGINS_PER_PAGE, 1)

    help_text = build_help_text(callback.from_user.id, total_plugins, page=0, total_pages=total_pages)
    keyboard = build_plugins_keyboard(page=0)
    await callback.edit_message_text(help_text, reply_markup=keyboard)
    await callback.answer("Kembali ke menu")

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
👨‍💻 **Pyrogram × Trio**
♾ **Total Plugin:** Auto-loaded
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

    # Show help menu
    plugins = get_plugins()
    total_plugins = len(plugins)
    total_pages = max((total_plugins + PLUGINS_PER_PAGE - 1) // PLUGINS_PER_PAGE, 1)

    help_text = build_help_text(callback.from_user.id, total_plugins, page=0, total_pages=total_pages)
    keyboard = build_plugins_keyboard(page=0)
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

    # Load plugins on startup
    plugins = get_plugins()
    logger.info(f"Loaded {len(plugins)} plugins")
    print(f"✅ Loaded {len(plugins)} plugins")
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
