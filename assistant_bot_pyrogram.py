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
from pyrogram import Client, filters, enums
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
from helpers.vc_bridge import VCBridge
from helpers.vz_emoji_manager import VZEmojiManager

# Load environment
load_dotenv()

# Initialize VC Bridge
vc_bridge = VCBridge()

# Initialize Emoji Manager
emoji_manager = VZEmojiManager()

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

# Log group
LOG_GROUP_ID = os.getenv("LOG_GROUP_ID")
if LOG_GROUP_ID:
    try:
        LOG_GROUP_ID = int(LOG_GROUP_ID)
    except ValueError:
        LOG_GROUP_ID = None

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
    workdir="sessions"  # Separate session directory to avoid lock conflicts
)

# Global plugins cache
PLUGINS_CACHE = None

# Startup flag for log group join
_log_group_joined = False

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
            # Remove emoji - inline keyboards don't support premium emoji
            name = plugin.get("display_name", plugin["name"])
            row.append(
                InlineKeyboardButton(
                    name,  # No emoji
                    callback_data=f"plugin:{plugin['name']}"
                )
            )
        buttons.append(row)

    # Pagination row (pangkas ukuran)
    pagination_row = []
    if page > 0:
        pagination_row.append(
            InlineKeyboardButton("◀️", callback_data=f"page:{page-1}")
        )
    if page < total_pages - 1:
        pagination_row.append(
            InlineKeyboardButton("▶️", callback_data=f"page:{page+1}")
        )

    if pagination_row:
        buttons.append(pagination_row)

    # VBot & Developer buttons (lebih compact)
    buttons.append([
        InlineKeyboardButton("🤖 VBot", url="https://t.me/vmusic_vbot"),
        InlineKeyboardButton("👨‍💻 Dev", url="https://t.me/VZLfxs")
    ])

    return InlineKeyboardMarkup(buttons)

def build_plugin_detail_keyboard():
    """Build keyboard for plugin detail view."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("◀️ Back", callback_data="back_to_plugins")]
    ])


def build_help_text(user_id: int, total_plugins: int, page: int = 0, total_pages: int = 1) -> str:
    """Build the help text message with premium emoji mapping."""
    # Get emojis
    main_emoji = emoji_manager.getemoji('utama')
    petir_emoji = emoji_manager.getemoji('petir')
    robot_emoji = emoji_manager.getemoji('robot')
    dev_emoji = emoji_manager.getemoji('developer')
    gear_emoji = emoji_manager.getemoji('gear')

    # Determine role
    role = 'DEVELOPER' if user_id in DEVELOPER_IDS else 'SUDOER'

    help_text = (
        f"{main_emoji} **VZ ASSISTANT - HELP MENU**\n\n"
        f"{petir_emoji} **Total Plugins:** {total_plugins}\n"
        f"{robot_emoji if role == 'SUDOER' else dev_emoji} **Role:** {role}\n"
        f"{gear_emoji} **Prefix:** .\n\n"
        "**Pilih Plugin:**\n"
        "Click plugin dibawah untuk melihat commands\n\n"
        f"{robot_emoji} Powered by VzBot"
    )

    if total_pages > 1:
        help_text += f"\n\n**Halaman:** {page + 1}/{total_pages}"

    return help_text

def get_plugin_by_name(name: str):
    """Get plugin info by name."""
    plugins = get_plugins()
    for plugin in plugins:
        if plugin["name"] == name:
            return plugin
    return None

# ============================================================================
# STARTUP - AUTO JOIN LOG GROUP
# ============================================================================

@app.on_message(filters.private & ~filters.bot, group=-1)
async def log_forwarder_and_auto_delete(client: Client, message: Message):
    """
    Forward logs from userbot to log group and auto-delete.

    Flow:
    1. Receive message from userbot (via activity_logger.py)
    2. Forward to LOG_GROUP_ID
    3. Auto-delete message from bot (no trace)
    """
    global _log_group_joined

    # Check if this is from authorized user (userbot owner)
    if not is_authorized(message.from_user.id):
        return

    # Auto-join log group on first message (runs once)
    if not _log_group_joined and LOG_GROUP_ID:
        _log_group_joined = True

        try:
            logger.info(f"📋 First log received, checking log group: {LOG_GROUP_ID}")

            # Get bot info
            bot_me = await client.get_me()

            # Send startup log
            startup_msg = f"""
