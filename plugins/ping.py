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

# Global variables (set by main.py)
vz_client = None
vz_emoji = None

# ============================================================================
# PING COMMAND
# ============================================================================

@events.register(events.NewMessage(pattern=r'^\.ping$', outgoing=True))
async def ping_handler(event):
    """
    .ping - Check latency and uptime
    Shows: Latency (ms), Uptime, Owner, Founder
    """
    global vz_client, vz_emoji

    start_time = time.time()

    # Initial response with loading emoji
    loading_emoji = vz_emoji.getemoji('loading')
    msg = await event.edit(f"{loading_emoji} **Pinging...**")

    # Calculate latency
    end_time = time.time()
    latency_ms = round((end_time - start_time) * 1000, 2)

    # Get uptime from client
    uptime = vz_client.get_uptime() if vz_client else "0s"

    # Get emoji based on latency (premium emojis)
    if latency_ms <= 150:
        status_emoji = vz_emoji.getemoji('hijau')  # 👍 HIJAU
    elif latency_ms <= 200:
        status_emoji = vz_emoji.getemoji('kuning')  # ⚠️ KUNING
    else:
        status_emoji = vz_emoji.getemoji('merah')  # 👎 MERAH

    # Get signature emojis
    main_emoji = vz_emoji.getemoji('utama')
    petir_emoji = vz_emoji.getemoji('petir')

    # Build response
    response = f"""
{main_emoji}{status_emoji} **VZ ASSISTANT - PING**

⚡ **Latency:** `{latency_ms}ms`
⏰ **Uptime:** `{uptime}`
👤 **Owner:** @{event.sender.username if event.sender.username else 'Unknown'}
🌟 **Founder:** {config.FOUNDER_USERNAME}

{petir_emoji} {config.BRANDING_FOOTER}
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
    Shows compact latency status
    """
    global vz_client, vz_emoji

    start_time = time.time()

    # Initial response with gear emoji
    gear_emoji = vz_emoji.getemoji('gear')
    msg = await event.edit(f"{gear_emoji} **Checking...**")

    # Calculate latency
    end_time = time.time()
    latency_ms = round((end_time - start_time) * 1000, 2)

    # Get emoji based on latency with premium mapping
    if latency_ms <= 150:
        status_emoji = vz_emoji.getemoji('hijau')  # 👍 HIJAU (1-150ms)
        status_text = "Excellent"
    elif latency_ms <= 200:
        status_emoji = vz_emoji.getemoji('kuning')  # ⚠️ KUNING (151-200ms)
        status_text = "Good"
    else:
        status_emoji = vz_emoji.getemoji('merah')  # 👎 MERAH (200+ms)
        status_text = "Slow"

    # Get signature emoji
    petir_emoji = vz_emoji.getemoji('petir')

    # Build response
    response = f"""
{status_emoji} **{latency_ms}ms** - {status_text}

{petir_emoji} {config.BRANDING_FOOTER}
"""

    await msg.edit(response)

# ============================================================================
# PONG COMMAND (shows uptime)
# ============================================================================

@events.register(events.NewMessage(pattern=r'^\.pong$', outgoing=True))
async def pong_handler(event):
    """
    .pong - Show uptime
    Displays bot uptime information
    """
    global vz_client, vz_emoji

    # Get uptime from client
    uptime = vz_client.get_uptime() if vz_client else "0s"

    # Get emojis
    nyala_emoji = vz_emoji.getemoji('nyala')
    petir_emoji = vz_emoji.getemoji('petir')

    response = f"""
{nyala_emoji} **VZ ASSISTANT - UPTIME**

⏰ **Uptime:** `{uptime}`

{petir_emoji} {config.BRANDING_FOOTER}
Founder & DEVELOPER : {config.FOUNDER_USERNAME}
"""

    await event.edit(response)

print("✅ Plugin loaded: ping.py")
