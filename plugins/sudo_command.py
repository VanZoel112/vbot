"""
VZ ASSISTANT v0.0.0.69
Sudo Command Plugin - Execute Commands as Other Users

Commands (DEVELOPER ONLY):
- .s<command> <args> - Execute command on behalf of sudoer
  Example: .sgcast Hello from developer

2025© Vzoel Fox's Lutpan
Founder & DEVELOPER : @VZLfxs
"""

from telethon import events
import config

# Global variables (set by main.py)
vz_client = None
vz_emoji = None
manager = None

# Commands that should NOT be caught by sudo prefix
# These are legitimate commands starting with .s
EXCLUDED_COMMANDS = [
    'setlogo', 'resetlogo', 'getlogo',  # Logo commands
    'setpm', 'setget', 'settoken',      # Settings commands
    'showjson', 'sj',                   # JSON commands
    'song', 'stop', 'stag',             # Music/group commands
    'settings',                         # Settings (if added)
]

# ============================================================================
# SUDO COMMAND HANDLER
# ============================================================================

@events.register(events.NewMessage(pattern=r'^\.s([a-z]+)(?:\s+(.*))?$', outgoing=True))
async def sudo_command_handler(event):
    """
    .s<command> - Execute command as sudoer (DEVELOPER ONLY)

    Usage:
        .sgcast <message>   - Broadcast as sudoer
        .sping              - Ping as sudoer
        .salive             - Alive as sudoer

    This allows developers to execute commands on behalf of sudoers
    without switching accounts.

    IMPORTANT: Does NOT catch .setlogo, .setpm, etc (excluded list)
    """
    global vz_client, vz_emoji, manager

    # Check if developer
    if not config.is_developer(event.sender_id):
        return  # Silently ignore for non-developers

    # Extract command and args
    command = event.pattern_match.group(1)
    args = event.pattern_match.group(2) or ""

    # Check if this is an excluded command (legitimate .s* command)
    if command in EXCLUDED_COMMANDS:
        return  # Let the original handler process it

    # Check if manager is available
    if not manager:
        error_emoji = vz_emoji.getemoji('merah')
        await vz_client.edit_with_premium_emoji(
            event,
            f"{error_emoji} **Manager not available**\n\nNo sudoers connected"
        )
        return

    # Get sudoers
    sudoers = manager.get_sudoer_clients()

    if not sudoers:
        error_emoji = vz_emoji.getemoji('merah')
        await vz_client.edit_with_premium_emoji(
            event,
            f"{error_emoji} **No sudoers connected**\n\nDeploy sudoers first with `.dp`"
        )
        return

    # Build full command
    full_command = f".{command}"
    if args:
        full_command += f" {args}"

    # Show broadcast notification
    loading_emoji = vz_emoji.getemoji('loading')
    petir_emoji = vz_emoji.getemoji('petir')
    dev_emoji = vz_emoji.getemoji('developer')

    status_msg = await vz_client.edit_with_premium_emoji(
        event,
        f"{loading_emoji} **Executing as sudoer...**\n\n"
        f"{petir_emoji} **Command:** `{full_command}`\n"
        f"{dev_emoji} **Sudoers:** {len(sudoers)}"
    )

    # Broadcast command to all sudoers
    results = await manager.broadcast_command(full_command)

    # Count success/fail
    success_count = sum(1 for v in results.values() if v)
    fail_count = len(results) - success_count

    # Show results
    centang_emoji = vz_emoji.getemoji('centang')
    merah_emoji = vz_emoji.getemoji('merah')
    robot_emoji = vz_emoji.getemoji('robot')
    main_emoji = vz_emoji.getemoji('utama')

    result_text = f"""
{centang_emoji} **Sudo Command Executed**

{robot_emoji} **Command:** `{full_command}`
{dev_emoji} **Target:** {len(sudoers)} sudoers

{centang_emoji} **Succeeded:** {success_count}
{merah_emoji} **Failed:** {fail_count}

{petir_emoji} {robot_emoji} Plugins Digunakan: **SUDO**
{petir_emoji} by {main_emoji} {config.RESULT_FOOTER}
"""

    await vz_client.edit_with_premium_emoji(status_msg, result_text)

    # Auto-delete after 5 seconds
    import asyncio
    await asyncio.sleep(5)
    try:
        await status_msg.delete()
    except:
        pass

print("✅ Plugin loaded: sudo_command.py")
