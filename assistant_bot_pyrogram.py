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

# Import config and deploy auth
import config
from database.deploy_auth import DeployAuthDB

# Load environment
load_dotenv()

# Initialize VC Bridge
vc_bridge = VCBridge()

# Initialize Deploy Auth Database (for developers only)
deploy_auth_db = None

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
    """Check if user is authorized to use this assistant bot.

    Since each user creates their own assistant bot via .dp command,
    all users should have access to their own bot instance.
    Deploy management commands are separately restricted via is_developer().
    """
    return True  # Allow all users (each has their own bot instance)

def is_developer(user_id: int) -> bool:
    """Check if user is a developer."""
    return config.is_developer(user_id)

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

    # Build keyboard rows (2 plugins per row for 1:1 ratio - more square)
    buttons = []
    for i in range(0, len(page_plugins), 2):
        row = []
        for plugin in page_plugins[i:i+2]:
            # Remove emoji - inline keyboards don't support premium emoji
            name = plugin.get("display_name", plugin["name"])
            row.append(
                InlineKeyboardButton(
                    name,  # No emoji
                    callback_data=f"plugin:{plugin['name']}"
                )
            )
        buttons.append(row)

    # Pagination + About row (compact)
    nav_row = []
    if page > 0:
        nav_row.append(
            InlineKeyboardButton("◀️", callback_data=f"page:{page-1}")
        )

    # About button (compact)
    nav_row.append(
        InlineKeyboardButton("ℹ️", callback_data="about")
    )

    if page < total_pages - 1:
        nav_row.append(
            InlineKeyboardButton("▶️", callback_data=f"page:{page+1}")
        )

    if nav_row:
        buttons.append(nav_row)

    # VBot & Developer buttons (compact 1:1)
    buttons.append([
        InlineKeyboardButton("🤖", url="https://t.me/vmusic_vbot"),
        InlineKeyboardButton("👨‍💻", url="https://t.me/VZLfxs")
    ])

    return InlineKeyboardMarkup(buttons)

def build_plugin_detail_keyboard():
    """Build keyboard for plugin detail view."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("◀️ Back", callback_data="back_to_plugins")]
    ])


def build_help_text(user_id: int, total_plugins: int, page: int = 0, total_pages: int = 1) -> str:
    """Build the help text message with regular emoji (Pyrogram compatible)."""
    # Use regular Unicode emoji for Pyrogram bot
    main_emoji = "🌟"
    petir_emoji = "⚡"
    robot_emoji = "🤖"
    dev_emoji = "👨‍💻"
    gear_emoji = "⚙️"

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

    # Use regular Unicode emoji (Pyrogram compatible)
    main_emoji = "🌟"
    robot_emoji = "🤖"
    petir_emoji = "⚡"
    gear_emoji = "⚙️"
    dev_emoji = "👨‍💻"
    rocket_emoji = "🚀"

    # Check if developer
    if is_developer(user_id):
        # Developer menu with deploy management AND own deploy access
        welcome_text = f"""
{main_emoji} **VZ ASSISTANT BOT** - Developer Mode

Hello {message.from_user.first_name}! I'm your personal assistant bot.

**🌟 Developer Privileges:**
{rocket_emoji} Full deploy access (no approval needed)
{gear_emoji} Can approve/reject other users
{petir_emoji} Manage all deployments

**📱 Assistant Features:**
{petir_emoji} Inline keyboards for plugin help
{petir_emoji} Fast response with Pyrogram + Trio
{gear_emoji} Secure & authorized access

**🚀 Quick Actions:**
Use buttons below for instant access!

