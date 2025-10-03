"""
VZ ASSISTANT v0.0.0.69
VZL2-Style Response Helpers

2025© Vzoel Fox's Lutpan
Founder & DEVELOPER : @VZLfxs
"""

import config

def success_response(vz_emoji, message: str, plugin_name: str = "") -> str:
    """
    Create vzl2-style success response.

    Args:
        vz_emoji: VZEmojiManager instance
        message: Success message
        plugin_name: Name of plugin (optional)

    Returns:
        Formatted success message with vzl2 footer
    """
    centang_emoji = vz_emoji.getemoji('centang')
    gear_emoji = vz_emoji.getemoji('gear')
    petir_emoji = vz_emoji.getemoji('petir')
    main_emoji = vz_emoji.getemoji('utama')

    response = f"{centang_emoji} {message}\n\n"

    if plugin_name:
        response += f"{gear_emoji} Plugins Digunakan: **{plugin_name.upper()}**\n"

    response += f"{petir_emoji} by {main_emoji} {config.RESULT_FOOTER}"

    return response

def error_response(vz_emoji, message: str, plugin_name: str = "") -> str:
    """
    Create vzl2-style error response.

    Args:
        vz_emoji: VZEmojiManager instance
        message: Error message
        plugin_name: Name of plugin (optional)

    Returns:
        Formatted error message with vzl2 footer
    """
    merah_emoji = vz_emoji.getemoji('merah')
    gear_emoji = vz_emoji.getemoji('gear')
    petir_emoji = vz_emoji.getemoji('petir')
    main_emoji = vz_emoji.getemoji('utama')

    response = f"{merah_emoji} {message}\n\n"

    if plugin_name:
        response += f"{gear_emoji} Plugins Digunakan: **{plugin_name.upper()}**\n"

    response += f"{petir_emoji} by {main_emoji} {config.RESULT_FOOTER}"

    return response

def info_response(vz_emoji, message: str, plugin_name: str = "") -> str:
    """
    Create vzl2-style info response.

    Args:
        vz_emoji: VZEmojiManager instance
        message: Info message
        plugin_name: Name of plugin (optional)

    Returns:
        Formatted info message with vzl2 footer
    """
    kuning_emoji = vz_emoji.getemoji('kuning')
    gear_emoji = vz_emoji.getemoji('gear')
    petir_emoji = vz_emoji.getemoji('petir')
    main_emoji = vz_emoji.getemoji('utama')

    response = f"{kuning_emoji} {message}\n\n"

    if plugin_name:
        response += f"{gear_emoji} Plugins Digunakan: **{plugin_name.upper()}**\n"

    response += f"{petir_emoji} by {main_emoji} {config.RESULT_FOOTER}"

    return response

def get_vzl2_signature(vz_emoji) -> str:
    """
    Get vzl2 signature pattern: utama + adder1 + petir

    Args:
        vz_emoji: VZEmojiManager instance

    Returns:
        Signature emoji string
    """
    utama = vz_emoji.getemoji('utama')
    adder1 = vz_emoji.getemoji('developer')  # Using developer as adder1
    petir = vz_emoji.getemoji('petir')

    return f"{utama}{adder1}{petir}"

def format_plugin_footer(vz_emoji, plugin_name: str) -> str:
    """
    Format plugin footer in vzl2 style.

    Args:
        vz_emoji: VZEmojiManager instance
        plugin_name: Name of plugin

    Returns:
        Formatted footer string
    """
    gear_emoji = vz_emoji.getemoji('gear')
    petir_emoji = vz_emoji.getemoji('petir')
    main_emoji = vz_emoji.getemoji('utama')

    return f"""
{gear_emoji} Plugins Digunakan: **{plugin_name.upper()}**
{petir_emoji} by {main_emoji} {config.RESULT_FOOTER}"""

print("✅ VZL2 helpers loaded")
