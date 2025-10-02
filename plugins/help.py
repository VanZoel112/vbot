"""
VZ ASSISTANT v0.0.0.69
Help Plugin - Command Documentation & Navigation

2025© Vzoel Fox's Lutpan
Founder & DEVELOPER : @VZLfxs
"""

from telethon import events, Button
import config
from utils.animation import animate_loading
from helpers.inline import KeyboardBuilder

# Global variables (set by main.py)
vz_client = None
vz_emoji = None

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

async def show_help_menu(event, is_developer=False):
    global vz_client, vz_emoji

    """Show main help menu."""
    categories = get_all_categories(is_developer)
    total_commands = count_total_commands(is_developer)

    help_text = f"""
📚 **VZ ASSISTANT - HELP MENU**

🔍 **Total Commands:** {total_commands}
👤 **Role:** {'DEVELOPER' if is_developer else 'SUDOER'}
📝 **Prefix:** {config.DEFAULT_PREFIX}

**📂 Categories:**
Select a category to view commands

{gear_emoji} Plugins Digunakan: **HELP**
{petir_emoji} by {main_emoji} Vzoel Fox's Lutpan
"""

    # Create category buttons
    kb = KeyboardBuilder()

    # Add category buttons (2 per row)
    for i, category in enumerate(categories):
        same_row = (i % 2 == 1)
        kb.add_button(f"📁 {category}", f"help_cat_{category}", same_row=same_row)

    # Add close button
    kb.add_button("❌ Close", "help_close")

    buttons = kb.build()

    # Send or edit message
    try:
        if hasattr(event, 'edit'):
            await event.edit(help_text, buttons=buttons)
        else:
            await event.respond(help_text, buttons=buttons)
    except Exception as e:
        # Fallback without buttons
        if hasattr(event, 'edit'):
            await vz_client.edit_with_premium_emoji(event, help_text)
        else:
            await event.respond(help_text)

# ============================================================================
# CALLBACK HANDLERS
# ============================================================================

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

    # Build category view
    category_text = f"""
📁 **{category} Commands**

**Available commands in this category:**

"""

    for cmd_name, cmd_data in commands.items():
        category_text += f"• `{cmd_data['cmd']}` - {cmd_data['desc']}\n"

    category_text += f"""

💡 **Tip:** Click a command for detailed info

{gear_emoji} Plugins Digunakan: **HELP**
{petir_emoji} by {main_emoji} Vzoel Fox's Lutpan"""

    # Create command buttons
    kb = KeyboardBuilder()

    for cmd_name in commands.keys():
        kb.add_button(f"📝 {cmd_name}", f"help_cmd_{category}_{cmd_name}")

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

    # Build command detail view
    cmd_text = f"""
📝 **Command Details**

**Command:** `{cmd_data['cmd']}`
**Description:** {cmd_data['desc']}

**Usage:**
`{cmd_data['usage']}`

**Example:**
`{cmd_data['example']}`

📂 **Category:** {category}

{gear_emoji} Plugins Digunakan: **HELP**
{petir_emoji} by {main_emoji} Vzoel Fox's Lutpan"""

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

    await show_help_menu(event, is_developer)
    await event.answer()

@events.register(events.CallbackQuery(pattern=b"help_home"))
async def help_home_callback(event):
    global vz_client, vz_emoji

    """Handle home button."""
    user_id = event.sender_id
    is_developer = config.is_developer(user_id)

    await show_help_menu(event, is_developer)
    await event.answer("🏠 Returning to main menu...")

@events.register(events.CallbackQuery(pattern=b"help_close"))
async def help_close_callback(event):
    global vz_client, vz_emoji

    """Handle close button."""
    await event.delete()
    await event.answer("✅ Help menu closed")

print("✅ Plugin loaded: help.py")