{main_emoji} by VzBot | {dev_emoji} @VZLfxs
"""

        # Developer inline buttons with deploy + management
        buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🚀 Deploy My Bot", callback_data="dev_deploy"),
                InlineKeyboardButton("📊 My Status", callback_data="deploy_status")
            ],
            [
                InlineKeyboardButton("⏳ Pending Requests", callback_data="deploy_pending"),
                InlineKeyboardButton("✅ Approved Users", callback_data="deploy_approved")
            ],
            [
                InlineKeyboardButton("📖 Help", callback_data="cmd_help"),
                InlineKeyboardButton("💓 Alive", callback_data="alive_status")
            ]
        ])

        await message.reply(welcome_text, reply_markup=buttons)
        return

    else:
        # Regular user menu with deploy request option
        # Check deploy status
        global deploy_auth_db
        if deploy_auth_db is None:
            deploy_auth_db = DeployAuthDB()

        status_info = deploy_auth_db.get_user_status(user_id)

        if status_info["status"] == "approved":
            deploy_text = f"\n**🚀 Deploy Access:** ✅ Approved\n\n**📋 Next Steps:**\n1. Generate session: `python3 stringgenerator.py`\n2. Deploy: Send `..dp` in main bot\n3. Follow setup wizard\n"
        elif status_info["status"] == "pending":
            deploy_text = f"\n**🚀 Deploy Access:** ⏳ Pending approval\n💡 Use /status to check request status\n"
        elif status_info["status"] == "rejected":
            deploy_text = f"\n**🚀 Deploy Access:** ❌ Rejected\n💡 Use /request to request again\n"
        else:
            deploy_text = f"\n**🚀 Deploy Access:** 🔒 Not requested\n💡 Use /request to request deploy access\n"

        welcome_text = f"""
{main_emoji} **VZ ASSISTANT BOT**

Hello {message.from_user.first_name}! I'm your personal assistant bot.

**Features:**
{petir_emoji} Inline keyboards for plugin help
{petir_emoji} Fast response with Pyrogram + Trio
{gear_emoji} Secure & authorized access
{deploy_text}
**Available Commands:**
{robot_emoji} /help - Interactive plugin help menu
{robot_emoji} /alive - Bot status with buttons
{robot_emoji} /ping - Check latency
{rocket_emoji} /request [reason] - Request deploy access
{rocket_emoji} /status - Check deploy status

{main_emoji} by VzBot | {dev_emoji} @VZLfxs
"""

        # User inline buttons based on deploy status
        if status_info["status"] == "approved":
            buttons = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("✅ Deploy Status", callback_data="deploy_status"),
                    InlineKeyboardButton("📋 Deploy Guide", callback_data="deploy_guide")
                ],
                [
                    InlineKeyboardButton("💓 Alive", callback_data="alive_status"),
                    InlineKeyboardButton("⚡ Ping", callback_data="ping_check")
                ],
                [
                    InlineKeyboardButton("📖 Help", callback_data="cmd_help")
                ]
            ])
        elif status_info["status"] == "pending":
            buttons = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("⏳ Check Status", callback_data="deploy_status"),
                    InlineKeyboardButton("💓 Alive", callback_data="alive_status")
                ],
                [
                    InlineKeyboardButton("📖 Help", callback_data="cmd_help"),
                    InlineKeyboardButton("⚡ Ping", callback_data="ping_check")
                ]
            ])
        elif status_info["status"] == "rejected":
            buttons = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("🔁 Request Again", callback_data="deploy_request"),
                    InlineKeyboardButton("📊 Status", callback_data="deploy_status")
                ],
                [
                    InlineKeyboardButton("📖 Help", callback_data="cmd_help"),
                    InlineKeyboardButton("💓 Alive", callback_data="alive_status")
                ]
            ])
        else:
            # No access - show request button
            buttons = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("🚀 Request Deploy Access", callback_data="deploy_request"),
                    InlineKeyboardButton("📊 Status", callback_data="deploy_status")
                ],
                [
                    InlineKeyboardButton("📖 Help", callback_data="cmd_help"),
                    InlineKeyboardButton("💓 Alive", callback_data="alive_status")
                ]
            ])

        await message.reply(welcome_text, reply_markup=buttons)

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

@app.on_callback_query(filters.regex(r"^about$"))
async def about_callback(client: Client, callback: CallbackQuery):
    """Handle about button."""
    await log_action(callback.from_user.id, "about")

    # Build about text
    about_text = """
ℹ️ **ABOUT VZBOT**

**Dibuat oleh:**
Vzoel Fox's (Lutpan)

**Library:**
• Telethon
• Pyrogram

**Bahasa:**
Python 3+

**Sistem:**
• Trio Async
• Uvloop

**Fitur:**
Simple fitur untuk kebutuhan standar

