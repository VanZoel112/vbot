"""
VZ ASSISTANT v0.0.0.69
Install Plugin - Dependency Management

Commands:
- .install <package> - Install Python package
- .install (reply to requirements.txt) - Install from file
- .uninstall <package> - Uninstall package
- .piplist - List installed packages

2025© Vzoel Fox's Lutpan
Founder & DEVELOPER : @VZLfxs
"""

from telethon import events
import subprocess
import asyncio
import os
import config
from utils.animation import animate_loading

# Global variables (set by main.py)
vz_client = None
vz_emoji = None

# Common packages with descriptions
COMMON_PACKAGES = {
    "pillow": "Image processing library",
    "pytgcalls": "Voice chat support",
    "py-tgcalls": "Alternative voice chat library",
    "yt-dlp": "YouTube downloader",
    "aiohttp": "Async HTTP client",
    "requests": "HTTP library",
    "beautifulsoup4": "HTML parser",
    "opencv-python": "Computer vision",
    "numpy": "Scientific computing",
    "pandas": "Data analysis",
    "matplotlib": "Plotting library",
    "ffmpeg-python": "FFmpeg wrapper"
}

# ============================================================================
# INSTALL COMMAND
# ============================================================================

@events.register(events.NewMessage(pattern=r'^\.install(?:\s+(.+))?$', outgoing=True))
async def install_handler(event):
    """
    .install - Install Python package

    Usage:
        .install <package>       - Install specific package
        .install (reply to file) - Install from requirements.txt

    Examples:
        .install pillow
        .install pytgcalls
        .install requests aiohttp
    """
    global vz_client, vz_emoji

    package_name = event.pattern_match.group(1)
    reply = await event.get_reply_message()

    # Run animation
    msg = await animate_loading(vz_client, vz_emoji, event)

    # Check if replying to requirements file
    if reply and reply.media and reply.file:
        if reply.file.name and reply.file.name.endswith('.txt'):
            # Download requirements file
            loading_emoji = vz_emoji.getemoji('loading')
            await vz_client.edit_with_premium_emoji(msg, f"{loading_emoji} **Downloading requirements.txt...**")

            file_path = await reply.download_media(file="requirements.txt")

            # Install from file
            await vz_client.edit_with_premium_emoji(msg, f"{loading_emoji} **Installing from {reply.file.name}...**")

            try:
                process = await asyncio.create_subprocess_exec(
                    "pip3", "install", "-r", file_path,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )

                stdout, stderr = await process.communicate()

                # Clean up
                os.remove(file_path)

                if process.returncode == 0:
                    success_emoji = vz_emoji.getemoji('centang')
                    petir_emoji = vz_emoji.getemoji('petir')
                    gear_emoji = vz_emoji.getemoji('gear')
                    main_emoji = vz_emoji.getemoji('utama')

                    result_text = f"""
{success_emoji} **Installation Complete**

**File:** {reply.file.name}
**Status:** Successfully installed

**Output:**
```
{stdout.decode()[-500:] if stdout else 'Success'}
```

{petir_emoji} {gear_emoji} Plugins Digunakan: **INSTALL**
{petir_emoji} by {main_emoji} {config.RESULT_FOOTER}
"""
                    await vz_client.edit_with_premium_emoji(msg, result_text)
                else:
                    error_emoji = vz_emoji.getemoji('merah')
                    await vz_client.edit_with_premium_emoji(msg, f"""
{error_emoji} **Installation Failed**

**Error:**
```
{stderr.decode()[-500:]}
```
""")

            except Exception as e:
                error_emoji = vz_emoji.getemoji('merah')
                await vz_client.edit_with_premium_emoji(msg, f"{error_emoji} **Error:** {str(e)}")

            return

    if not package_name:
        # Show common packages
        gear_emoji = vz_emoji.getemoji('gear')
        petir_emoji = vz_emoji.getemoji('petir')
        main_emoji = vz_emoji.getemoji('utama')
        robot_emoji = vz_emoji.getemoji('robot')

        packages_text = "\n".join([f"• `{pkg}` - {desc}" for pkg, desc in COMMON_PACKAGES.items()])

        await vz_client.edit_with_premium_emoji(msg, f"""
{gear_emoji} **INSTALL - Dependency Manager**

**Usage:**
`.install <package>` - Install package
`.install` reply to requirements.txt

**Common Packages:**
{packages_text}

**Examples:**
`.install pillow`
`.install pytgcalls yt-dlp`

{petir_emoji} {robot_emoji} Plugins Digunakan: **INSTALL**
{petir_emoji} by {main_emoji} {config.RESULT_FOOTER}
""")
        return

    # Install package(s)
    packages = package_name.split()
    loading_emoji = vz_emoji.getemoji('loading')

    for pkg in packages:
        await vz_client.edit_with_premium_emoji(msg, f"{loading_emoji} **Installing {pkg}...**")

        try:
            process = await asyncio.create_subprocess_exec(
                "pip3", "install", pkg, "--upgrade",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                # Verify installation
                verify = await asyncio.create_subprocess_exec(
                    "pip3", "show", pkg,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                verify_out, _ = await verify.communicate()

                if verify.returncode == 0:
                    success_emoji = vz_emoji.getemoji('centang')
                    await vz_client.edit_with_premium_emoji(msg, f"{success_emoji} **{pkg}** installed successfully!")
                else:
                    kuning_emoji = vz_emoji.getemoji('kuning')
                    await vz_client.edit_with_premium_emoji(msg, f"{kuning_emoji} **{pkg}** install completed but not verified")
                await asyncio.sleep(1)
            else:
                error_emoji = vz_emoji.getemoji('merah')
                error_msg = stderr.decode()[-300:] if stderr else "Unknown error"
                await vz_client.edit_with_premium_emoji(msg, f"{error_emoji} **{pkg}** failed:\n```\n{error_msg}\n```")
                await asyncio.sleep(2)

        except Exception as e:
            error_emoji = vz_emoji.getemoji('merah')
            await vz_client.edit_with_premium_emoji(msg, f"{error_emoji} **Error installing {pkg}:** {str(e)}")
            await asyncio.sleep(2)

    # Final summary
    success_emoji = vz_emoji.getemoji('centang')
    petir_emoji = vz_emoji.getemoji('petir')
    gear_emoji = vz_emoji.getemoji('gear')
    main_emoji = vz_emoji.getemoji('utama')

    result_text = f"""
{success_emoji} **Installation Process Complete**

**Installed:** {', '.join(packages)}

**Check Status:**
Use `.piplist {packages[0]}` to verify

{petir_emoji} {gear_emoji} Plugins Digunakan: **INSTALL**
{petir_emoji} by {main_emoji} {config.RESULT_FOOTER}
"""

    await vz_client.edit_with_premium_emoji(msg, result_text)

# ============================================================================
# UNINSTALL COMMAND
# ============================================================================

@events.register(events.NewMessage(pattern=r'^\.uninstall\s+(.+)$', outgoing=True))
async def uninstall_handler(event):
    """
    .uninstall - Uninstall Python package

    Usage:
        .uninstall <package>

    Example:
        .uninstall pillow
    """
    global vz_client, vz_emoji

    package_name = event.pattern_match.group(1).strip()

    # Run animation
    msg = await animate_loading(vz_client, vz_emoji, event)

    loading_emoji = vz_emoji.getemoji('loading')
    await vz_client.edit_with_premium_emoji(msg, f"{loading_emoji} **Uninstalling {package_name}...**")

    try:
        process = await asyncio.create_subprocess_exec(
            "pip3", "uninstall", package_name, "-y",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        if process.returncode == 0:
            success_emoji = vz_emoji.getemoji('centang')
            petir_emoji = vz_emoji.getemoji('petir')
            gear_emoji = vz_emoji.getemoji('gear')
            main_emoji = vz_emoji.getemoji('utama')

            result_text = f"""
{success_emoji} **Uninstalled Successfully**

**Package:** {package_name}
**Status:** Removed

{petir_emoji} {gear_emoji} Plugins Digunakan: **INSTALL**
{petir_emoji} by {main_emoji} {config.RESULT_FOOTER}
"""
            await vz_client.edit_with_premium_emoji(msg, result_text)
        else:
            error_emoji = vz_emoji.getemoji('merah')
            error_msg = stderr.decode()[-300:] if stderr else "Unknown error"
            await vz_client.edit_with_premium_emoji(msg, f"{error_emoji} **Failed to uninstall:**\n```\n{error_msg}\n```")

    except Exception as e:
        error_emoji = vz_emoji.getemoji('merah')
        await vz_client.edit_with_premium_emoji(msg, f"{error_emoji} **Error:** {str(e)}")

# ============================================================================
# PIPLIST COMMAND
# ============================================================================

@events.register(events.NewMessage(pattern=r'^\.piplist(?:\s+(.+))?$', outgoing=True))
async def piplist_handler(event):
    """
    .piplist - List installed packages

    Usage:
        .piplist          - List all packages
        .piplist <search> - Search for specific package

    Example:
        .piplist pytgcalls
    """
    global vz_client, vz_emoji

    search_term = event.pattern_match.group(1)

    # Run animation
    msg = await animate_loading(vz_client, vz_emoji, event)

    try:
        if search_term:
            # Search for specific package
            process = await asyncio.create_subprocess_exec(
                "pip3", "show", search_term.strip(),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
        else:
            # List all packages
            process = await asyncio.create_subprocess_exec(
                "pip3", "list",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

        stdout, stderr = await process.communicate()

        if process.returncode == 0:
            output = stdout.decode()

            # Limit output
            if len(output) > 3000:
                output = output[:3000] + "\n... (truncated)"

            gear_emoji = vz_emoji.getemoji('gear')
            petir_emoji = vz_emoji.getemoji('petir')
            main_emoji = vz_emoji.getemoji('utama')

            result_text = f"""
{gear_emoji} **{'Package Info' if search_term else 'Installed Packages'}**

```
{output}
```

{petir_emoji} {gear_emoji} Plugins Digunakan: **INSTALL**
{petir_emoji} by {main_emoji} {config.RESULT_FOOTER}
"""
            await vz_client.edit_with_premium_emoji(msg, result_text)
        else:
            error_emoji = vz_emoji.getemoji('merah')
            if search_term:
                await vz_client.edit_with_premium_emoji(msg, f"{error_emoji} **Package '{search_term}' not found**")
            else:
                await vz_client.edit_with_premium_emoji(msg, f"{error_emoji} **Failed to list packages**")

    except Exception as e:
        error_emoji = vz_emoji.getemoji('merah')
        await vz_client.edit_with_premium_emoji(msg, f"{error_emoji} **Error:** {str(e)}")

print("✅ Plugin loaded: install.py")
