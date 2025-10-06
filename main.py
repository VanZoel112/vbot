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
import subprocess
import signal
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

async def send_startup_log(client: VZClient, plugin_count: int):
    """Send startup notification to log group."""
    if not config.LOG_GROUP_ID:
        return

    try:
        role = "DEVELOPER" if client.is_developer else "SUDOER"
        startup_msg = f"""
🚀 **VZ ASSISTANT DEPLOYED**

👤 **User:** {client.me.first_name} (@{client.me.username})
🆔 **ID:** `{client.me.id}`
🔑 **Role:** {role}
📝 **Prefix:** `{client.get_prefix()}`
📦 **Plugins:** {plugin_count}
🕐 **Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

✅ Bot is now running and ready!
"""
        await client.client.send_message(config.LOG_GROUP_ID, startup_msg)
        logger.info("Sent startup notification to log group")
        print("✅ Startup notification sent to log group")

    except Exception as e:
        logger.error(f"Failed to send startup log: {e}")
        print(f"⚠️  Could not send startup log: {e}")


async def setup_log_handler(client: VZClient):
    """Setup comprehensive log handler to send logs to LOG_GROUP_ID."""
    logger.info("Setting up log handler...")

    if not config.LOG_GROUP_ID:
        logger.warning("LOG_GROUP_ID not configured - logs will only be in local files")
        print("⚠️  LOG_GROUP_ID not configured - logs will only be in terminal")
        return

    @events.register(events.NewMessage(outgoing=True))
    async def command_log_handler(event):
        """Log all outgoing commands to log group."""
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
📝 **Command Executed**

👤 **User:** {client.me.first_name} (@{client.me.username})
💬 **Chat:** {chat_name} (`{event.chat_id}`)
⚡ **Command:** `{event.text}`
🕐 **Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

            # Send to log group
            await client.client.send_message(config.LOG_GROUP_ID, log_msg)

        except Exception as e:
            logger.error(f"Command log handler error: {e}", exc_info=True)

    @events.register(events.NewMessage(incoming=True))
    async def mention_log_handler(event):
        """Log all mentions to log group."""
        try:
            # Skip if message is from log group itself
            if event.chat_id == config.LOG_GROUP_ID:
                return

            # Check if we are mentioned
            if not event.text:
                return

            me_username = client.me.username
            if not me_username:
                return

            # Check for @username or text mention
            mentioned = (
                f"@{me_username}" in event.text or
                (event.message.entities and any(
                    hasattr(e, 'user_id') and e.user_id == client.me.id
                    for e in event.message.entities
                ))
            )

            if not mentioned:
                return

            # Get sender and chat info
            sender = await event.get_sender()
            chat = await event.get_chat()

            sender_name = getattr(sender, 'first_name', 'Unknown')
            sender_username = getattr(sender, 'username', None)
            chat_name = getattr(chat, 'title', None) or getattr(chat, 'first_name', 'Unknown')

            # Log to local file
            logger.info(f"Mention from: {sender_name} (@{sender_username}) in {chat_name}")

            # Build log message
            log_msg = f"""
🔔 **Mentioned**

👤 **From:** {sender_name} {f'(@{sender_username})' if sender_username else ''}
💬 **Chat:** {chat_name} (`{event.chat_id}`)
📨 **Message:** {event.text[:200]}{'...' if len(event.text) > 200 else ''}
🕐 **Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

            # Send to log group
            await client.client.send_message(config.LOG_GROUP_ID, log_msg)

        except Exception as e:
            logger.error(f"Mention log handler error: {e}", exc_info=True)

    # Add handlers to client
    client.client.add_event_handler(command_log_handler)
    client.client.add_event_handler(mention_log_handler)

    logger.info(f"Log handlers configured - sending to group {config.LOG_GROUP_ID}")
    print(f"✅ Log handlers configured - commands, mentions → group {config.LOG_GROUP_ID}")


async def setup_error_handler(client: VZClient):
    """Setup global error handler to log all errors to log group."""
    if not config.LOG_GROUP_ID:
        return

    import traceback as tb

    async def send_error_log(error_msg: str):
        """Send error log to log group."""
        try:
            await client.client.send_message(config.LOG_GROUP_ID, error_msg)
        except Exception as e:
            logger.error(f"Failed to send error log: {e}")

    # Monkey-patch client to catch all errors
    original_handle_update = client.client._handle_update

    async def handle_update_with_error_logging(update):
        """Wrapper to catch and log all errors."""
        try:
            await original_handle_update(update)
        except Exception as e:
            # Log locally
            logger.error(f"Error handling update: {e}", exc_info=True)

            # Get traceback
            tb_lines = tb.format_exception(type(e), e, e.__traceback__)
            tb_text = ''.join(tb_lines)

            # Build error message
            error_msg = f"""
