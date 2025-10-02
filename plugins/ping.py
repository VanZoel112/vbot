"""
VZ ASSISTANT v0.0.0.69
Ping Plugin - Latency & Uptime Checker

2025© Vzoel Fox's Lutpan
Founder & DEVELOPER : @VZLfxs
"""

from telethon import events
import time
import asyncio
import config

# ============================================================================
# PING COMMAND
# ============================================================================

@events.register(events.NewMessage(pattern=r'^\.ping$', outgoing=True))
async def ping_handler(event):
    """
    .ping - Check latency and uptime
    Shows: Latency (ms), Uptime, Owner, Founder
    """
    start_time = time.time()

    # Initial response
    msg = await event.edit("**Pinging...**")

    # Calculate latency
    end_time = time.time()
    latency_ms = round((end_time - start_time) * 1000, 2)

    # Get uptime (placeholder - will be from client)
    uptime = "0h 0m 0s"  # TODO: Implement actual uptime

    # Get emoji based on latency
    emoji_map = config.load_emoji_mapping()
    if latency_ms <= 150:
        status_emoji = "👍"  # HIJAU
    elif latency_ms <= 200:
        status_emoji = "⚠️"  # KUNING
    else:
        status_emoji = "👎"  # MERAH

    # Build response
    response = f"""
{status_emoji} **VZ ASSISTANT - PING**

⚡ **Latency:** `{latency_ms}ms`
⏰ **Uptime:** `{uptime}`
👤 **Owner:** @{event.sender.username if event.sender.username else 'Unknown'}
🌟 **Founder:** {config.FOUNDER_USERNAME}

{config.BRANDING_FOOTER} PING
Founder & DEVELOPER : {config.FOUNDER_USERNAME}
"""

    await msg.edit(response)

# ============================================================================
# PINK COMMAND (with color emoji)
# ============================================================================

@events.register(events.NewMessage(pattern=r'^\.pink$', outgoing=True))
async def pink_handler(event):
    """
    .pink - Check latency with color emoji mapping
    Auto-triggers .limit after execution
    """
    start_time = time.time()

    # Initial response
    msg = await event.edit("**🔍 Checking...**")

    # Calculate latency
    end_time = time.time()
    latency_ms = round((end_time - start_time) * 1000, 2)

    # Get emoji based on latency with premium mapping
    if latency_ms <= 150:
        status_emoji = "👍"  # HIJAU (1-150ms)
        status_text = "Excellent"
    elif latency_ms <= 200:
        status_emoji = "⚠️"  # KUNING (151-200ms)
        status_text = "Good"
    else:
        status_emoji = "👎"  # MERAH (200+ms)
        status_text = "Slow"

    # Build response
    response = f"""
{status_emoji} **{latency_ms}ms** - {status_text}

{config.BRANDING_FOOTER} PING
"""

    await msg.edit(response)

    # Auto-trigger .limit (placeholder)
    # TODO: Implement .limit command integration

# ============================================================================
# PONG COMMAND (shows uptime)
# ============================================================================

@events.register(events.NewMessage(pattern=r'^\.pong$', outgoing=True))
async def pong_handler(event):
    """
    .pong - Show uptime
    Auto-triggers .alive after execution
    """
    # Get uptime (placeholder - will be from client)
    uptime = "0h 0m 0s"  # TODO: Implement actual uptime

    response = f"""
⏰ **Uptime:** `{uptime}`

{config.BRANDING_FOOTER} PONG
Founder & DEVELOPER : {config.FOUNDER_USERNAME}
"""

    await event.edit(response)

    # Auto-trigger .alive (placeholder)
    # TODO: Implement .alive command integration

print("✅ Plugin loaded: ping.py")
