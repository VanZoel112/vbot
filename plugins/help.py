"""
VZ ASSISTANT v0.0.0.69
Help Plugin - Command Documentation & Navigation

2025© Vzoel Fox's Lutpan
Founder & DEVELOPER : @VZLfxs
"""

import ast
import logging
import os
from typing import Dict, List

from telethon import events
import config

# Global variables (set by main.py)
vz_client = None
vz_emoji = None


logger = logging.getLogger(__name__)


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


def build_sudoer_help_text(emoji_manager, user_id=None) -> str:
    """Build the static sudoer help text."""
    main_emoji = emoji_manager.getemoji('utama')
    petir_emoji = emoji_manager.getemoji('petir')
    robot_emoji = emoji_manager.getemoji('robot')
    gear_emoji = emoji_manager.getemoji('gear')
    owner_emoji = emoji_manager.getemoji('owner')
    dev_emoji = emoji_manager.getemoji('developer')

    # Detect if user is developer
    is_developer = config.is_developer(user_id) if user_id else False
    role = "DEVELOPER" if is_developer else "SUDOER"
    role_emoji = dev_emoji if is_developer else owner_emoji

    total_commands = count_total_commands(is_developer=is_developer)

    help_text = f"""{main_emoji} **VZ ASSISTANT - HELP MENU**

{petir_emoji} **Total Commands:** {total_commands}
{role_emoji} **Role:** {role}
{gear_emoji} **Prefix:** {config.DEFAULT_PREFIX}

"""

    for category, commands in SUDOERS_COMMANDS.items():
        help_text += f"\n**{petir_emoji} {category.upper()} COMMANDS:**\n"
        for cmd_data in commands.values():
            help_text += f"• `{cmd_data['cmd']}` - {cmd_data['desc']}\n"

    # Show developer commands if user is developer
    if is_developer:
        help_text += f"\n**{dev_emoji} DEVELOPER EXCLUSIVE COMMANDS:**\n"
        for category, commands in DEVELOPER_COMMANDS.items():
            help_text += f"\n**{petir_emoji} {category}:**\n"
            for cmd_data in commands.values():
                help_text += f"• `{cmd_data['cmd']}` - {cmd_data['desc']}\n"

    help_text += f"""{gear_emoji} **Usage:** Type command for details
{robot_emoji} **Example:** `.ping`, `.admin @user`, `.gcast hello`

{robot_emoji} Plugins Digunakan: **HELP**
{petir_emoji} by {main_emoji} {config.RESULT_FOOTER}
"""

    return help_text

# ============================================================================
# HELP COMMAND (SUDOERS)
# ============================================================================

@events.register(events.NewMessage(pattern=r'^\.help$', outgoing=True))
async def help_handler(event):
    global vz_client, vz_emoji

    """
    .help - Open interactive help via assistant bot.

    Tries to launch the assistant bot inline browser and falls back to
    the static command list if the assistant is unavailable.
    """
    warning_emoji = vz_emoji.getemoji('merah')
    gear_emoji = vz_emoji.getemoji('gear')
    robot_emoji = vz_emoji.getemoji('robot')

    assistant_username = getattr(config, 'ASSISTANT_BOT_USERNAME', None)
    fallback_prefix = None
    fallback_target = event

    if assistant_username:
        opening_text = (
            f"{robot_emoji} **Membuka inline help...**\n"
            f"{gear_emoji} Mohon tunggu sebentar."
        )
        status_msg = await vz_client.edit_with_premium_emoji(event, opening_text)
        fallback_target = status_msg

        try:
            results = await event.client.inline_query(assistant_username, 'help')
            if not results:
                raise RuntimeError('Assistant bot returned no inline results')

            await results[0].click(
                event.chat_id,
                reply_to=event.reply_to_msg_id,
                hide_via=True,
                clear_draft=True,
            )

            await status_msg.delete()
            return
        except Exception as inline_error:
            logger.warning(
                'Failed to open inline help via %s: %s',
                assistant_username,
                inline_error,
            )
            fallback_prefix = (
                f"{warning_emoji} **Inline help tidak tersedia saat ini.**\n"
                f"{gear_emoji} Menampilkan menu bantuan standar.\n\n"
            )

    if fallback_prefix is None:
        if assistant_username:
            fallback_prefix = (
                f"{warning_emoji} **Tidak dapat menampilkan inline help.**\n"
                f"{gear_emoji} Menampilkan menu bantuan standar.\n\n"
            )
        else:
            fallback_prefix = (
                f"{warning_emoji} **Assistant bot belum dikonfigurasi.**\n"
                f"{gear_emoji} Set `ASSISTANT_BOT_USERNAME` untuk mengaktifkan inline help.\n\n"
            )

    fallback_text = fallback_prefix + build_sudoer_help_text(vz_emoji, event.sender_id)
    await vz_client.edit_with_premium_emoji(fallback_target, fallback_text)

# ============================================================================
# HELPRO COMMAND (DEVELOPERS ONLY)
# ============================================================================

@events.register(events.NewMessage(pattern=r'^\.helpro$', outgoing=True))
async def helpro_handler(event):
    global vz_client, vz_emoji

    """
    .helpro - Show developer command help (DEVELOPERS ONLY)

    Displays all commands including developer-exclusive commands:
    - All sudoers commands
    - Developer commands (.vzoel, .dp, .cr, .out, .sdb, .sgd)
    - Sudo prefix commands (.s*)
    """
    user_id = event.sender_id

    # Check if user is developer
    if not config.is_developer(user_id):
        merah_emoji = vz_emoji.getemoji('merah')
        await vz_client.edit_with_premium_emoji(event, f"{merah_emoji} **Access Denied!** Developer only command.")
        return

    # Get emojis
    main_emoji = vz_emoji.getemoji('utama')
    petir_emoji = vz_emoji.getemoji('petir')
    robot_emoji = vz_emoji.getemoji('robot')
    gear_emoji = vz_emoji.getemoji('gear')
    dev_emoji = vz_emoji.getemoji('developer')

    # Count total commands
    total_commands = count_total_commands(is_developer=True)

    # Build help text
    help_text = f"""{main_emoji} **VZ ASSISTANT - DEVELOPER HELP**

{petir_emoji} **Total Commands:** {total_commands}
{dev_emoji} **Role:** DEVELOPER
{gear_emoji} **Prefix:** {config.DEFAULT_PREFIX}

"""

    # Add all sudoers command categories
    help_text += f"**{robot_emoji} SUDOERS COMMANDS:**\n"
    for category, commands in SUDOERS_COMMANDS.items():
        help_text += f"\n**{petir_emoji} {category}:**\n"
        for cmd_name, cmd_data in commands.items():
            help_text += f"• `{cmd_data['cmd']}` - {cmd_data['desc']}\n"

    # Add developer command categories
    help_text += f"\n**{dev_emoji} DEVELOPER EXCLUSIVE COMMANDS:**\n"
    for category, commands in DEVELOPER_COMMANDS.items():
        help_text += f"\n**{petir_emoji} {category}:**\n"
        for cmd_name, cmd_data in commands.items():
            help_text += f"• `{cmd_data['cmd']}` - {cmd_data['desc']}\n"

    help_text += f"""
{gear_emoji} **Privilege:** Full system access
{robot_emoji} **Control:** All sudoer sessions

{robot_emoji} Plugins Digunakan: **HELP**
{petir_emoji} by {main_emoji} {config.RESULT_FOOTER}
"""

    await vz_client.edit_with_premium_emoji(event, help_text)

print("✅ Plugin loaded: help.py")
