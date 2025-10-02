"""
VZ ASSISTANT v0.0.0.69
Sudo Command Handler

Allows developers to execute sudoer commands with 's' prefix

2025© Vzoel Fox's Lutpan
Founder & DEVELOPER : @VZLfxs
"""

import config
from telethon import events
import re

# ============================================================================
# SUDO COMMAND MAPPER
# ============================================================================

class SudoCommandHandler:
    """Handle sudo command execution for developers."""

    # Map of sudo commands to their actual command handlers
    COMMAND_MAP = {
        'sgcast': 'gcast',
        'sbl': 'bl',
        'sdbl': 'dbl',
        'stag': 'tag',
        'sstag': 'stag',
        'slock': 'lock',
        'sunlock': 'unlock',
        'sid': 'id',
        'sgetfileid': 'getfileid',
        'sping': 'ping',
        'spink': 'pink',
        'spong': 'pong',
        'slimit': 'limit',
        'salive': 'alive',
        'sjoinvc': 'joinvc',
        'sleavevc': 'leavevc',
        'sget': 'get',
        'ssetget': 'setget',
        'sgetqr': 'getqr',
        'spmon': 'pmon',
        'spmoff': 'pmoff',
        'ssetpm': 'setpm',
        'shelp': 'help',
        'sadmin': 'admin',
        'sunadmin': 'unadmin',
        'sprefix': 'prefix',
        'sshowjson': 'showjson'
    }

    def __init__(self, client):
        """Initialize sudo handler."""
        self.client = client

    @staticmethod
    def is_sudo_command(text):
        """Check if message is a sudo command."""
        if not text:
            return False

        # Check if starts with any prefix + 's' + command
        prefix = config.DEFAULT_PREFIX
        pattern = f"^{re.escape(prefix)}s[a-z]+"

        return bool(re.match(pattern, text))

    @staticmethod
    def parse_sudo_command(text):
        """
        Parse sudo command and return actual command.

        Examples:
            .sgcast Hello -> (.gcast, Hello)
            .sping -> (.ping, None)
            .stag reply -> (.tag, reply)
        """
        prefix = config.DEFAULT_PREFIX

        # Remove prefix
        if not text.startswith(prefix):
            return None, None

        text = text[len(prefix):]

        # Check if starts with 's'
        if not text.startswith('s'):
            return None, None

        # Split command and args
        parts = text.split(maxsplit=1)
        sudo_cmd = parts[0]  # e.g., 'sgcast'
        args = parts[1] if len(parts) > 1 else None

        # Map to actual command
        actual_cmd = SudoCommandHandler.COMMAND_MAP.get(sudo_cmd)

        if actual_cmd:
            return actual_cmd, args
        else:
            # Try removing 's' prefix
            possible_cmd = sudo_cmd[1:]  # Remove 's'
            return possible_cmd, args

    async def execute_sudo_command(self, event, command, args=None):
        """
        Execute command as if it was a sudoer command.

        Args:
            event: Telegram event
            command: Actual command name (without prefix)
            args: Command arguments
        """
        # Build the command text
        prefix = config.DEFAULT_PREFIX
        cmd_text = f"{prefix}{command}"
        if args:
            cmd_text += f" {args}"

        # Create a fake message event with the actual command
        # This will trigger the real command handler

        # Edit the message to show what's being executed
        await event.edit(f"⚡ **Sudo Executing:** `{cmd_text}`")

        # Note: Actual execution requires event simulation
        # For now, we'll just show info
        # TODO: Implement proper event forwarding to command handlers

        return True

# ============================================================================
# SUDO COMMAND INFO
# ============================================================================

def get_sudo_help():
    """Get help text for sudo commands."""
    return f"""
🔐 **SUDO COMMAND SYSTEM**

**📝 Usage:**
Prefix any sudoer command with 's' to execute as developer

**Examples:**
```
.sgcast Hello       → Execute .gcast as sudo
.sping              → Execute .ping as sudo
.stag Message       → Execute .tag as sudo
.slock @user        → Execute .lock as sudo
```

**✅ Available Sudo Commands:**
All sudoer commands can be executed with 's' prefix:
• `.sgcast` - Sudo broadcast
• `.stag` - Sudo tag all
• `.slock` / `.sunlock` - Sudo lock management
• `.sping` / `.spink` / `.spong` - Sudo ping commands
• `.shelp` - Sudo help menu
• And all other sudoer commands...

**💡 Purpose:**
Allows developers to test sudoer commands
without switching accounts or losing privileges.

**⚠️ Note:**
Sudo commands inherit developer permissions
but execute as sudoer-level commands.

{config.BRANDING_FOOTER} SUDO
Founder & DEVELOPER : {config.FOUNDER_USERNAME}
"""

# ============================================================================
# SUDO DECORATOR
# ============================================================================

def handle_sudo_prefix(func):
    """
    Decorator to handle sudo prefix for commands.

    Allows developers to run command with 's' prefix.
    """
    async def wrapper(event):
        # Check if this is a sudo call
        if event.text and event.text.startswith(f"{config.DEFAULT_PREFIX}s"):
            # Only allow for developers
            if not config.is_developer(event.sender_id):
                return

            # Parse the sudo command
            handler = SudoCommandHandler(event.client)
            actual_cmd, args = handler.parse_sudo_command(event.text)

            if actual_cmd:
                # Mark that this is a sudo execution
                event._is_sudo = True
                event._sudo_args = args

        # Execute the original function
        return await func(event)

    return wrapper

print("✅ Sudo Command Handler Loaded")
