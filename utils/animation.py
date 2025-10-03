"""
VZ ASSISTANT v0.0.0.69
Animation Utilities - 12-Phase Loading Animation

2025© Vzoel Fox's Lutpan
Founder & DEVELOPER : @VZLfxs
"""

import asyncio
import config

async def animate_loading(vz_client, vz_emoji, event_or_message):
    """
    12-phase premium emoji loading animation.
    VZOEL FOX'S STYLE - Descriptive phases matching vzl2 pattern.

    Args:
        vz_client: VZClient instance
        vz_emoji: VZEmojiManager instance
        event_or_message: Event or Message object to edit

    Returns:
        Final message object after animation completes
    """
    # Get premium emojis for animation
    loading_emoji = vz_emoji.getemoji('loading')
    gear_emoji = vz_emoji.getemoji('gear')
    proses1_emoji = vz_emoji.getemoji('proses1')
    proses2_emoji = vz_emoji.getemoji('proses2')
    proses3_emoji = vz_emoji.getemoji('proses3')
    checklist_emoji = vz_emoji.getemoji('centang')
    petir_emoji = vz_emoji.getemoji('petir')
    nyala_emoji = vz_emoji.getemoji('nyala')

    # 12 descriptive animation phases (vzl2 style)
    frames = [
        f"{loading_emoji} Initializing Vzoel Fox's Assistant...",
        f"{petir_emoji} Loading premium systems...",
        f"{proses1_emoji} Activating power modules...",
        f"{proses2_emoji} Configuring features...",
        f"{nyala_emoji} Establishing connections...",
        f"{gear_emoji} Running diagnostics...",
        f"{proses3_emoji} Checking permissions...",
        f"{loading_emoji} Validating plugins...",
        f"{petir_emoji} Applying enhancements...",
        f"{proses1_emoji} Finalizing configuration...",
        f"{checklist_emoji} System ready...",
        f"{nyala_emoji} Vzoel Fox's Assistant ONLINE!"
    ]

    # Start with first frame
    msg = await vz_client.edit_with_premium_emoji(event_or_message, frames[0])

    # Animate through remaining frames (vzl2 uses 7 reduced phases)
    # We'll show all 12 but with optimized timing
    for i, frame in enumerate(frames[1:7], 1):  # Show first 7 phases
        await asyncio.sleep(config.ANIMATION_DELAY)
        msg = await vz_client.edit_with_premium_emoji(msg, frame)

    # Small delay before final output
    await asyncio.sleep(1)

    return msg

async def animate_custom(vz_client, event_or_message, frames, delay=None):
    """
    Custom animation with provided frames.

    Args:
        vz_client: VZClient instance
        event_or_message: Event or Message object to edit
        frames: List of text frames to animate
        delay: Optional custom delay (defaults to config.ANIMATION_DELAY)

    Returns:
        Final message object after animation completes
    """
    if not frames:
        return event_or_message

    delay = delay or config.ANIMATION_DELAY

    # Start with first frame
    msg = await vz_client.edit_with_premium_emoji(event_or_message, frames[0])

    # Animate through remaining frames
    for frame in frames[1:]:
        await asyncio.sleep(delay)
        msg = await vz_client.edit_with_premium_emoji(msg, frame)

    return msg

async def animate_fast(vz_client, vz_emoji, event_or_message):
    """
    Fast 4-phase animation for quick operations.

    Args:
        vz_client: VZClient instance
        vz_emoji: VZEmojiManager instance
        event_or_message: Event or Message object to edit

    Returns:
        Final message object after animation completes
    """
    # Get premium emojis
    loading_emoji = vz_emoji.getemoji('loading')
    proses1_emoji = vz_emoji.getemoji('proses1')
    gear_emoji = vz_emoji.getemoji('gear')
    checklist_emoji = vz_emoji.getemoji('centang')

    # 4 fast animation frames
    frames = [
        f"{loading_emoji} Processing...",
        f"{proses1_emoji} Working...",
        f"{gear_emoji} Finalizing...",
        f"{checklist_emoji} Done!"
    ]

    # Use fast delay
    delay = getattr(config, 'FAST_ANIMATION_DELAY', 0.2)

    # Start with first frame
    msg = await vz_client.edit_with_premium_emoji(event_or_message, frames[0])

    # Animate through remaining frames
    for frame in frames[1:]:
        await asyncio.sleep(delay)
        msg = await vz_client.edit_with_premium_emoji(msg, frame)

    await asyncio.sleep(delay)
    return msg

async def animate_ping(vz_client, vz_emoji, event_or_message):
    """
    Ping-specific animation (vzl2 style).
    Shows latency calculation process.

    Args:
        vz_client: VZClient instance
        vz_emoji: VZEmojiManager instance
        event_or_message: Event or Message object to edit

    Returns:
        Final message object after animation completes
    """
    loading_emoji = vz_emoji.getemoji('loading')

    # Ping animation frame (vzl2 pattern - simple and fast)
    msg = await vz_client.edit_with_premium_emoji(
        event_or_message,
        f"{loading_emoji} Menghitung..."
    )

    return msg

async def animate_alive(vz_client, vz_emoji, event_or_message):
    """
    Alive-specific 12-phase animation (vzl2 style).
    Descriptive phases for alive plugin.

    Args:
        vz_client: VZClient instance
        vz_emoji: VZEmojiManager instance
        event_or_message: Event or Message object to edit

    Returns:
        Final message object after animation completes
    """
    # Get premium emojis
    loading_emoji = vz_emoji.getemoji('loading')
    proses1_emoji = vz_emoji.getemoji('proses1')
    petir_emoji = vz_emoji.getemoji('petir')
    nyala_emoji = vz_emoji.getemoji('nyala')
    gear_emoji = vz_emoji.getemoji('gear')
    proses2_emoji = vz_emoji.getemoji('proses2')
    checklist_emoji = vz_emoji.getemoji('centang')

    # 12-phase animation with Vzoel Fox's descriptive phases
    animation_phases = [
        f"{loading_emoji} Initializing Vzoel Fox's Assistant...",
        f"{proses1_emoji} Loading premium systems...",
        f"{petir_emoji} Activating power modules...",
        f"{nyala_emoji} Configuring features...",
        f"{gear_emoji} Establishing connections...",
        f"{proses2_emoji} Running diagnostics...",
        f"{checklist_emoji} System ready..."
    ]

    # Start animation with first phase
    msg = await vz_client.edit_with_premium_emoji(event_or_message, animation_phases[0])

    # Animate through reduced phases (vzl2 uses 7 to prevent flood)
    for i in range(1, 7):
        await asyncio.sleep(config.ANIMATION_DELAY)
        msg = await vz_client.edit_with_premium_emoji(msg, animation_phases[i])

    # Final delay before showing result
    await asyncio.sleep(1)

    return msg

print("✅ Animation utilities loaded - vzl2 style enabled")
