"""
VZ ASSISTANT v0.0.0.69
Telethon Client Manager

2025© Vzoel Fox's Lutpan
Founder & DEVELOPER : @VZLfxs
"""

from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.types import MessageEntityCustomEmoji
import asyncio
import os
import sys
import time
from datetime import datetime

# Import config and database
import config
from database.models import DatabaseManager, MultiUserDatabaseManager
from helpers.vz_emoji_manager import VZEmojiManager
from utils.emoji import build_combined_entities

# ============================================================================
# VZ CLIENT CLASS
# ============================================================================

class VZClient:
    """Enhanced Telethon client for VZ ASSISTANT."""

    def __init__(self, session_string: str = None, user_id: int = None):
        """Initialize VZ Client."""
        self.user_id = user_id
        self.start_time = time.time()

        # Initialize client
        if session_string:
            self.client = TelegramClient(
                StringSession(session_string),
                config.API_ID,
                config.API_HASH
            )
        else:
            # Use file-based session for first time
            session_name = f"vz_session_{user_id}" if user_id else "vz_session"
            session_path = os.path.join(config.SESSION_DIR, session_name)
            self.client = TelegramClient(
                session_path,
                config.API_ID,
                config.API_HASH
            )

        # Database manager
        if user_id:
            self.db = DatabaseManager(config.get_sudoer_db_path(user_id))
        else:
            self.db = DatabaseManager(config.DEVELOPER_DB_PATH)

        # User info
        self.me = None
        self.is_developer = False

        # Emoji manager
        self.emoji = VZEmojiManager()

    async def start(self):
        """Start the client."""
        await self.client.start()

        # Get user info
        self.me = await self.client.get_me()
        self.user_id = self.me.id
        self.is_developer = config.is_developer(self.me.id)

        # Register user in database
        self.db.add_user(
            user_id=self.me.id,
            username=self.me.username,
            first_name=self.me.first_name,
            is_developer=self.is_developer,
            is_sudoer=not self.is_developer
        )

        print(f"✅ Client started for: {self.me.first_name} (@{self.me.username})")
        print(f"👤 User ID: {self.me.id}")
        print(f"🔑 Role: {'DEVELOPER' if self.is_developer else 'SUDOER'}")

        return self

    async def get_session_string(self) -> str:
        """Get session string for current client."""
        return self.client.session.save()

    def get_prefix(self) -> str:
        """Get user's command prefix."""
        return self.db.get_prefix(self.user_id)

    async def send_with_premium_emoji(self, chat_id, text: str, **kwargs):
        """Send message with premium emoji conversion using entities."""
        if not self.emoji.available:
            return await self.client.send_message(chat_id, text, **kwargs)

        # Build combined entities (markdown + premium emojis)
        cleaned_text, entities = build_combined_entities(text)

        # Always send with entities - even if empty (Telegram requirement)
        # Remove parse_mode if present as entities takes precedence
        if 'parse_mode' in kwargs:
            del kwargs['parse_mode']

        return await self.client.send_message(
            chat_id,
            cleaned_text,
            formatting_entities=entities if entities else None,
            **kwargs
        )

    async def edit_with_premium_emoji(self, message, text: str, **kwargs):
        """Edit message with premium emoji conversion using entities."""
        if not self.emoji.available:
            return await message.edit(text, **kwargs)

        # Build combined entities (markdown + premium emojis)
        cleaned_text, entities = build_combined_entities(text)

        # Always edit with entities - even if empty (Telegram requirement)
        # Remove parse_mode if present as entities takes precedence
        if 'parse_mode' in kwargs:
            del kwargs['parse_mode']

        return await message.edit(
            cleaned_text,
            formatting_entities=entities if entities else None,
            **kwargs
        )

    def get_uptime(self) -> str:
        """Get bot uptime in human-readable format."""
        uptime_seconds = int(time.time() - self.start_time)

        days = uptime_seconds // 86400
        hours = (uptime_seconds % 86400) // 3600
        minutes = (uptime_seconds % 3600) // 60
        seconds = uptime_seconds % 60

        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        if seconds > 0 or not parts:
            parts.append(f"{seconds}s")

        return " ".join(parts)

    async def stop(self):
        """Stop the client."""
        if self.client.is_connected():
            await self.client.disconnect()
        self.db.close()
        print("❌ Client stopped")