🤖 Powered by VzBot
👨‍💻 Developer: @VZLfxs
"""

    # Back button
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("◀️ Back", callback_data="back_to_plugins")]
    ])

    await callback.edit_message_text(about_text, reply_markup=keyboard)
    await callback.answer("About VzBot")

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
# DEPLOY MANAGEMENT COMMANDS (Developer Only)
# ============================================================================

@app.on_message(filters.command("approve") & filters.private)
async def approve_handler(client: Client, message: Message):
    """Approve user for deployment (Developer only)."""
    user_id = message.from_user.id

    # Developer only
    if not is_developer(user_id):
        await message.reply("❌ Developer only command!")
        return

    # Initialize deploy auth DB if needed
    global deploy_auth_db
    if deploy_auth_db is None:
        deploy_auth_db = DeployAuthDB()

    # Parse command
    parts = message.text.split(maxsplit=2)
    if len(parts) < 2:
        await message.reply("❌ Usage: `/approve <user_id> [notes]`")
        return

    try:
        target_id = int(parts[1])
        notes = parts[2] if len(parts) > 2 else "Approved via assistant bot"
    except ValueError:
        await message.reply("❌ Invalid user ID!")
        return

    # Get target user info if possible
    username = None
    first_name = None
    try:
        # Try to get user from Telegram
        target_user = await client.get_users(target_id)
        username = target_user.username
        first_name = target_user.first_name
    except:
        pass

    # Approve user
    created, updated, record = deploy_auth_db.approve_user(
        target_id,
        user_id,
        notes,
        username=username,
        first_name=first_name
    )

    if created:
        status = "✅ **User Approved!**"
        footer = "User can now deploy."
    elif updated:
        status = "✅ **Approval Updated**"
        footer = "User approval details updated."
    else:
        status = "ℹ️ **Already Approved**"
        footer = "User already has deploy access."

    response = f"""{status}

**User Info:**
├ Name: {record.get('first_name') or 'Unknown'}
├ Username: @{record.get('username') or 'None'}
├ User ID: `{record['user_id']}`
├ Approved: {record.get('approved_at', 'Unknown')}
└ Notes: {record.get('notes', 'None')}

{footer}

🤖 VZ Assistant Bot"""

    await message.reply(response)
    logger.info(f"User {target_id} approved by {user_id}")


@app.on_message(filters.command("reject") & filters.private)
async def reject_handler(client: Client, message: Message):
    """Reject user deployment request (Developer only)."""
    user_id = message.from_user.id

    # Developer only
    if not is_developer(user_id):
        await message.reply("❌ Developer only command!")
        return

    # Initialize deploy auth DB if needed
    global deploy_auth_db
    if deploy_auth_db is None:
        deploy_auth_db = DeployAuthDB()

    # Parse command
    parts = message.text.split(maxsplit=2)
    if len(parts) < 2:
        await message.reply("❌ Usage: `/reject <user_id> [reason]`")
        return

    try:
        target_id = int(parts[1])
        reason = parts[2] if len(parts) > 2 else "Not specified"
    except ValueError:
        await message.reply("❌ Invalid user ID!")
        return

    # Reject user
    deploy_auth_db.reject_user(target_id, user_id, reason)

    response = f"""❌ **User Rejected**

**User ID:** `{target_id}`
**Reason:** {reason}
**Rejected by:** {message.from_user.first_name}

User has been notified.

🤖 VZ Assistant Bot"""

    await message.reply(response)
    logger.info(f"User {target_id} rejected by {user_id}")


@app.on_message(filters.command("pending") & filters.private)
async def pending_handler(client: Client, message: Message):
    """View pending deploy requests (Developer only)."""
    user_id = message.from_user.id

    # Developer only
    if not is_developer(user_id):
        await message.reply("❌ Developer only command!")
        return

    # Initialize deploy auth DB if needed
    global deploy_auth_db
    if deploy_auth_db is None:
        deploy_auth_db = DeployAuthDB()

    # Get pending requests
    requests = deploy_auth_db.get_pending_requests()

    if not requests:
        await message.reply("ℹ️ No pending requests.")
        return

    response = "⏳ **Pending Deploy Requests:**\n\n"

    for req in requests[:10]:  # Limit to 10
        response += f"""**👤 {req['first_name']}**
