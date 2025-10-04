"""
VZ ASSISTANT v0.0.0.69
Broadcast Middleware - Developer Command Broadcasting to Sudoers

2025© Vzoel Fox's Lutpan
Founder & DEVELOPER : @VZLfxs
"""

from telethon import events
import config

# Global variables (set by main.py)
vz_client = None
vz_emoji = None
manager = None  # MultiClientManager instance

# Developer-only commands that should NOT be broadcast to sudoers
DEVELOPER_ONLY_COMMANDS = [
    'pull', 'push', 'update', 'restart', 'status', 'logs', 'log',
    'sdb', 'sgd', 'cr', 'out', 'dp', 'settoken'
]

# ============================================================================
# BROADCAST MIDDLEWARE
# ============================================================================

@events.register(events.NewMessage(outgoing=True))
async def broadcast_middleware(event):
    """
    Middleware to broadcast developer commands to all sudoers.

    When developer uses .. prefix for regular commands:
    - ..gcast → broadcast to all sudoers
    - ..ping → all sudoers ping
    - ..join → all sudoers join

    Developer-only commands (..pull, ..push, etc) are NOT broadcast.
    """
    global vz_client, vz_emoji, manager

    # Only for developers
    if not vz_client or not vz_client.is_developer:
        return

    # Only process if manager is available
    if not manager:
        return

    # Get message text
    text = event.text
    if not text or not text.startswith('..'):
        return

    # Extract command (remove .. prefix)
    parts = text[2:].split()
    if not parts:
        return

    command = parts[0]

    # Check if this is a developer-only command
    if command in DEVELOPER_ONLY_COMMANDS:
        return  # Don't broadcast developer-only commands

    # Check if sudoers exist
    sudoers = manager.get_sudoer_clients()
    if not sudoers:
        return  # No sudoers to broadcast to

    # Build command with single . prefix for sudoers
    sudoer_command = '.' + text[2:]  # Replace .. with .

    # Show broadcast notification to developer
    main_emoji = vz_emoji.getemoji('utama')
    loading_emoji = vz_emoji.getemoji('loading')
    robot_emoji = vz_emoji.getemoji('robot')
    petir_emoji = vz_emoji.getemoji('petir')

    broadcast_msg = await vz_client.edit_with_premium_emoji(
        event,
        f"{loading_emoji} **Broadcasting command to {len(sudoers)} sudoers...**"
    )

    # Broadcast to all sudoers
    results = await manager.broadcast_command(sudoer_command)

    # Count success/fail
    success_count = sum(1 for v in results.values() if v)
    fail_count = len(results) - success_count

    # Show results
    centang_emoji = vz_emoji.getemoji('centang')
    merah_emoji = vz_emoji.getemoji('merah')

    result_text = f"""
{centang_emoji} **Broadcast Complete**

{robot_emoji} **Command:** `{sudoer_command}`
{petir_emoji} **Sudoers:** {len(sudoers)} total

{centang_emoji} **Succeeded:** {success_count}
{merah_emoji} **Failed:** {fail_count}

{robot_emoji} All sudoers will execute this command.

{robot_emoji} Plugins Digunakan: **BROADCAST**
{petir_emoji} by {main_emoji} Vzoel Fox's Lutpan
"""

    await vz_client.edit_with_premium_emoji(broadcast_msg, result_text)

    # Delete the result after 3 seconds
    import asyncio
    await asyncio.sleep(3)
    try:
        await broadcast_msg.delete()
    except:
        pass

print("✅ Plugin loaded: broadcast_middleware.py")
