"""
VZ ASSISTANT v0.0.0.69
Help Plugin - Command Documentation & Navigation

2025© Vzoel Fox's Lutpan
Founder & DEVELOPER : @VZLfxs
"""

import ast
import os
from typing import Dict, List

from telethon import events
import config
from utils.animation import animate_loading
# Note: help.py can use animate_loading as it's generic enough
# or can create help-specific animation in utils/animation.py later
from helpers.inline import KeyboardBuilder

# Global variables (set by main.py)
vz_client = None
vz_emoji = None


def _load_plugin_metadata() -> List[Dict[str, object]]:
    """Load plugin metadata from module docstrings."""
    plugin_dir = os.path.dirname(__file__)
    metadata: List[Dict[str, object]] = []

    for filename in sorted(os.listdir(plugin_dir)):
        if not filename.endswith(".py") or filename == "__init__.py":
            continue

        file_id = filename[:-3]
        file_path = os.path.join(plugin_dir, filename)

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                module = ast.parse(f.read())
            docstring = ast.get_docstring(module) or ""
        except (SyntaxError, OSError):
            docstring = ""

        doc_lines = [line.strip() for line in docstring.splitlines() if line.strip()]

        summary = next((line for line in doc_lines if "Plugin" in line), "")
        if not summary and doc_lines:
            summary = doc_lines[0]

        commands: List[str] = []
        capture_commands = False
        for line in doc_lines:
            if line.lower().startswith("commands"):
                capture_commands = True
                continue
            if capture_commands:
                if line.startswith("-"):
                    commands.append(line[1:].strip())
                else:
                    capture_commands = False

        metadata.append(
            {
                "id": file_id,
                "filename": filename,
                "display_name": file_id.replace("_", " ").title(),
                "summary": summary,
                "commands": commands,
            }
        )

    return metadata


PLUGIN_METADATA: List[Dict[str, object]] = _load_plugin_metadata()

# ============================================================================
# COMMAND DATABASE
# ============================================================================

# Sudoers commands (visible to all)
SUDOERS_COMMANDS = {
    "Basic": {
        "ping": {
            "cmd": ".ping",
            "desc": "Check latency, uptime, and bot status",
            "usage": ".ping",
            "example": ".ping"
        },
        "pink": {
            "cmd": ".pink",
            "desc": "Check latency with color emoji (auto-triggers .limit)",
            "usage": ".pink",
            "example": ".pink"
        },
        "pong": {
            "cmd": ".pong",
            "desc": "Show uptime (auto-triggers .alive)",
            "usage": ".pong",
            "example": ".pong"
        },
        "alive": {
            "cmd": ".alive",
            "desc": "Show bot information and status",
            "usage": ".alive",
            "example": ".alive"
        },
        "help": {
            "cmd": ".help",
            "desc": "Show this help menu",
            "usage": ".help",
            "example": ".help"
        }
    },
    "Admin": {
        "admin": {
            "cmd": ".admin",
            "desc": "Promote user to admin",
            "usage": ".admin @username <title> | .admin reply <title>",
            "example": ".admin @user Moderator"
        },
        "unadmin": {
            "cmd": ".unadmin",
            "desc": "Demote admin to regular user",
            "usage": ".unadmin @username | .unadmin reply",
            "example": ".unadmin @user"
        }
    },
    "Broadcast": {
        "gcast": {
            "cmd": ".gcast",
            "desc": "Broadcast message to all groups",
            "usage": ".gcast <message> | .gcast reply",
            "example": ".gcast Hello everyone!"
        },
        "bl": {
            "cmd": ".bl",
            "desc": "Add group to blacklist (won't receive gcast)",
            "usage": ".bl <group_id> | .bl (in group)",
            "example": ".bl -1001234567890"
        },
        "dbl": {
            "cmd": ".dbl",
            "desc": "Remove group from blacklist",
            "usage": ".dbl <group_id> | .dbl (in group)",
            "example": ".dbl -1001234567890"
        }
    },
    "Group": {
        "tag": {
            "cmd": ".tag",
            "desc": "Tag all members in group (no admin required)",
            "usage": ".tag <message> | .tag reply",
            "example": ".tag Important announcement!"
        },
        "stag": {
            "cmd": ".stag",
            "desc": "Stop ongoing tag operation",
            "usage": ".stag",
            "example": ".stag"
        },
        "lock": {
            "cmd": ".lock",
            "desc": "Auto-delete messages from user (requires admin)",
            "usage": ".lock @username | .lock reply",
            "example": ".lock @spammer"
        },
        "unlock": {
            "cmd": ".unlock",
            "desc": "Remove user from lock list",
            "usage": ".unlock @username | .unlock reply",
            "example": ".unlock @user"
        }
    },
    "Info": {
        "id": {
            "cmd": ".id",
            "desc": "Get user info (ID, name, username, group count)",
            "usage": ".id @username | .id reply",
            "example": ".id @user"
        },
        "getfileid": {
            "cmd": ".getfileid",
            "desc": "Get file ID from media",
            "usage": ".getfileid (reply to media)",
            "example": ".getfileid"
        }
    },
    "Settings": {
        "prefix": {
            "cmd": ".prefix",
            "desc": "Change command prefix",
            "usage": ".prefix <new_prefix>",
            "example": ".prefix !"
        },
        "pmon": {
            "cmd": ".pmon",
            "desc": "Enable PM permit system",
            "usage": ".pmon",
            "example": ".pmon"
        },
        "pmoff": {
            "cmd": ".pmoff",
            "desc": "Disable PM permit system",
            "usage": ".pmoff",
            "example": ".pmoff"
        },
        "setpm": {
            "cmd": ".setpm",
            "desc": "Set custom PM permit message",
            "usage": ".setpm <message>",
            "example": ".setpm Please wait for approval"
        }
    }
}