🤖 **VZ Assistant Bot Online**

**Bot:** @{bot_me.username}
**Owner:** {message.from_user.first_name}
**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

✅ Log forwarding active!
"""
            await client.send_message(LOG_GROUP_ID, startup_msg)
            logger.info("✅ Startup log sent to group")

        except Exception as e:
            logger.warning(f"Log group access: {e}")

    # Forward to log group if configured
    if LOG_GROUP_ID:
        try:
            # Forward message to log group
            await client.forward_messages(
                chat_id=LOG_GROUP_ID,
                from_chat_id=message.chat.id,
                message_ids=message.id
            )

            # Auto-delete message from bot PM (no trace)
            await message.delete()

            logger.debug(f"✅ Log forwarded and deleted")

        except Exception as e:
            logger.error(f"Failed to forward log: {e}")

    # Don't continue to other handlers
    from pyrogram.handlers import StopPropagation
    raise StopPropagation

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

    # Get emojis
    main_emoji = emoji_manager.getemoji('utama')
    robot_emoji = emoji_manager.getemoji('robot')
    petir_emoji = emoji_manager.getemoji('petir')
    gear_emoji = emoji_manager.getemoji('gear')
    dev_emoji = emoji_manager.getemoji('developer')

    welcome_text = f"""
{main_emoji} **VZ ASSISTANT BOT**

Hello {message.from_user.first_name}! I'm your personal assistant bot.

**Features:**
{petir_emoji} Inline keyboards for plugin help
{petir_emoji} Fast response with Pyrogram + Trio
{gear_emoji} Secure & authorized access

**Available Commands:**
{robot_emoji} /help - Interactive plugin help menu
{robot_emoji} /alive - Bot status with buttons
{robot_emoji} /ping - Check latency

{main_emoji} by VzBot | {dev_emoji} @VZLfxs
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
            parse_mode=enums.ParseMode.MARKDOWN,
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

    # Build detail text (no premium emoji in inline messages)
    display_name = plugin.get("display_name", plugin["name"])
    description = plugin.get("description", "No description available")
    commands = plugin.get("commands", [])

    detail_text = f"""**{display_name}**

**Description:**
{description}

**Commands:**
"""

    if commands:
        formatted_commands = "\n".join(f"• {cmd}" for cmd in commands)
        detail_text += f"{formatted_commands}\n"
    else:
        detail_text += "No commands documented\n"

    detail_text += f"\nUse these commands in userbot"

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
# LOG MANAGER COMMANDS
# ============================================================================

@app.on_message(filters.command("log") & filters.private)
async def log_command_handler(client: Client, message: Message):
    """Send log to log group."""
    user_id = message.from_user.id

    if not is_authorized(user_id):
        await message.reply("❌ Access Denied")
        return

    if not LOG_GROUP_ID:
        await message.reply(
            "⚠️ **Log Group tidak dikonfigurasi**\n\n"
            "Set `LOG_GROUP_ID` di `.env` untuk enable logging"
        )
        return

    # Get log message
    log_text = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else None

    if not log_text:
        await message.reply("❌ **Usage:** `/log <message>`")
        return

    await log_action(user_id, f"manual_log")

    # Format log
    log_msg = f"""
📝 **Manual Log**

👤 **From:** {message.from_user.first_name} (@{message.from_user.username or 'no_username'})
🆔 **User ID:** `{user_id}`
📅 **Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

💬 **Message:**
{log_text}

🤖 via VZ Assistant Bot
"""

    try:
        await client.send_message(LOG_GROUP_ID, log_msg)
        await message.reply("✅ **Log sent to group**")
    except Exception as e:
        await message.reply(f"❌ **Failed to send log:** `{str(e)}`")
        logger.error(f"Failed to send log: {e}")