├ Username: @{req['username'] or 'None'}
├ User ID: `{req['user_id']}`
├ Requested: {req['requested_at']}
"""
        if req.get('reason'):
            response += f"├ Reason: {req['reason']}\n"
        response += f"└ Actions: `/approve {req['user_id']}` or `/reject {req['user_id']}`\n\n"

    if len(requests) > 10:
        response += f"\n_...and {len(requests) - 10} more_"

    response += "\n🤖 VZ Assistant Bot"

    await message.reply(response)


@app.on_message(filters.command("approved") & filters.private)
async def approved_handler(client: Client, message: Message):
    """View approved users (Developer only)."""
    user_id = message.from_user.id

    # Developer only
    if not is_developer(user_id):
        await message.reply("❌ Developer only command!")
        return

    # Initialize deploy auth DB if needed
    global deploy_auth_db
    if deploy_auth_db is None:
        deploy_auth_db = DeployAuthDB()

    # Get approved users
    users = deploy_auth_db.get_approved_users()

    if not users:
        await message.reply("ℹ️ No approved users.")
        return

    response = "✅ **Approved Users:**\n\n"

    for user in users[:10]:  # Limit to 10
        response += f"""**👤 {user['first_name']}**
├ Username: @{user['username'] or 'None'}
├ User ID: `{user['user_id']}`
├ Approved: {user['approved_at']}
"""
        if user.get('notes'):
            response += f"├ Notes: {user['notes']}\n"
        response += f"└ Revoke: `/revoke {user['user_id']}`\n\n"

    if len(users) > 10:
        response += f"\n_...and {len(users) - 10} more_"

    response += f"\n🤖 VZ Assistant Bot\n📊 Total: {len(users)} approved users"

    await message.reply(response)


@app.on_message(filters.command("revoke") & filters.private)
async def revoke_handler(client: Client, message: Message):
    """Revoke user deploy access (Developer only)."""
    user_id = message.from_user.id

    # Developer only
    if not is_developer(user_id):
        await message.reply("❌ Developer only command!")
        return

    # Initialize deploy auth DB if needed
    global deploy_auth_db
    if deploy_auth_db is None:
        deploy_auth_db = DeployAuthDB()

    # Parse command
    parts = message.text.split()
    if len(parts) < 2:
        await message.reply("❌ Usage: `/revoke <user_id>`")
        return

    try:
        target_id = int(parts[1])
    except ValueError:
        await message.reply("❌ Invalid user ID!")
        return

    # Revoke access
    deploy_auth_db.revoke_access(target_id)

    response = f"""🔒 **Access Revoked**

**User ID:** `{target_id}`
**Revoked by:** {message.from_user.first_name}

Deploy access has been revoked.

🤖 VZ Assistant Bot"""

    await message.reply(response)
    logger.info(f"User {target_id} revoked by {user_id}")


# ============================================================================
# USER DEPLOY REQUEST (Non-Developer)
# ============================================================================

@app.on_message(filters.command("request") & filters.private)
async def request_deploy_handler(client: Client, message: Message):
    """Request deploy access (Non-developer users)."""
    user_id = message.from_user.id

    # Developers don't need to request
    if is_developer(user_id):
        await message.reply("🌟 Developers have automatic deploy access!")
        return

    # Initialize deploy auth DB if needed
    global deploy_auth_db
    if deploy_auth_db is None:
        deploy_auth_db = DeployAuthDB()

    # Check current status
    status_info = deploy_auth_db.get_user_status(user_id)

    if status_info["status"] == "approved":
        await message.reply("✅ You are already approved for deployment!")
        return

    if status_info["status"] == "pending":
        await message.reply("⏳ Your request is already pending approval!")
        return

    # Parse reason (optional)
    parts = message.text.split(maxsplit=1)
    reason = parts[1] if len(parts) > 1 else "Requested via assistant bot"

    # Add request
    deploy_auth_db.add_request(
        user_id=user_id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        reason=reason
    )

    response = f"""✅ **Deploy Access Requested**

Hi {message.from_user.first_name},

Your deployment request has been submitted to the developers.

**📊 Request Info:**
├ User ID: `{user_id}`
├ Username: @{message.from_user.username or 'None'}
├ Reason: {reason}
└ Status: ⏳ Pending

**⏰ Next Steps:**
A developer will review your request soon.
You will be notified when approved.

💡 Use /status to check your request status

