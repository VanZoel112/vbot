#!/usr/bin/env python3
"""
VZ ASSISTANT v0.0.0.69
Main Entry Point

2025© Vzoel Fox's Lutpan
Founder & DEVELOPER : @VZLfxs
"""

import asyncio
import sys
import os
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import modules
import config
from client import VZClient, MultiClientManager
from database.models import DatabaseManager
from helpers import load_plugins, logger, log_event, log_exception
from telethon import events

# ============================================================================
# ASCII ART BANNER
# ============================================================================

BANNER = f"""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║              VZ ASSISTANT v{config.BOT_VERSION}                      ║
║              Telethon × Python 3+                        ║
║                                                          ║
║              {config.BRANDING_FOOTER}                    ║
║              Founder & DEVELOPER : {config.FOUNDER_USERNAME}               ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝

🚀 Starting VZ ASSISTANT...
"""

# ============================================================================
# LOG HANDLER
# ============================================================================

async def setup_log_handler(client: VZClient):
    """Setup log handler to send logs to LOG_GROUP_ID."""
    logger.info("Setting up log handler...")

    if not config.LOG_GROUP_ID:
        logger.warning("LOG_GROUP_ID not configured - logs will only be in local files")
        print("⚠️  LOG_GROUP_ID not configured - logs will only be in terminal")
        return

    @events.register(events.NewMessage(outgoing=True))
    async def log_handler(event):
        """Log all outgoing messages to log group."""
        try:
            # Skip if message is from log group itself
            if event.chat_id == config.LOG_GROUP_ID:
                return

            # Skip if not a command
            prefix = client.get_prefix()
            if not event.text or not event.text.startswith(prefix):
                return

            # Extract command
            cmd = event.text.split()[0][len(prefix):]

            # Get chat info
            chat = await event.get_chat()
            chat_name = getattr(chat, 'title', None) or getattr(chat, 'first_name', 'Unknown')

            # Log to local file
            logger.info(f"Command: {event.text} | User: {client.me.username} | Chat: {chat_name}")

            # Build log message
            log_msg = f"""
📝 **Command Log**

👤 User: {client.me.first_name} (@{client.me.username})
💬 Chat: {chat_name} (`{event.chat_id}`)
⚡ Command: `{event.text}`
🕐 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

            # Send to log group
            await client.client.send_message(config.LOG_GROUP_ID, log_msg)
            logger.debug(f"Sent log to group {config.LOG_GROUP_ID}")

        except Exception as e:
            logger.error(f"Log handler error: {e}", exc_info=True)
            print(f"❌ Log handler error: {e}")

    # Add handler to client
    client.client.add_event_handler(log_handler)
    logger.info(f"Log handler configured - sending to group {config.LOG_GROUP_ID}")
    print(f"✅ Log handler configured - sending to group {config.LOG_GROUP_ID}")

# ============================================================================
# MAIN FUNCTION
# ============================================================================

async def main():
    """Main application function."""
    print(BANNER)
    logger.info("="*60)
    logger.info("VZ ASSISTANT Starting...")
    logger.info("="*60)

    # Print log file location
    print(f"\n📁 Logs Directory: {logger.log_dir}")
    print(f"📄 Main Log: {logger.get_log_path()}")
    print(f"❌ Error Log: {logger.get_error_log_path()}")
    print(f"⚡ Command Log: {logger.get_command_log_path()}\n")

    # Check for session string
    print("🔐 Session Configuration")
    print("="*60)
    logger.info("Checking session configuration...")

    session_string = os.getenv("SESSION_STRING")

    if not session_string:
        logger.warning("No SESSION_STRING found in environment variables")
        print("⚠️  No SESSION_STRING found in environment variables")
        print("\nOptions:")
        print("  1. Run stringgenerator.py to create a session")
        print("  2. Set SESSION_STRING environment variable")
        print("  3. Enter session string now (press Enter to skip)")
        print()

        session_input = input("Enter session string (or press Enter to exit): ").strip()

        if not session_input:
            logger.info("No session string provided. Exiting...")
            print("\n❌ No session string provided. Exiting...")
            return

        session_string = session_input

    # Initialize client manager
    print("\n🔧 Initializing Client Manager...")
    logger.info("Initializing client manager...")
    manager = MultiClientManager()

    try:
        # Add main client
        print("📡 Connecting to Telegram...")
        logger.info("Connecting to Telegram...")
        main_client = await manager.add_client(session_string)
        logger.info(f"Connected as: {main_client.me.first_name} (@{main_client.me.username})")

        # Set global variables for plugins BEFORE loading them
        import builtins
        builtins.vz_client = main_client
        builtins.vz_emoji = main_client.emoji
        builtins.manager = manager  # For broadcast middleware
        logger.info("Global variables set: vz_client, vz_emoji, manager")

        # Setup log handler
        print("\n📋 Configuring Logging...")
        await setup_log_handler(main_client)

        # Load plugins with event registration
        print("\n📦 Loading Plugins...")
        logger.info("Loading plugins...")
        plugin_count = load_plugins(main_client)

        # Inject globals into all loaded plugin modules
        import sys
        for module_name in list(sys.modules.keys()):
            if module_name.startswith('plugins.'):
                module = sys.modules[module_name]
                if hasattr(module, 'vz_client'):
                    module.vz_client = main_client
                if hasattr(module, 'vz_emoji'):
                    module.vz_emoji = main_client.emoji
                if hasattr(module, 'manager'):
                    module.manager = manager
        logger.info("Injected globals into all plugin modules")

        print("\n" + "="*60)
        print("✅ VZ ASSISTANT Started Successfully!")
        print("="*60)
        print(f"👤 User: {main_client.me.first_name}")
        print(f"🆔 ID: {main_client.me.id}")
        print(f"🔑 Role: {'DEVELOPER' if main_client.is_developer else 'SUDOER'}")
        print(f"📝 Prefix: {main_client.get_prefix()}")
        print(f"📦 Plugins: {plugin_count}")
        print("="*60)

        logger.info("VZ ASSISTANT started successfully")
        logger.info(f"User: {main_client.me.first_name} (ID: {main_client.me.id})")
        logger.info(f"Role: {'DEVELOPER' if main_client.is_developer else 'SUDOER'}")
        logger.info(f"Loaded {plugin_count} plugins")

        # Keep running
        print("\n🔄 Bot is now running... (Press Ctrl+C to stop)")
        logger.info("Bot is now running and listening for events...")
        await main_client.client.run_until_disconnected()

    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
        print("\n\n⚠️  Stopping VZ ASSISTANT...")
    except Exception as e:
        logger.critical(f"Fatal error in main: {e}", exc_info=True)
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        logger.info("Shutting down...")
        print("\n🛑 Shutting down...")
        await manager.stop_all()
        logger.info("VZ ASSISTANT stopped")
        print("👋 Goodbye!")

# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    # Use uvloop for better performance (vzl2 style)
    try:
        import uvloop
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        print("⚡ uvloop enabled for performance boost")
    except ImportError:
        print("⚠️  uvloop not installed - using default asyncio")
        pass

    try:
        # Check Python version
        if sys.version_info < (3, 9):
            print("❌ Python 3.9+ is required!")
            sys.exit(1)

        # Run main function
        asyncio.run(main())

    except KeyboardInterrupt:
        print("\n\n⚠️  Process interrupted by user")
    except Exception as e:
        print(f"\n❌ Fatal Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
