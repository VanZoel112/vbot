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

    # 12 animation frames with premium emojis
    frames = [
        f"{loading_emoji} Loading...",
        f"{petir_emoji} Initializing...",
        f"{proses1_emoji} Processing...",
        f"{proses2_emoji} Gathering data...",
        f"{proses3_emoji} Compiling info...",
        f"{gear_emoji} Almost there...",
        f"{loading_emoji} Finalizing...",
        f"{gear_emoji} Configuring...",
        f"{proses1_emoji} Optimizing...",
        f"{proses2_emoji} Polishing...",
        f"{proses3_emoji} Rendering...",
        f"{checklist_emoji} Complete!"
    ]

    # Start with first frame
    msg = await vz_client.edit_with_premium_emoji(event_or_message, frames[0])

    # Animate through remaining frames
    for frame in frames[1:]:
        await asyncio.sleep(config.ANIMATION_DELAY)
        msg = await vz_client.edit_with_premium_emoji(msg, frame)

    # Small delay before final output
    await asyncio.sleep(config.ANIMATION_DELAY)

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

print("✅ Animation utilities loaded")
