"""
VZ ASSISTANT v0.0.0.69
Restart Plugin - Bot Restart Management

Commands:
- .restart - Restart bot (all roles)

2025© Vzoel Fox's Lutpan
Founder & DEVELOPER : @VZLfxs
"""

from telethon import events
import sys
import os
import config

# Global variables (set by main.py)
vz_client = None
vz_emoji = None

# ============================================================================
# RESTART COMMAND
# ============================================================================

@events.register(events.NewMessage(pattern=r'^\.restart$', outgoing=True))
async def restart_handler(event):
    """
    .restart - Full bot restart with complete reload

    Applies ALL code changes from:
    - GitHub updates (.pull) - NEW/UPDATED FILES
    - Plugin updates (new plugins, edited plugins)
    - Helper module updates (utils, database, etc)
    - .env configuration changes
    - config.py changes
    - JSON data files

    How it works:
    - os.execv() creates NEW Python process
    - All Python modules re-imported from disk
    - Fresh plugin loader reads all .py files
    - .env and config.py hot-reloaded before restart

    Preserved per user (file-based storage):
    - Blacklist groups (JSON)
    - Lock users (SQLite)
    - PM permit settings (SQLite)
    - Custom prefix (SQLite)
    - Custom logo (file)

    Available for all roles (USER, ADMIN, DEVELOPER).

    Usage:
        .restart

    After restart (ALL changes applied):
    - .env reloaded from disk
    - config.py reloaded from disk
    - plugins/*.py imported fresh from disk
    - helpers/*.py imported fresh from disk
    - All .py files reflect latest code
    - User data preserved from database/JSON
    """
    global vz_client, vz_emoji

    user_id = event.sender_id

    # Get user role for display
    user_role = config.get_user_role(user_id)
    role_emoji = config.get_role_emoji(user_role, vz_emoji)

    # Get emojis
    loading_emoji = vz_emoji.getemoji('loading')
    gear_emoji = vz_emoji.getemoji('gear')
    petir_emoji = vz_emoji.getemoji('petir')
    main_emoji = vz_emoji.getemoji('utama')
    nyala_emoji = vz_emoji.getemoji('nyala')

    restart_text = f"""
{loading_emoji} **Restarting VZ ASSISTANT...**

{role_emoji} **User:** {event.sender.first_name}
{gear_emoji} **Role:** {user_role}
{petir_emoji} **Action:** Full process restart

{nyala_emoji} **Applying ALL changes:**
• New/updated plugins
• Helper module updates
• .env configuration
• config.py settings
• All .py files from disk

{gear_emoji} **Preserved (file-based):**
• Blacklist groups
• Lock users
• PM permit settings
• Custom prefix & logo

{nyala_emoji} **Please wait...**
Creating fresh Python process...

{main_emoji} by {config.RESULT_FOOTER}
"""

    await vz_client.edit_with_premium_emoji(event, restart_text)

    # Log restart
    from helpers import logger
    logger.info(f"Bot restart initiated by {user_id} ({user_role})")

    # Reload .env before restart
    try:
        from dotenv import load_dotenv
        logger.info("Reloading .env...")
        load_dotenv(override=True)  # Override existing vars with new values
        logger.info("✅ .env reloaded")
    except Exception as e:
        logger.warning(f"Failed to reload .env: {e}")

    # Reload config module
    try:
        import importlib
        logger.info("Reloading config.py...")
        importlib.reload(config)
        logger.info("✅ config.py reloaded")
    except Exception as e:
        logger.warning(f"Failed to reload config: {e}")

    # Note: User data is automatically preserved on restart:
    # - SQLite databases per user: database/sudoers/{user_id}.db
    # - Gcast blacklist: data/gcast_blacklist.json
    # - Lock users: database/sudoers/{user_id}.db
    # - PM permit: database/sudoers/{user_id}.db
    # - Custom settings: database/sudoers/{user_id}.db
    # All file-based storage is preserved across restarts

    # Stop assistant bot if running
    try:
        import subprocess
        subprocess.run(["pkill", "-f", "assistant_bot_pyrogram.py"], timeout=5)
        logger.info("Assistant bot stopped for restart")
    except:
        pass

    # Restart using execv (replaces current process)
    try:
        python = sys.executable
        logger.info(f"Restarting with: {python} {sys.argv}")
        os.execv(python, [python] + sys.argv)
    except Exception as e:
        error_emoji = vz_emoji.getemoji('merah')
        await vz_client.edit_with_premium_emoji(event, f"""
{error_emoji} **Restart Failed**

**Error:** {str(e)}

**Manual Restart:**
Stop bot (Ctrl+C) and run:
`python3 main.py`
""")

print("✅ Plugin loaded: restart.py")
