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
from utils.animation import animate_loading

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

    # Run 12-phase animation
    msg = await animate_loading(vz_client, vz_emoji, event)

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

    # Get varied emojis
    main_emoji = vz_emoji.getemoji('utama')
    petir_emoji = vz_emoji.getemoji('petir')
    nyala_emoji = vz_emoji.getemoji('nyala')
    owner_emoji = vz_emoji.getemoji('owner')
    dev_emoji = vz_emoji.getemoji('developer')

    # Get owner username safely
    owner_username = 'Unknown'
    if event.sender:
        owner_username = event.sender.username if event.sender.username else 'Unknown'

    # Build response with varied emojis
    response = f"""
{main_emoji}{status_emoji} **VZ ASSISTANT - PING**

{petir_emoji} **Latency:** `{latency_ms}ms`
{nyala_emoji} **Uptime:** `{uptime}`
{owner_emoji} **Owner:** @{owner_username}
{dev_emoji} **Founder:** {config.FOUNDER_USERNAME}

{gear_emoji} Plugins Digunakan: **PING**
{petir_emoji} by {main_emoji} Vzoel Fox's Lutpan
"""

    await vz_client.edit_with_premium_emoji(msg, response)

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

    # Run 12-phase animation
    msg = await animate_loading(vz_client, vz_emoji, event)

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

    # Get varied emojis
    petir_emoji = vz_emoji.getemoji('petir')
    main_emoji = vz_emoji.getemoji('utama')

    # Build response with varied emojis
    response = f"""
{status_emoji} **{latency_ms}ms** - {status_text}

{gear_emoji} Plugins Digunakan: **PINK**
{petir_emoji} by {main_emoji} Vzoel Fox's Lutpan
"""

    await vz_client.edit_with_premium_emoji(msg, response)

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

    # Run 12-phase animation
    msg = await animate_loading(vz_client, vz_emoji, event)

    # Get uptime from client
    uptime = vz_client.get_uptime() if vz_client else "0s"

    # Get emojis
    nyala_emoji = vz_emoji.getemoji('nyala')
    petir_emoji = vz_emoji.getemoji('petir')
    gear_emoji = vz_emoji.getemoji('gear')
    main_emoji = vz_emoji.getemoji('utama')

    response = f"""
{nyala_emoji} **VZ ASSISTANT - UPTIME**

⏰ **Uptime:** `{uptime}`

{gear_emoji} Plugins Digunakan: **PONG**
{petir_emoji} by {main_emoji} Vzoel Fox's Lutpan
"""

    await vz_client.edit_with_premium_emoji(msg, response)

print("✅ Plugin loaded: ping.py")