# ============================================================================
# MULTI-CLIENT MANAGER
# ============================================================================

class MultiClientManager:
    """Manage multiple Telegram clients (Developer + Sudoers)."""

    def __init__(self):
        """Initialize multi-client manager."""
        self.clients = {}
        self.multi_db = MultiUserDatabaseManager(config.SUDOERS_DB_DIR)

    async def add_client(self, session_string: str, user_id: int = None) -> VZClient:
        """Add a new client."""
        vz_client = VZClient(session_string=session_string, user_id=user_id)
        await vz_client.start()

        self.clients[vz_client.user_id] = vz_client
        return vz_client

    async def add_client_from_file(self, session_name: str) -> VZClient:
        """Add client from session file."""
        vz_client = VZClient(user_id=None)
        await vz_client.start()

        self.clients[vz_client.user_id] = vz_client
        return vz_client

    def get_client(self, user_id: int) -> VZClient:
        """Get client by user ID."""
        return self.clients.get(user_id)

    async def remove_client(self, user_id: int):
        """Remove and stop a client."""
        if user_id in self.clients:
            await self.clients[user_id].stop()
            del self.clients[user_id]

    async def stop_all(self):
        """Stop all clients."""
        for client in self.clients.values():
            await client.stop()
        self.multi_db.close_all()

    def get_all_clients(self):
        """Get all active clients."""
        return self.clients.values()

    def get_sudoer_clients(self):
        """Get all sudoer clients (non-developers)."""
        return [client for client in self.clients.values() if not client.is_developer]

    async def broadcast_command(self, command_text: str, exclude_user_id: int = None):
        """
        Broadcast command to all sudoer clients.

        Args:
            command_text: The full command text to send (e.g., ".gcast Hello")
            exclude_user_id: Optional user ID to exclude from broadcast

        Returns:
            dict: Results from each client {user_id: success_bool}
        """
        results = {}
        sudoers = self.get_sudoer_clients()

        for client in sudoers:
            # Skip excluded user
            if exclude_user_id and client.user_id == exclude_user_id:
                continue

            try:
                # Send command to saved messages (or specified chat)
                await client.client.send_message(
                    'me',  # Send to self (saved messages)
                    command_text
                )
                results[client.user_id] = True
            except Exception as e:
                results[client.user_id] = False
                print(f"Failed to broadcast to {client.user_id}: {e}")

        return results

# ============================================================================
# COMMAND DECORATOR
# ============================================================================

def command(pattern: str, allow_sudoers: bool = True, allow_developers: bool = True):
    """Decorator for command handlers."""
    def decorator(func):
        async def wrapper(client: VZClient, event):
            # Get user prefix
            prefix = client.get_prefix()

            # Build pattern with prefix
            cmd_pattern = f"^{prefix}{pattern}"

            # Check if message matches
            if not event.text or not event.text.startswith(prefix):
                return

            # Extract command
            cmd = event.text.split()[0][len(prefix):]

            # Check permissions
            if client.is_developer and not allow_developers:
                return
            if not client.is_developer and not allow_sudoers:
                return

            # Log command
            args = event.text[len(prefix) + len(cmd):].strip()
            client.db.add_log(
                user_id=client.user_id,
                command=cmd,
                arguments=args,
                chat_id=event.chat_id
            )

            try:
                # Execute command
                await func(client, event)
            except Exception as e:
                # Log error
                client.db.add_log(
                    user_id=client.user_id,
                    command=cmd,
                    arguments=args,
                    chat_id=event.chat_id,
                    success=False,
                    error_message=str(e)
                )
                await event.reply(f"❌ Error: {str(e)}")

        return wrapper
    return decorator

print("✅ VZ Client Manager Loaded")