# Developer commands (only visible to developers)
DEVELOPER_COMMANDS = {
    "Developer": {
        "vzoel": {
            "cmd": ".vzoel",
            "desc": "Show developer profile (12 edit animation)",
            "usage": ".vzoel",
            "example": ".vzoel"
        },
        "dp": {
            "cmd": ".dp",
            "desc": "Deploy new sudoer via bot",
            "usage": ".dp",
            "example": ".dp"
        },
        "cr": {
            "cmd": ".cr",
            "desc": "Force stop sudoer session",
            "usage": ".cr <user_id>",
            "example": ".cr 123456789"
        },
        "out": {
            "cmd": ".out",
            "desc": "Force logout sudoer from Telegram",
            "usage": ".out @username | .out reply",
            "example": ".out @user"
        },
        "sdb": {
            "cmd": ".sdb",
            "desc": "View sudoer's database",
            "usage": ".sdb @username",
            "example": ".sdb @user"
        },
        "sgd": {
            "cmd": ".sgd",
            "desc": "Get data from reply context",
            "usage": ".sgd reply",
            "example": ".sgd"
        }
    },
    "Sudo": {
        "s{command}": {
            "cmd": ".s<command>",
            "desc": "Execute sudoer command as developer",
            "usage": ".s<command> (example: .sgcast)",
            "example": ".sgcast Hello from developer!"
        }
    }
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_all_categories(is_developer=False):
    """Get all command categories."""
    categories = list(SUDOERS_COMMANDS.keys())
    if is_developer:
        categories.extend(DEVELOPER_COMMANDS.keys())
    return categories

def get_category_commands(category, is_developer=False):
    """Get commands in a category."""
    if category in SUDOERS_COMMANDS:
        return SUDOERS_COMMANDS[category]
    elif is_developer and category in DEVELOPER_COMMANDS:
        return DEVELOPER_COMMANDS[category]
    return {}

def count_total_commands(is_developer=False):
    """Count total available commands."""
    count = sum(len(cmds) for cmds in SUDOERS_COMMANDS.values())
    if is_developer:
        count += sum(len(cmds) for cmds in DEVELOPER_COMMANDS.values())
    return count

# ============================================================================
# HELP COMMAND
# ============================================================================

@events.register(events.NewMessage(pattern=r'^\.help$', outgoing=True))
async def help_handler(event):
    global vz_client, vz_emoji

    """
    .help - Show command help menu

    Interactive inline button menu with:
    - Category navigation
    - Command list per category
    - Detailed command info
    - Developer-only commands (if developer)
    """
    user_id = event.sender_id
    is_developer = config.is_developer(user_id)

    # Show main help menu
    await show_help_menu(event, is_developer)

# ============================================================================
# HELP MENU FUNCTIONS
# ============================================================================

async def show_help_menu(event, is_developer=False, skip_animation=False):
    global vz_client, vz_emoji

    """Show main help menu."""
    # Determine message object (events.NewMessage or events.CallbackQuery)
    message = getattr(event, "message", event)

    # Run 12-phase animation for the initial command only
    if not skip_animation:
        try:
            message = await animate_loading(vz_client, vz_emoji, message)
        except Exception:
            # If animation fails (e.g. callback query edit limitations), fall back to original message
            message = getattr(event, "message", event)

    categories = get_all_categories(is_developer)
    total_commands = count_total_commands(is_developer)

    # Get emojis for footer
    gear_emoji = vz_emoji.getemoji('gear')
    petir_emoji = vz_emoji.getemoji('petir')
    main_emoji = vz_emoji.getemoji('utama')
    robot_emoji = vz_emoji.getemoji('robot')

    # Get additional emojis
    owner_role_emoji = vz_emoji.getemoji('owner')
    telegram_emoji = vz_emoji.getemoji('telegram')

    help_text = f"""
{main_emoji} **VZ ASSISTANT - HELP MENU**

{petir_emoji} **Total Commands:** {total_commands}
{owner_role_emoji} **Role:** {'DEVELOPER' if is_developer else 'SUDOER'}
{gear_emoji} **Prefix:** {config.DEFAULT_PREFIX}

**{telegram_emoji} Categories:**
Select a category to view commands

{robot_emoji} Plugins Digunakan: **HELP**
{petir_emoji} by {main_emoji} {config.RESULT_FOOTER}
"""

    # Create category buttons
    kb = KeyboardBuilder()

    # Add category buttons (2 per row)
    for i, category in enumerate(categories):
        same_row = (i % 2 == 1)
        kb.add_button(f"{main_emoji} {category}", f"help_cat_{category}", same_row=same_row)

    # Add plugin info toggle + close button
    kb.add_button(f"{robot_emoji} Plugin Info", "help_plugin_toggle_show")
    kb.add_button("❌ Close", "help_close", same_row=True)

    buttons = kb.build()

    # Send or edit message
    try:
        if hasattr(message, 'edit'):
            await message.edit(help_text, buttons=buttons)
        elif hasattr(event, 'respond'):
            await event.respond(help_text, buttons=buttons)
    except Exception:
        # Fallback without buttons or premium emoji helper
        try:
            if hasattr(message, 'edit'):
                await vz_client.edit_with_premium_emoji(message, help_text)
            elif hasattr(event, 'respond'):
                await vz_client.send_with_premium_emoji(event.chat_id, help_text)
        except Exception:
            if hasattr(event, 'respond'):
                await event.respond(help_text)

async def show_help_plugin_info(event, is_developer=False):
    global vz_client, vz_emoji

    """Show plugin metadata list with inline buttons."""
    main_emoji = vz_emoji.getemoji('utama')
    robot_emoji = vz_emoji.getemoji('robot')
    petir_emoji = vz_emoji.getemoji('petir')
    telegram_emoji = vz_emoji.getemoji('telegram')
    nyala_emoji = vz_emoji.getemoji('nyala')

    total_plugins = len(PLUGIN_METADATA)
    total_commands = count_total_commands(is_developer)

    plugin_text = f"""
{robot_emoji} **HELP Plugin Directory**

{telegram_emoji} **Total Plugin:** {total_plugins}
{petir_emoji} **Total Commands Terdata:** {total_commands}

{nyala_emoji} **Petunjuk:**
Pilih salah satu plugin di bawah untuk melihat detail modul dan ringkasan perintah.

{robot_emoji} Plugins Digunakan: **HELP**
{petir_emoji} by {main_emoji} {config.RESULT_FOOTER}
"""

    kb = KeyboardBuilder()

    for index, plugin in enumerate(PLUGIN_METADATA):
        kb.add_button(
            f"{robot_emoji} {plugin['display_name']}",
            f"help_plugin_detail_{plugin['id']}",
            same_row=(index % 2 == 1)
        )

    kb.add_button("◀️ Kembali", "help_plugin_toggle_hide")
    kb.add_button("❌ Close", "help_close", same_row=True)

    buttons = kb.build()

    message = getattr(event, "message", event)

    try:
        await message.edit(plugin_text, buttons=buttons)
    except Exception:
        await vz_client.edit_with_premium_emoji(message, plugin_text)


async def show_help_plugin_detail(event, plugin_id):
    global vz_client, vz_emoji

    """Show detailed metadata for a single plugin."""
    plugin = next((item for item in PLUGIN_METADATA if item['id'] == plugin_id), None)

    if not plugin:
        await event.answer("❌ Plugin tidak ditemukan", alert=True)
        return

    main_emoji = vz_emoji.getemoji('utama')
    robot_emoji = vz_emoji.getemoji('robot')
    petir_emoji = vz_emoji.getemoji('petir')
    nyala_emoji = vz_emoji.getemoji('nyala')
    gear_emoji = vz_emoji.getemoji('gear')

    plugin_text = f"""
{robot_emoji} **{plugin['display_name']} Plugin Info**

{gear_emoji} **File:** `{plugin['filename']}`
{nyala_emoji} **Deskripsi:** {plugin['summary'] or 'Ringkasan belum tersedia'}
"""

    if plugin['commands']:
        plugin_text += "\n**Perintah (Docstring):**\n"
        for command in plugin['commands']:
            plugin_text += f"• {command}\n"

    plugin_text += f"""

{robot_emoji} Plugins Digunakan: **{plugin['display_name'].upper()}**
{petir_emoji} by {main_emoji} {config.RESULT_FOOTER}
"""

    kb = KeyboardBuilder()
    kb.add_button("◀️ Daftar Plugin", "help_plugin_toggle_show")
    kb.add_button("🏠 Menu", "help_home", same_row=True)
    kb.add_button("❌ Close", "help_close")

    buttons = kb.build()

    try:
        await event.edit(plugin_text, buttons=buttons)
    except Exception:
        await vz_client.edit_with_premium_emoji(event, plugin_text)

    await event.answer()

# ============================================================================
# CALLBACK HANDLERS
# ============================================================================

@events.register(events.CallbackQuery(pattern=b"help_plugin_toggle_(show|hide)"))
async def help_plugin_toggle_callback(event):
    global vz_client, vz_emoji

    """Toggle plugin info panel visibility."""
    data = event.data.decode('utf-8')
    user_id = event.sender_id
    is_developer = config.is_developer(user_id)

    if data.endswith('show'):
        await show_help_plugin_info(event, is_developer)
        await event.answer(f"{vz_emoji.getemoji('robot')} Menampilkan info plugin")
    else:
        await show_help_menu(event, is_developer, skip_animation=True)
        await event.answer(f"{vz_emoji.getemoji('robot')} Kembali ke menu bantuan")


@events.register(events.CallbackQuery(pattern=b"help_plugin_detail_.*"))
async def help_plugin_detail_callback(event):
    """Handle detailed plugin info requests."""

    plugin_id = event.data.decode('utf-8').replace("help_plugin_detail_", "")
    await show_help_plugin_detail(event, plugin_id)


@events.register(events.CallbackQuery(pattern=b"help_cat_.*"))
async def help_category_callback(event):
    global vz_client, vz_emoji

    """Handle category button click."""
    # Parse category name
    data = event.data.decode('utf-8')
    category = data.replace("help_cat_", "")

    user_id = event.sender_id
    is_developer = config.is_developer(user_id)

    # Get commands in category
    commands = get_category_commands(category, is_developer)

    if not commands:
        await event.answer("❌ Category not found", alert=True)
        return

    # Get emojis for footer
    main_emoji = vz_emoji.getemoji('utama')
    petir_emoji = vz_emoji.getemoji('petir')
    robot_emoji = vz_emoji.getemoji('robot')
    telegram_emoji = vz_emoji.getemoji('telegram')

    # Build category view
    category_text = f"""
{telegram_emoji} **{category} Commands**

**Available commands in this category:**

"""

    for cmd_name, cmd_data in commands.items():
        category_text += f"• `{cmd_data['cmd']}` - {cmd_data['desc']}\n"

    kuning_emoji = vz_emoji.getemoji('kuning')

    category_text += f"""

{kuning_emoji} **Tip:** Click a command for detailed info

{robot_emoji} Plugins Digunakan: **HELP**
{petir_emoji} by {main_emoji} {config.RESULT_FOOTER}"""

    # Create command buttons
    kb = KeyboardBuilder()

    for cmd_name in commands.keys():
        kb.add_button(f"{petir_emoji} {cmd_name}", f"help_cmd_{category}_{cmd_name}")

    # Add navigation buttons
    kb.add_button("◀️ Back", "help_back")
    kb.add_button("❌ Close", "help_close", same_row=True)

    buttons = kb.build()

    try:
        await event.edit(category_text, buttons=buttons)
    except:
        await vz_client.edit_with_premium_emoji(event, category_text)

    await event.answer()

@events.register(events.CallbackQuery(pattern=b"help_cmd_.*"))
async def help_command_callback(event):
    global vz_client, vz_emoji

    """Handle command detail button click."""
    # Parse command info
    data = event.data.decode('utf-8')
    parts = data.replace("help_cmd_", "").split("_", 1)

    if len(parts) < 2:
        await event.answer("❌ Invalid command", alert=True)
        return

    category, cmd_name = parts

    user_id = event.sender_id
    is_developer = config.is_developer(user_id)

    # Get command data
    commands = get_category_commands(category, is_developer)
    cmd_data = commands.get(cmd_name)

    if not cmd_data:
        await event.answer("❌ Command not found", alert=True)
        return

    # Get emojis for footer
    main_emoji = vz_emoji.getemoji('utama')
    petir_emoji = vz_emoji.getemoji('petir')
    robot_emoji = vz_emoji.getemoji('robot')
    gear_emoji = vz_emoji.getemoji('gear')

    # Build command detail view
    cmd_text = f"""
{gear_emoji} **Command Details**

**Command:** `{cmd_data['cmd']}`
**Description:** {cmd_data['desc']}

**Usage:**
`{cmd_data['usage']}`

**Example:**
`{cmd_data['example']}`

{petir_emoji} **Category:** {category}

{robot_emoji} Plugins Digunakan: **HELP**
{petir_emoji} by {main_emoji} {config.RESULT_FOOTER}"""

    # Create navigation buttons
    kb = KeyboardBuilder()
    kb.add_button("◀️ Back", f"help_cat_{category}")
    kb.add_button("🏠 Home", "help_home", same_row=True)
    kb.add_button("❌ Close", "help_close")

    buttons = kb.build()

    try:
        await event.edit(cmd_text, buttons=buttons)
    except:
        await vz_client.edit_with_premium_emoji(event, cmd_text)

    await event.answer()

@events.register(events.CallbackQuery(pattern=b"help_back"))
async def help_back_callback(event):
    global vz_client, vz_emoji

    """Handle back button."""
    user_id = event.sender_id
    is_developer = config.is_developer(user_id)

    await show_help_menu(event, is_developer, skip_animation=True)
    await event.answer()

@events.register(events.CallbackQuery(pattern=b"help_home"))
async def help_home_callback(event):
    global vz_client, vz_emoji

    """Handle home button."""
    user_id = event.sender_id
    is_developer = config.is_developer(user_id)

    await show_help_menu(event, is_developer, skip_animation=True)

    main_emoji = vz_emoji.getemoji('utama')
    await event.answer(f"{main_emoji} Returning to main menu...")

@events.register(events.CallbackQuery(pattern=b"help_close"))
async def help_close_callback(event):
    global vz_client, vz_emoji

    """Handle close button."""
    await event.delete()

    centang_emoji = vz_emoji.getemoji('centang')
    await event.answer(f"{centang_emoji} Help menu closed")

print("✅ Plugin loaded: help.py")