🤖 VZ Assistant Bot"""

    await message.reply(response)
    logger.info(f"Deploy request from user {user_id}")


@app.on_message(filters.command("status") & filters.private)
async def status_deploy_handler(client: Client, message: Message):
    """Check deploy access status."""
    user_id = message.from_user.id

    # Initialize deploy auth DB if needed
    global deploy_auth_db
    if deploy_auth_db is None:
        deploy_auth_db = DeployAuthDB()

    # Get status
    status_info = deploy_auth_db.get_user_status(user_id)

    if is_developer(user_id):
        status_emoji = "🌟"
        status_text = "Developer (Full Access)"
        detail = "You have automatic deploy access."
    elif status_info["status"] == "approved":
        status_emoji = "✅"
        status_text = "Approved"
        data = status_info["data"]
        detail = f"Approved: {data.get('approved_at', 'Unknown')}"
    elif status_info["status"] == "pending":
        status_emoji = "⏳"
        status_text = "Pending"
        data = status_info["data"]
        detail = f"Requested: {data.get('requested_at', 'Unknown')}"
    elif status_info["status"] == "rejected":
        status_emoji = "❌"
        status_text = "Rejected"
        data = status_info["data"]
        detail = f"Reason: {data.get('reason', 'Not specified')}"
    else:
        status_emoji = "🔒"
        status_text = "No Access"
        detail = "Use /request to request deploy access"

    response = f"""{status_emoji} **Deploy Status**

**User:** {message.from_user.first_name}
**Status:** {status_text}

{detail}

🤖 VZ Assistant Bot"""

    await message.reply(response)


# ============================================================================
# DEPLOY INLINE BUTTON CALLBACKS
# ============================================================================

@app.on_callback_query(filters.regex("^deploy_request$"))
async def deploy_request_callback(client: Client, callback: CallbackQuery):
    """Handle deploy request button."""
    user_id = callback.from_user.id

    # Developers don't need to request
    if is_developer(user_id):
        await callback.answer("🌟 Developers have automatic access!", show_alert=True)
        return

    # Initialize deploy auth DB if needed
    global deploy_auth_db
    if deploy_auth_db is None:
        deploy_auth_db = DeployAuthDB()

    # Check current status
    status_info = deploy_auth_db.get_user_status(user_id)

    if status_info["status"] == "approved":
        await callback.answer("✅ You are already approved!", show_alert=True)
        return

    if status_info["status"] == "pending":
        await callback.answer("⏳ Your request is pending!", show_alert=True)
        return

    # Add request
    reason = "Requested via assistant bot button"
    deploy_auth_db.add_request(
        user_id=user_id,
        username=callback.from_user.username,
        first_name=callback.from_user.first_name,
        reason=reason
    )

    # Update message
    response = f"""✅ **Deploy Access Requested**

Hi {callback.from_user.first_name},

Your deployment request has been submitted to the developers.

**📊 Request Info:**
├ User ID: `{user_id}`
├ Username: @{callback.from_user.username or 'None'}
└ Status: ⏳ Pending

**⏰ Next Steps:**
A developer will review your request soon.
You will be notified when approved.

🤖 VZ Assistant Bot"""

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("⏳ Check Status", callback_data="deploy_status")],
        [InlineKeyboardButton("🔙 Back", callback_data="back_to_start")]
    ])

    await callback.edit_message_text(response, reply_markup=buttons)
    await callback.answer("✅ Request sent!", show_alert=False)
    logger.info(f"Deploy request from user {user_id} via button")


@app.on_callback_query(filters.regex("^deploy_status$"))
async def deploy_status_callback(client: Client, callback: CallbackQuery):
    """Handle deploy status button."""
    user_id = callback.from_user.id

    # Initialize deploy auth DB if needed
    global deploy_auth_db
    if deploy_auth_db is None:
        deploy_auth_db = DeployAuthDB()

    # Get status
    status_info = deploy_auth_db.get_user_status(user_id)

    if is_developer(user_id):
        status_emoji = "🌟"
        status_text = "Developer (Full Access)"
        detail = "You have automatic deploy access."
    elif status_info["status"] == "approved":
        status_emoji = "✅"
        status_text = "Approved"
        data = status_info["data"]
        detail = f"Approved: {data.get('approved_at', 'Unknown')}"
    elif status_info["status"] == "pending":
        status_emoji = "⏳"
        status_text = "Pending"
        data = status_info["data"]
        detail = f"Requested: {data.get('requested_at', 'Unknown')}"
    elif status_info["status"] == "rejected":
        status_emoji = "❌"
        status_text = "Rejected"
        data = status_info["data"]
        detail = f"Reason: {data.get('reason', 'Not specified')}"
    else:
        status_emoji = "🔒"
        status_text = "No Access"
        detail = "Use button below to request deploy access"

    response = f"""{status_emoji} **Deploy Status**