@app.on_message(filters.command("logs") & filters.private)
async def logs_list_handler(client: Client, message: Message):
    """Show recent logs info."""
    user_id = message.from_user.id

    if not is_authorized(user_id):
        await message.reply("❌ Access Denied")
        return

    await log_action(user_id, "logs_info")

    if not LOG_GROUP_ID:
        logs_text = """
📊 **Log Manager**

⚠️ **Status:** Not Configured

Set `LOG_GROUP_ID` di `.env` untuk enable logging

**Commands:**
• `/log <msg>` - Send log manual
• `/logs` - Log manager info

🤖 VZ Assistant Bot
"""
    else:
        logs_text = f"""
📊 **Log Manager**

✅ **Status:** Active
📍 **Log Group:** `{LOG_GROUP_ID}`

**Commands:**
• `/log <msg>` - Send log manual
• `/logs` - Log manager info

🤖 Semua command logs otomatis dikirim ke group
"""

    await message.reply(logs_text)

# ============================================================================
# AUTO LOG HELPER
# ============================================================================

async def send_command_log(client: Client, user_id: int, username: str, first_name: str, command: str):
    """Helper to send command log to log group."""
    if not LOG_GROUP_ID:
        return

    log_msg = f"""
⚡ **Command Log**

👤 **User:** {first_name} (@{username or 'no_username'})
🆔 **ID:** `{user_id}`
💬 **Command:** `{command}`
📅 **Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🤖 via VZ Assistant Bot
"""

    try:
        await client.send_message(LOG_GROUP_ID, log_msg)
    except Exception as e:
        logger.error(f"Failed to send command log: {e}")

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
# VC COMMANDS
# ============================================================================

@app.on_message(filters.command("joinvc") & filters.private)
async def joinvc_handler(client: Client, message: Message):
    """Join voice chat silently."""
    user_id = message.from_user.id

    if not is_authorized(user_id):
        await message.reply("❌ Access Denied")
        return

    await log_action(user_id, "joinvc")

    # Get chat ID from command or reply
    args = message.text.split(maxsplit=1)
    chat_id = None

    if len(args) > 1:
        try:
            chat_id = int(args[1])
        except:
            await message.reply("❌ **Invalid chat ID**\n\nUsage: `/joinvc <chat_id>`")
            return
    else:
        await message.reply("❌ **Chat ID required**\n\nUsage: `/joinvc <chat_id>`")
        return

    status_msg = await message.reply("🎙 **Joining voice chat...**")

    # Send command to userbot via bridge
    command_id = await vc_bridge.send_command(
        chat_id=chat_id,
        command="join",
        params={"silent": True}
    )

    # Wait for result
    result = await vc_bridge.wait_for_result(command_id, timeout=30)

    if result["status"] == "completed":
        await status_msg.edit(
            f"✅ **Joined voice chat!**\n\n"
            f"📍 **Chat:** `{chat_id}`\n"
            f"🎙 **Mode:** Silent (no admin required)\n"
            f"⏱ **Status:** Active"
        )
    elif result["status"] == "error":
        await status_msg.edit(
            f"❌ **Failed to join VC**\n\n"
            f"Error: `{result.get('error', 'Unknown error')}`"
        )
    else:
        await status_msg.edit("⏳ **Request timeout** - Check userbot logs")