❌ **ERROR OCCURRED**

⚠️ **Error Type:** `{type(e).__name__}`
📝 **Error Message:** `{str(e)}`

**Traceback:**
```python
{tb_text[:3000]}
```

🕐 **Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

            # Send to log group
            await send_error_log(error_msg)

            # Re-raise to maintain normal error flow
            raise

    client.client._handle_update = handle_update_with_error_logging

    logger.info("Global error handler configured")
    print("✅ Error handler configured - all errors → log group")

# ============================================================================
# ASSISTANT BOT PROCESS MANAGEMENT
# ============================================================================

def start_assistant_bot():
    """Start assistant bot as subprocess."""
    try:
        # Check if already running
        result = subprocess.run(
            ["pgrep", "-f", "assistant_bot_pyrogram.py"],
            capture_output=True,
            text=True
        )

        if result.stdout.strip():
            logger.info("Assistant bot already running, skipping start")
            print("ℹ️  Assistant bot already running")
            return None

        # Start assistant bot
        logger.info("Starting assistant bot subprocess...")
        process = subprocess.Popen(
            ["python3", "assistant_bot_pyrogram.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True  # Isolate from parent process
        )

        # Wait a moment to check if it started successfully
        import time
        time.sleep(2)

        if process.poll() is None:
            logger.info(f"Assistant bot started successfully (PID: {process.pid})")
            print(f"✅ Assistant bot started (PID: {process.pid})")
            return process
        else:
            stdout, stderr = process.communicate()
            logger.error(f"Assistant bot failed to start: {stderr.decode()}")
            print(f"❌ Assistant bot failed to start")
            return None

    except Exception as e:
        logger.error(f"Error starting assistant bot: {e}")
        print(f"⚠️  Could not start assistant bot: {e}")
        return None

def stop_assistant_bot(process):
    """Stop assistant bot subprocess gracefully."""
    if process and process.poll() is None:
        try:
            logger.info("Stopping assistant bot...")
            print("🛑 Stopping assistant bot...")

            # Send SIGTERM for graceful shutdown
            process.terminate()

            # Wait up to 5 seconds for graceful shutdown
            try:
                process.wait(timeout=5)
                logger.info("Assistant bot stopped gracefully")
                print("✅ Assistant bot stopped")
            except subprocess.TimeoutExpired:
                # Force kill if still running
                logger.warning("Assistant bot did not stop gracefully, forcing...")
                process.kill()
                process.wait()
                logger.info("Assistant bot force stopped")
                print("⚠️  Assistant bot force stopped")

        except Exception as e:
            logger.error(f"Error stopping assistant bot: {e}")
            print(f"⚠️  Error stopping assistant bot: {e}")

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

    # Track assistant bot process for cleanup
    assistant_bot_process = None

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

        # Setup log group (auto-create if needed)
        print("\n📋 Setting up Log Group...")
        from helpers.log_group import setup_log_group
        await setup_log_group(main_client.client)

        # Reload LOG_GROUP_ID from environment (in case it was just created)
        log_group_id_str = os.getenv("LOG_GROUP_ID")
        if log_group_id_str:
            try:
                config.LOG_GROUP_ID = int(log_group_id_str)
            except ValueError:
                config.LOG_GROUP_ID = None

        # Setup log handler
        print("\n📋 Configuring Logging...")
        await setup_log_handler(main_client)

        # Setup error handler
        print("📋 Configuring Error Handler...")
        await setup_error_handler(main_client)

        # Setup assistant bot (auto-create if needed)
        print("\n🤖 Setting up Assistant Bot...")
        from helpers.botfather import setup_assistant_bot
        await setup_assistant_bot(main_client.client)

        # Start assistant bot subprocess
        print("\n🚀 Starting Assistant Bot...")
        assistant_bot_process = start_assistant_bot()

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

        # Send startup notification to log group
        await send_startup_log(main_client, plugin_count)

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

        # Stop assistant bot
        stop_assistant_bot(assistant_bot_process)

        # Stop all clients
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