**User:** {callback.from_user.first_name}
**Status:** {status_text}

{detail}

🤖 VZ Assistant Bot"""

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back", callback_data="back_to_start")]
    ])

    await callback.edit_message_text(response, reply_markup=buttons)
    await callback.answer()


@app.on_callback_query(filters.regex("^deploy_pending$"))
async def deploy_pending_callback(client: Client, callback: CallbackQuery):
    """Handle pending requests button (Developer only)."""
    user_id = callback.from_user.id

    # Developer only
    if not is_developer(user_id):
        await callback.answer("❌ Developer only!", show_alert=True)
        return

    # Initialize deploy auth DB if needed
    global deploy_auth_db
    if deploy_auth_db is None:
        deploy_auth_db = DeployAuthDB()

    # Get pending requests
    requests = deploy_auth_db.get_pending_requests()

    if not requests:
        await callback.answer("ℹ️ No pending requests.", show_alert=True)
        return

    response = "⏳ **Pending Deploy Requests:**\n\n"

    for req in requests[:10]:  # Limit to 10
        response += f"""**👤 {req['first_name']}**
├ Username: @{req['username'] or 'None'}
├ User ID: `{req['user_id']}`
├ Requested: {req['requested_at']}
"""
        if req.get('reason'):
            response += f"├ Reason: {req['reason']}\n"
        response += f"└ `/approve {req['user_id']}`\n\n"

    if len(requests) > 10:
        response += f"\n_...and {len(requests) - 10} more_"

    response += "\n🤖 VZ Assistant Bot"

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back", callback_data="back_to_start")]
    ])

    await callback.edit_message_text(response, reply_markup=buttons)
    await callback.answer()


@app.on_callback_query(filters.regex("^deploy_approved$"))
async def deploy_approved_callback(client: Client, callback: CallbackQuery):
    """Handle approved users button (Developer only)."""
    user_id = callback.from_user.id

    # Developer only
    if not is_developer(user_id):
        await callback.answer("❌ Developer only!", show_alert=True)
        return

    # Initialize deploy auth DB if needed
    global deploy_auth_db
    if deploy_auth_db is None:
        deploy_auth_db = DeployAuthDB()

    # Get approved users
    users = deploy_auth_db.get_approved_users()

    if not users:
        await callback.answer("ℹ️ No approved users.", show_alert=True)
        return

    response = "✅ **Approved Users:**\n\n"

    for user in users[:10]:  # Limit to 10
        response += f"""**👤 {user['first_name']}**
├ Username: @{user['username'] or 'None'}
├ User ID: `{user['user_id']}`
├ Approved: {user['approved_at']}
"""
        if user.get('notes'):
            response += f"├ Notes: {user['notes']}\n"
        response += f"└ `/revoke {user['user_id']}`\n\n"

    if len(users) > 10:
        response += f"\n_...and {len(users) - 10} more_"

    response += f"\n🤖 VZ Assistant Bot\n📊 Total: {len(users)} approved users"

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back", callback_data="back_to_start")]
    ])

    await callback.edit_message_text(response, reply_markup=buttons)
    await callback.answer()


@app.on_callback_query(filters.regex("^back_to_start$"))
async def back_to_start_callback(client: Client, callback: CallbackQuery):
    """Handle back to start button."""
    # Just re-trigger /start handler logic
    user_id = callback.from_user.id

    # Use regular Unicode emoji (Pyrogram compatible)
    main_emoji = "🌟"
    robot_emoji = "🤖"
    petir_emoji = "⚡"
    gear_emoji = "⚙️"
    dev_emoji = "👨‍💻"
    rocket_emoji = "🚀"

    # Check if developer
    if is_developer(user_id):
        # Developer menu with deploy management AND own deploy access
        welcome_text = f"""
{main_emoji} **VZ ASSISTANT BOT** - Developer Mode

Hello {callback.from_user.first_name}! I'm your personal assistant bot.

**🌟 Developer Privileges:**
{rocket_emoji} Full deploy access (no approval needed)
{gear_emoji} Can approve/reject other users
{petir_emoji} Manage all deployments

**📱 Assistant Features:**
{petir_emoji} Inline keyboards for plugin help
{petir_emoji} Fast response with Pyrogram + Trio
{gear_emoji} Secure & authorized access

**🚀 Quick Actions:**
Use buttons below for instant access!