@app.on_message(filters.command("play") & filters.private)
async def play_handler(client: Client, message: Message):
    """Play music in voice chat."""
    user_id = message.from_user.id

    if not is_authorized(user_id):
        await message.reply("❌ Access Denied")
        return

    await log_action(user_id, "play")

    # Get song title
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply("❌ **Song title required**\n\nUsage: `/play <song title>`")
        return

    song = args[1]
    status_msg = await message.reply(f"🔍 **Searching:** {song}")

    # Get active VC sessions
    sessions = await vc_bridge.get_active_vc_sessions()

    if not sessions:
        await status_msg.edit(
            "⚠️ **No active VC sessions**\n\n"
            "Join VC first with `/joinvc <chat_id>`"
        )
        return

    # Use first active session
    chat_id = int(list(sessions.keys())[0])

    # Send play command
    command_id = await vc_bridge.send_command(
        chat_id=chat_id,
        command="play",
        params={"song": song}
    )

    # Wait for result
    result = await vc_bridge.wait_for_result(command_id, timeout=45)

    if result["status"] == "completed":
        song_info = result.get("result", {})
        await status_msg.edit(
            f"🎵 **Now Playing**\n\n"
            f"🎼 **Title:** {song_info.get('title', song)}\n"
            f"📍 **Chat:** `{chat_id}`\n"
            f"⏱ **Duration:** {song_info.get('duration', 'Unknown')}"
        )
    elif result["status"] == "error":
        await status_msg.edit(
            f"❌ **Playback failed**\n\n"
            f"Error: `{result.get('error', 'Unknown error')}`"
        )
    else:
        await status_msg.edit("⏳ **Request timeout**")

@app.on_message(filters.command(["leave", "stop"]) & filters.private)
async def leave_handler(client: Client, message: Message):
    """Leave voice chat."""
    user_id = message.from_user.id

    if not is_authorized(user_id):
        await message.reply("❌ Access Denied")
        return

    command = message.text.split()[0].replace("/", "")
    await log_action(user_id, command)

    # Get active sessions
    sessions = await vc_bridge.get_active_vc_sessions()

    if not sessions:
        await message.reply(
            "⚠️ **No active VC sessions**\n\n"
            "Not in any voice chat"
        )
        return

    status_msg = await message.reply("🚪 **Leaving voice chat...**")

    # Leave all active sessions
    results = []
    for chat_id in sessions.keys():
        command_id = await vc_bridge.send_command(
            chat_id=int(chat_id),
            command="leave"
        )
        result = await vc_bridge.wait_for_result(command_id, timeout=15)
        results.append((chat_id, result))

    # Format response
    response = "✅ **Left voice chat**\n\n"
    for chat_id, result in results:
        if result["status"] == "completed":
            response += f"📍 Chat `{chat_id}`: ✓\n"
        else:
            response += f"📍 Chat `{chat_id}`: ✗ ({result.get('error', 'timeout')})\n"

    await status_msg.edit(response)

@app.on_message(filters.command("vcstatus") & filters.private)
async def vcstatus_handler(client: Client, message: Message):
    """Check VC status."""
    user_id = message.from_user.id

    if not is_authorized(user_id):
        await message.reply("❌ Access Denied")
        return

    await log_action(user_id, "vcstatus")

    sessions = await vc_bridge.get_active_vc_sessions()

    if not sessions:
        await message.reply(
            "📊 **VC Status**\n\n"
            "⚠️ No active sessions\n\n"
            "**Commands:**\n"
            "• `/joinvc <chat_id>` - Join VC\n"
            "• `/play <song>` - Play music\n"
            "• `/leave` or `/stop` - Leave VC"
        )
        return

    status_text = "📊 **VC Status**\n\n"
    for chat_id, session in sessions.items():
        status_text += f"📍 **Chat:** `{chat_id}`\n"
        status_text += f"🎙 **Status:** {session.get('status', 'Active')}\n"
        if session.get('current_song'):
            status_text += f"🎵 **Playing:** {session['current_song']}\n"
        status_text += "\n"

    status_text += "**Commands:**\n"
    status_text += "• `/play <song>` - Play music\n"
    status_text += "• `/leave` or `/stop` - Leave VC"

    await message.reply(status_text)

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
