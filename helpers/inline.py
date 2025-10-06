"""
VZ ASSISTANT v0.0.0.69
Inline Button Helper

2025© Vzoel Fox's Lutpan
Founder & DEVELOPER : @VZLfxs
"""

from telethon import Button, events
from telethon.tl.types import KeyboardButtonCallback
import json
import config

# ============================================================================
# INLINE BOT MANAGER
# ============================================================================

class InlineManager:
    """Manage inline buttons for VZ ASSISTANT."""

    def __init__(self, client):
        """Initialize inline manager."""
        self.client = client
        self.bot = None
        self.callbacks = {}

    async def init_bot(self, bot_token=None):
        """Initialize inline bot if available."""
        if bot_token:
            from telethon import TelegramClient
            self.bot = TelegramClient('inline_bot', config.API_ID, config.API_HASH)
            await self.bot.start(bot_token=bot_token)
            print("✅ Inline bot initialized")
        else:
            print("⚠️  No inline bot token provided, using text-based interface")

    def create_button(self, text, callback_data=None, url=None):
        """Create an inline button."""
        if url:
            return Button.url(text, url)
        elif callback_data:
            return Button.inline(text, data=callback_data.encode('utf-8'))
        else:
            return Button.inline(text)

    def create_button_row(self, buttons):
        """Create a row of buttons."""
        return buttons

    async def send_with_buttons(self, chat_id, message, buttons, **kwargs):
        """Send message with inline buttons."""
        try:
            # Try using bot if available
            if self.bot:
                return await self.bot.send_message(
                    chat_id,
                    message,
                    buttons=buttons,
                    **kwargs
                )
            else:
                # Fallback to client
                return await self.client.send_message(
                    chat_id,
                    message,
                    buttons=buttons,
                    **kwargs
                )
        except Exception as e:
            # If buttons fail, send without buttons
            print(f"⚠️  Failed to send buttons: {e}")
            return await self.client.send_message(chat_id, message, **kwargs)

    async def edit_with_buttons(self, message, text, buttons, **kwargs):
        """Edit message with inline buttons."""
        try:
            return await message.edit(text, buttons=buttons, **kwargs)
        except Exception as e:
            print(f"⚠️  Failed to edit with buttons: {e}")
            return await message.edit(text, **kwargs)

    def register_callback(self, callback_id, handler):
        """Register callback handler."""
        self.callbacks[callback_id] = handler

    async def handle_callback(self, event):
        """Handle button callback."""
        callback_data = event.data.decode('utf-8')
        if callback_data in self.callbacks:
            await self.callbacks[callback_data](event)

# ============================================================================
# PREDEFINED BUTTON SETS
# ============================================================================

def get_alive_buttons():
    """Get buttons for .alive command (compact)."""
    return [
        [
            Button.inline("📋 Help", b"cmd_help"),
            Button.url("👨‍💻 Dev", "https://t.me/VZLfxs")
        ]
    ]

def get_help_main_buttons(categories):
    """Get main help menu buttons."""
    buttons = []

    # Create category buttons (2 per row)
    row = []
    for i, category in enumerate(categories):
        row.append(Button.inline(category, f"help_cat_{category}".encode('utf-8')))
        if len(row) == 2 or i == len(categories) - 1:
            buttons.append(row)
            row = []

    # Add close button (compact)
    buttons.append([Button.inline("❌", b"help_close")])

    return buttons

def get_help_category_buttons(category, commands):
    """Get buttons for a specific category (compact)."""
    buttons = []

    # Create command buttons
    for cmd in commands:
        buttons.append([Button.inline(f"• {cmd}", f"help_cmd_{cmd}".encode('utf-8'))])

    # Add back and close buttons (compact)
    buttons.append([
        Button.inline("◀️", b"help_back"),
        Button.inline("❌", b"help_close")
    ])

    return buttons

def get_help_command_buttons():
    """Get buttons for command detail view (compact)."""
    return [
        [
            Button.inline("◀️", b"help_back"),
            Button.inline("🏠", b"help_home"),
            Button.inline("❌", b"help_close")
        ]
    ]

def get_showjson_buttons():
    """Get buttons for .showjson command (compact)."""
    return [
        [
            Button.inline("📊", b"json_metrics"),
            Button.inline("🎨", b"json_emojis"),
            Button.inline("📄", b"json_fileids")
        ],
        [
            Button.inline("⚙️", b"json_settings"),
            Button.inline("❌", b"json_close")
        ]
    ]

def get_payment_buttons():
    """Get buttons for payment command (compact)."""
    return [
        [
            Button.inline("💳", b"pay_ewallet"),
            Button.inline("🏦", b"pay_bank"),
            Button.inline("📱", b"pay_qr")
        ],
        [Button.inline("❌", b"pay_close")]
    ]

def get_admin_buttons(user_id):
    """Get admin management buttons (compact)."""
    return [
        [
            Button.inline("✅", f"admin_promote_{user_id}".encode('utf-8')),
            Button.inline("❌", f"admin_demote_{user_id}".encode('utf-8')),
            Button.inline("🚫", b"admin_close")
        ]
    ]

def get_pm_permit_buttons():
    """Get PM permit approval buttons (compact)."""
    return [
        [
            Button.inline("✅", b"pm_approve"),
            Button.inline("🚫", b"pm_block"),
            Button.inline("📝", b"pm_report")
        ]
    ]

# ============================================================================
# CALLBACK QUERY BUILDER
# ============================================================================

class CallbackQuery:
    """Build callback query data."""

    @staticmethod
    def build(action, **kwargs):
        """Build callback data string."""
        data = {"action": action}
        data.update(kwargs)
        return json.dumps(data)

    @staticmethod
    def parse(data):
        """Parse callback data."""
        try:
            if isinstance(data, bytes):
                data = data.decode('utf-8')
            return json.loads(data)
        except:
            return {"action": data}

# ============================================================================
# INLINE KEYBOARD BUILDER
# ============================================================================

class KeyboardBuilder:
    """Build inline keyboards easily."""

    def __init__(self):
        """Initialize keyboard builder."""
        self.rows = []

    def add_button(self, text, callback_data=None, url=None, same_row=False):
        """Add button to keyboard."""
        if url:
            button = Button.url(text, url)
        elif callback_data:
            button = Button.inline(text, data=callback_data.encode('utf-8') if isinstance(callback_data, str) else callback_data)
        else:
            button = Button.inline(text)

        if same_row and self.rows:
            self.rows[-1].append(button)
        else:
            self.rows.append([button])

        return self

    def add_row(self, *buttons):
        """Add a row of buttons."""
        self.rows.append(list(buttons))
        return self

    def build(self):
        """Build the keyboard."""
        return self.rows

    def clear(self):
        """Clear all buttons."""
        self.rows = []
        return self

print("✅ Inline Helper Loaded")