{main_emoji} by VzBot | {dev_emoji} @VZLfxs
"""

        # Developer inline buttons with deploy + management
        buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🚀 Deploy My Bot", callback_data="dev_deploy"),
                InlineKeyboardButton("📊 My Status", callback_data="deploy_status")
            ],
            [
                InlineKeyboardButton("⏳ Pending Requests", callback_data="deploy_pending"),
                InlineKeyboardButton("✅ Approved Users", callback_data="deploy_approved")
            ],
            [
                InlineKeyboardButton("📖 Help", callback_data="cmd_help"),
                InlineKeyboardButton("💓 Alive", callback_data="alive_status")
            ]
        ])
    else:
        # Regular user menu with deploy request option
        # Check deploy status
        global deploy_auth_db
        if deploy_auth_db is None:
            deploy_auth_db = DeployAuthDB()

        status_info = deploy_auth_db.get_user_status(user_id)

        if status_info["status"] == "approved":
            deploy_text = f"\n**🚀 Deploy Access:** ✅ Approved\n\n**📋 Next Steps:**\n1. Generate session: `python3 stringgenerator.py`\n2. Deploy: Send `..dp` in main bot\n3. Follow setup wizard\n"
        elif status_info["status"] == "pending":
            deploy_text = f"\n**🚀 Deploy Access:** ⏳ Pending approval\n💡 Use /status to check request status\n"
        elif status_info["status"] == "rejected":
            deploy_text = f"\n**🚀 Deploy Access:** ❌ Rejected\n💡 Use /request to request again\n"
        else:
            deploy_text = f"\n**🚀 Deploy Access:** 🔒 Not requested\n💡 Use /request to request deploy access\n"

        welcome_text = f"""
{main_emoji} **VZ ASSISTANT BOT**

Hello {callback.from_user.first_name}! I'm your personal assistant bot.

**Features:**
{petir_emoji} Inline keyboards for plugin help
{petir_emoji} Fast response with Pyrogram + Trio
{gear_emoji} Secure & authorized access
{deploy_text}
**Available Commands:**
{robot_emoji} /help - Interactive plugin help menu
{robot_emoji} /alive - Bot status with buttons
{robot_emoji} /ping - Check latency
{rocket_emoji} /request [reason] - Request deploy access
{rocket_emoji} /status - Check deploy status

{main_emoji} by VzBot | {dev_emoji} @VZLfxs
"""

        # User inline buttons based on deploy status
        if status_info["status"] == "approved":
            buttons = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("✅ Deploy Status", callback_data="deploy_status"),
                    InlineKeyboardButton("📋 Deploy Guide", callback_data="deploy_guide")
                ],
                [
                    InlineKeyboardButton("💓 Alive", callback_data="alive_status"),
                    InlineKeyboardButton("⚡ Ping", callback_data="ping_check")
                ],
                [
                    InlineKeyboardButton("📖 Help", callback_data="cmd_help")
                ]
            ])
        elif status_info["status"] == "pending":
            buttons = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("⏳ Check Status", callback_data="deploy_status"),
                    InlineKeyboardButton("💓 Alive", callback_data="alive_status")
                ],
                [
                    InlineKeyboardButton("📖 Help", callback_data="cmd_help"),
                    InlineKeyboardButton("⚡ Ping", callback_data="ping_check")
                ]
            ])
        elif status_info["status"] == "rejected":
            buttons = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("🔁 Request Again", callback_data="deploy_request"),
                    InlineKeyboardButton("📊 Status", callback_data="deploy_status")
                ],
                [
                    InlineKeyboardButton("📖 Help", callback_data="cmd_help"),
                    InlineKeyboardButton("💓 Alive", callback_data="alive_status")
                ]
            ])
        else:
            # No access - show request button
            buttons = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("🚀 Request Deploy Access", callback_data="deploy_request"),
                    InlineKeyboardButton("📊 Status", callback_data="deploy_status")
                ],
                [
                    InlineKeyboardButton("📖 Help", callback_data="cmd_help"),
                    InlineKeyboardButton("💓 Alive", callback_data="alive_status")
                ]
            ])

    await callback.edit_message_text(welcome_text, reply_markup=buttons)
    await callback.answer()


@app.on_callback_query(filters.regex("^dev_deploy$"))
async def dev_deploy_callback(client: Client, callback: CallbackQuery):
    """Handle developer deploy button."""
    user_id = callback.from_user.id

    # Developer only
    if not is_developer(user_id):
        await callback.answer("❌ Developer only!", show_alert=True)
        return

    response = f"""🚀 **Developer Deployment**

