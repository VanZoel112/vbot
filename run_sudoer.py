#!/usr/bin/env python3
"""
VZ ASSISTANT v0.0.0.69
Sudoer Runner - Individual User Instance

2025© Vzoel Fox's Lutpan
Founder & DEVELOPER : @VZLfxs

This script runs a single sudoer instance managed by PM2.
Each user gets their own process with isolated session.
"""

import asyncio
import sys
import os
from telethon import TelegramClient
from telethon.sessions import StringSession

# Import main bot components
import config
from client import VZClient, MultiClientManager
from database.models import DatabaseManager
from helpers.plugin_loader import load_plugins
from helpers.vz_emoji_manager import VZEmojiManager

# Check if user_id provided
if len(sys.argv) < 2:
    print("❌ Error: USER_ID not provided")
    print("Usage: python run_sudoer.py <user_id>")
    sys.exit(1)

user_id = int(sys.argv[1])

# Get session string from environment or database
session_string = os.getenv('SESSION_STRING')

if not session_string:
    # Try to load from sessions JSON
    import json
    json_file = "sessions/sudoer_sessions.json"

    if os.path.exists(json_file):
        with open(json_file, 'r') as f:
            sessions = json.load(f)
            for session in sessions.get('sessions', []):
                if session['user_id'] == user_id:
                    session_string = session['session_string']
                    break

    if not session_string:
        print(f"❌ No session found for user {user_id}")
        sys.exit(1)

async def main():
    """Run sudoer instance."""
    print(f"""
╔══════════════════════════════════════════════════════════╗
║              VZ ASSISTANT v{config.BOT_VERSION}                      ║
║              Sudoer Instance - User {user_id}
║                                                          ║
║              {config.BRANDING_FOOTER}                    ║
║              Founder & DEVELOPER : {config.FOUNDER_USERNAME}               ║
╚══════════════════════════════════════════════════════════╝

🤖 Starting Sudoer Instance for User {user_id}...
""")

    # Use uvloop for better performance
    try:
        import uvloop
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        print("🚀 Using uvloop for optimized performance")
    except ImportError:
        print("⚠️  uvloop not available, using standard asyncio")

    # Get database path
    db_path = config.get_sudoer_db_path(user_id)

    # Initialize database
    db = DatabaseManager(db_path)
    user = db.get_user(user_id)

    if not user:
        print(f"❌ User {user_id} not found in database")
        sys.exit(1)

    prefix = db.get_prefix(user_id) or config.DEFAULT_PREFIX
    db.close()

    print(f"✅ User: {user.first_name} (@{user.username or 'None'})")
    print(f"✅ Prefix: {prefix}")

    # Create Telegram client with session string
    client = TelegramClient(
        StringSession(session_string),
        config.API_ID,
        config.API_HASH
    )

    # Connect
    await client.start()
    me = await client.get_me()

    print(f"✅ Connected as: {me.first_name} ({me.id})")

    # Initialize VZClient wrapper
    global vz_client
    vz_client = VZClient(client, user_id, prefix)

    # Initialize emoji manager
    global vz_emoji
    vz_emoji = VZEmojiManager(config.EMOJI_PRIME_JSON)

    # Load plugins
    print("\n📦 Loading plugins...")
    loaded_plugins = load_plugins(client, vz_client, vz_emoji)
    print(f"✅ Loaded {len(loaded_plugins)} plugins")

    # Update last active
    db = DatabaseManager(db_path)
    db.update_last_active(user_id)
    db.close()

    print(f"\n✅ VZ Assistant running for {me.first_name}!")
    print(f"📱 User ID: {me.id}")
    print(f"🔑 Prefix: {prefix}")
    print(f"🔄 Process: vz-sudoer-{user_id}")
    print("\n⚡ Bot is active... (Managed by PM2)\n")

    # Run until disconnected
    await client.run_until_disconnected()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n\n⚠️  Sudoer instance {user_id} stopped")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
