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
    .restart - Restart bot

    Restarts the bot to apply changes.
    Available for all roles (USER, ADMIN, DEVELOPER).

    Usage:
        .restart

    After restart:
    - New plugins will be loaded
    - Configuration changes applied
    - Memory cleared
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
{petir_emoji} **Action:** Bot restart

{nyala_emoji} **Please wait...**
Bot will reconnect in a few seconds

{main_emoji} by {config.RESULT_FOOTER}
"""

    await vz_client.edit_with_premium_emoji(event, restart_text)

    # Log restart
    from helpers import logger
    logger.info(f"Bot restart initiated by {user_id} ({user_role})")

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