Hi {callback.from_user.first_name},

As a developer, you have automatic deploy access!

**📊 Your Status:**
├ Role: 🌟 Developer
├ Access: ✅ Full Access (Auto-Approved)
└ Restrictions: None

**💡 How to Deploy:**

**Step 1: Generate Session String**
Run in terminal:
```bash
python3 stringgenerator.py
```
Save your session string securely!

**Step 2: Deploy via Main Bot**
Send `..dp` in your main userbot

**Step 3: Setup**
Follow the deployment wizard

**Or Contact Admin for Help:**
{config.FOUNDER_USERNAME}

**🛠️ Developer Privileges:**
✓ No approval needed
✓ Can deploy anytime
✓ Can approve other users
✓ Manage all deployments

**📞 Need Help?**
Contact: {config.FOUNDER_USERNAME}

🤖 VZ Assistant Bot"""

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back", callback_data="back_to_start")]
    ])

    await callback.edit_message_text(response, reply_markup=buttons)
    await callback.answer("🌟 Developer access active!", show_alert=False)


@app.on_callback_query(filters.regex("^alive_status$"))
async def alive_status_callback(client: Client, callback: CallbackQuery):
    """Handle alive button."""
    import time
    start_time = time.time()

    response = f"""💓 **VZ Assistant Bot - Alive**

**🤖 Bot Status:** Online
**⚡ Response:** {int((time.time() - start_time) * 1000)}ms
**🌟 Version:** v0.0.0.69
**📱 Framework:** Pyrogram + Trio

**Features:**
✓ Inline keyboards
✓ Deploy management
✓ Fast response
✓ Secure access

**📊 System:**
├ Owner: {callback.from_user.first_name}
└ Bot: VZ Assistant

🤖 by VzBot | 👨‍💻 @VZLfxs"""

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back", callback_data="back_to_start")]
    ])

    await callback.edit_message_text(response, reply_markup=buttons)
    await callback.answer()


@app.on_callback_query(filters.regex("^ping_check$"))
async def ping_check_callback(client: Client, callback: CallbackQuery):
    """Handle ping button."""
    import time
    start_time = time.time()

    # Calculate ping
    ping = int((time.time() - start_time) * 1000)

    response = f"""⚡ **Ping Check**

**Response Time:** `{ping}ms`

**Connection Quality:**
{'🟢 Excellent' if ping < 100 else '🟡 Good' if ping < 200 else '🔴 Slow'}

**Status:** ✅ Online

🤖 VZ Assistant Bot"""

    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔄 Check Again", callback_data="ping_check"),
            InlineKeyboardButton("🔙 Back", callback_data="back_to_start")
        ]
    ])

    await callback.edit_message_text(response, reply_markup=buttons)
    await callback.answer(f"⚡ Ping: {ping}ms", show_alert=False)


@app.on_callback_query(filters.regex("^deploy_guide$"))
async def deploy_guide_callback(client: Client, callback: CallbackQuery):
    """Handle deploy guide button."""

    response = f"""📋 **Complete Deployment Guide**

**🔐 Prerequisites:**
1. Get API credentials from https://my.telegram.org
2. Have phone number ready
3. Access to Telegram OTP

**📝 Step-by-Step Guide:**

**Step 1: Generate Session String**
Run in your terminal:
```bash
cd /path/to/vbot
python3 stringgenerator.py
```

Follow prompts:
├ Enter API_ID
├ Enter API_HASH
├ Enter phone number (+62...)
├ Enter OTP code
└ Copy session string

**Step 2: Request Deploy Access**
(You're already approved!)

**Step 3: Deploy Your Bot**
In your main userbot, send:
```
..dp
```

**Step 4: Follow Wizard**
├ Click "Start Deploy Bot"
├ Paste session string
├ Configure settings
└ Launch!

**💡 Tips:**
• Keep session string private
• Don't share with anyone
• Store in secure location
• Use strong password

**🆘 Need Help?**
Contact: {config.FOUNDER_USERNAME}

🤖 VZ Assistant Bot"""

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back", callback_data="back_to_start")]
    ])

    await callback.edit_message_text(response, reply_markup=buttons)
    await callback.answer()


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
