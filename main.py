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
# LOAD PLUGINS
# ============================================================================

def load_plugins():
    """Load all plugins from plugins directory."""
    plugins_dir = os.path.join(os.path.dirname(__file__), "plugins")

    if not os.path.exists(plugins_dir):
        os.makedirs(plugins_dir)
        print(f"📁 Created plugins directory: {plugins_dir}")
        return 0

    plugin_count = 0
    for filename in os.listdir(plugins_dir):
        if filename.endswith(".py") and not filename.startswith("_"):
            try:
                # Import plugin
                plugin_name = filename[:-3]
                __import__(f"plugins.{plugin_name}")
                plugin_count += 1
                print(f"  ✅ Loaded: {plugin_name}")
            except Exception as e:
                print(f"  ❌ Failed to load {filename}: {e}")

    return plugin_count

# ============================================================================
# MAIN FUNCTION
# ============================================================================

async def main():
    """Main application function."""
    print(BANNER)

    # Load plugins
    print("\n📦 Loading Plugins...")
    plugin_count = load_plugins()
    print(f"\n✅ Loaded {plugin_count} plugins\n")

    # Check for session string
    print("🔐 Session Configuration")
    print("="*60)

    session_string = os.getenv("SESSION_STRING")

    if not session_string:
        print("⚠️  No SESSION_STRING found in environment variables")
        print("\nOptions:")
        print("  1. Run stringgenerator.py to create a session")
        print("  2. Set SESSION_STRING environment variable")
        print("  3. Enter session string now (press Enter to skip)")
        print()

        session_input = input("Enter session string (or press Enter to exit): ").strip()

        if not session_input:
            print("\n❌ No session string provided. Exiting...")
            return

        session_string = session_input

    # Initialize client manager
    print("\n🔧 Initializing Client Manager...")
    manager = MultiClientManager()

    try:
        # Add main client
        print("📡 Connecting to Telegram...")
        main_client = await manager.add_client(session_string)

        print("\n" + "="*60)
        print("✅ VZ ASSISTANT Started Successfully!")
        print("="*60)
        print(f"👤 User: {main_client.me.first_name}")
        print(f"🆔 ID: {main_client.me.id}")
        print(f"🔑 Role: {'DEVELOPER' if main_client.is_developer else 'SUDOER'}")
        print(f"📝 Prefix: {main_client.get_prefix()}")
        print(f"📦 Plugins: {plugin_count}")
        print("="*60)

        # Keep running
        print("\n🔄 Bot is now running... (Press Ctrl+C to stop)")
        await main_client.client.run_until_disconnected()

    except KeyboardInterrupt:
        print("\n\n⚠️  Stopping VZ ASSISTANT...")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n🛑 Shutting down...")
        await manager.stop_all()
        print("👋 Goodbye!")

# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
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
