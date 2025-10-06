"""
VZ ASSISTANT v0.0.0.69
VC Plugin - Voice Chat Management with pytgcalls

Commands:
- .joinvc - Join voice chat (manual)
- .leavevc - Leave voice chat (manual)
- .vcbridge - Start bridge monitor

2025© Vzoel Fox's Lutpan
Founder & DEVELOPER : @VZLfxs
"""

import asyncio
import os
from telethon import events, functions
from telethon.tl.types import InputPeerChannel
import config
from helpers.vc_bridge import VCBridge

# Global variables (set by main.py)
vz_client = None
vz_emoji = None

# VC Bridge instance
vc_bridge = VCBridge()

# Active VC sessions
active_sessions = {}

# Bridge monitor task
bridge_monitor_task = None

# ============================================================================
# PYTGCALLS SETUP
# ============================================================================

try:
    from pytgcalls import PyTgCalls, idle
    from pytgcalls.types import MediaStream, AudioQuality
    from pytgcalls.exceptions import NoActiveGroupCall, AlreadyJoinedError

    # Try to import yt-dlp from vzoelupgrade first, fallback to pip
    try:
        import sys
        vzoelupgrade_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'vzoelupgrade')
        if vzoelupgrade_path not in sys.path:
            sys.path.insert(0, vzoelupgrade_path)
        import yt_dlp
    except ImportError:
        import yt_dlp

    PYTGCALLS_AVAILABLE = True
except ImportError:
    PYTGCALLS_AVAILABLE = False
    print("⚠️  pytgcalls not installed - VC features disabled")

# PyTgCalls client (initialized on first use)
py_tgcalls = None

def init_pytgcalls():
    """Initialize pytgcalls client."""
    global py_tgcalls
    if py_tgcalls is None and PYTGCALLS_AVAILABLE and vz_client:
        py_tgcalls = PyTgCalls(vz_client.client)
    return py_tgcalls

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

async def create_voice_chat(client, chat_id):
    """Create voice chat if not exists."""
    try:
        # Try to join existing VC first
        await client(functions.phone.JoinGroupCallRequest(
            call=InputPeerChannel(
                channel_id=chat_id,
                access_hash=0
            ),
            muted=True
        ))
        return True
    except:
        # If no VC exists, create one
        try:
            await client(functions.phone.CreateGroupCallRequest(
                peer=chat_id,
                random_id=0
            ))
            return True
        except Exception as e:
            print(f"Failed to create VC: {e}")
            return False

async def download_audio(query: str) -> tuple:
    """
    Download audio from YouTube.

    Returns:
        tuple: (file_path, title, duration) or (None, None, None)
    """
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'downloads/%(id)s.%(ext)s',
            'quiet': True,
            'no_warnings': True,
            'extractaudio': True,
            'audioformat': 'mp3',
            'prefer_ffmpeg': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch:{query}", download=True)
            if 'entries' in info:
                info = info['entries'][0]

            file_path = ydl.prepare_filename(info)
            title = info.get('title', query)
            duration = info.get('duration', 0)

            # Convert duration to mm:ss
            minutes = duration // 60
            seconds = duration % 60
            duration_str = f"{minutes}:{seconds:02d}"

            return file_path, title, duration_str

    except Exception as e:
        print(f"Error downloading audio: {e}")
        return None, None, None

# ============================================================================
# BRIDGE MONITOR
# ============================================================================

async def monitor_bridge():
    """Monitor bridge for commands from bot assistant."""
    global active_sessions

    print("🔄 VC Bridge monitor started")

    while True:
        try:
            # Cleanup old commands every loop
            await vc_bridge.cleanup_old_commands(max_age_hours=1)

            # Get bridge data
            import json
            bridge_file = vc_bridge.bridge_file
            if not os.path.exists(bridge_file):
                await asyncio.sleep(1)
                continue

            with open(bridge_file, 'r') as f:
                data = json.load(f)

            # Process pending commands
            for command_id, cmd_data in data.items():
                if command_id == "active_sessions":
                    continue

                if cmd_data.get("status") != "pending":
                    continue

                # Process command
                chat_id = cmd_data["chat_id"]
                command = cmd_data["command"]
                params = cmd_data.get("params", {})

                try:
                    if command == "join":
                        # Join VC
                        result = await join_vc_silent(chat_id)
                        if result:
                            await vc_bridge.update_command(command_id, "completed", {"chat_id": chat_id})
                        else:
                            await vc_bridge.update_command(command_id, "error", error="Failed to join VC")

                    elif command == "play":
                        # Play music
                        song = params.get("song", "")
                        result = await play_music(chat_id, song)
                        if result:
                            await vc_bridge.update_command(command_id, "completed", result)
                        else:
                            await vc_bridge.update_command(command_id, "error", error="Failed to play music")

                    elif command == "leave":
                        # Leave VC
                        result = await leave_vc(chat_id)
                        if result:
                            await vc_bridge.update_command(command_id, "completed", {"chat_id": chat_id})
                        else:
                            await vc_bridge.update_command(command_id, "error", error="Failed to leave VC")

                except Exception as e:
                    await vc_bridge.update_command(command_id, "error", error=str(e))

            await asyncio.sleep(1)  # Check every second

        except Exception as e:
            print(f"Bridge monitor error: {e}")
            await asyncio.sleep(5)

async def join_vc_silent(chat_id: int) -> bool:
    """Join VC silently (no admin required)."""
    global active_sessions

    if not PYTGCALLS_AVAILABLE:
        return False

    try:
        calls = init_pytgcalls()
        if not calls:
            return False

        # Start pytgcalls if not started
        if not calls.is_connected:
            await calls.start()

        # Create VC if not exists
        await create_voice_chat(vz_client.client, chat_id)

        # Join VC
        await calls.join_group_call(
            chat_id,
            MediaStream(
                "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",  # Silent/dummy stream
                audio_parameters=AudioQuality.STUDIO
            ),
        )

        # Track session
        active_sessions[chat_id] = {
            "status": "joined",
            "current_song": None
        }
        await vc_bridge.update_vc_session(chat_id, active_sessions[chat_id])

        return True

    except AlreadyJoinedError:
        return True  # Already joined
    except Exception as e:
        print(f"Error joining VC: {e}")
        return False

async def play_music(chat_id: int, song: str) -> dict:
    """Play music in VC."""
    global active_sessions

    if not PYTGCALLS_AVAILABLE:
        return None

    try:
        # Download audio
        file_path, title, duration = await download_audio(song)
        if not file_path:
            return None

        calls = init_pytgcalls()
        if not calls:
            return None

        # Change stream
        await calls.change_stream(
            chat_id,
            MediaStream(
                file_path,
                audio_parameters=AudioQuality.HIGH
            ),
        )

        # Update session
        if chat_id in active_sessions:
            active_sessions[chat_id]["current_song"] = title
            await vc_bridge.update_vc_session(chat_id, active_sessions[chat_id])

        return {
            "title": title,
            "duration": duration,
            "file": file_path
        }

    except Exception as e:
        print(f"Error playing music: {e}")
        return None

async def leave_vc(chat_id: int) -> bool:
    """Leave VC."""
    global active_sessions

    if not PYTGCALLS_AVAILABLE:
        return False

    try:
        calls = init_pytgcalls()
        if not calls:
            return False

        await calls.leave_group_call(chat_id)

        # Remove session
        if chat_id in active_sessions:
            del active_sessions[chat_id]
        await vc_bridge.remove_vc_session(chat_id)

        return True

    except Exception as e:
        print(f"Error leaving VC: {e}")
        return False

# ============================================================================
# MANUAL COMMANDS (for direct userbot control)
# ============================================================================

@events.register(events.NewMessage(pattern=r'^\.joinvc$', outgoing=True))
async def joinvc_handler(event):
    global vz_client, vz_emoji

    """
    .joinvc - Join voice chat manually

    Joins voice chat in current group silently.
    No admin permission required.
    """
    chat_id = event.chat_id

    robot_emoji = vz_emoji.getemoji('robot')
    status_msg = await vz_client.edit_with_premium_emoji(event, f"{robot_emoji} **Joining voice chat...**")

    if not PYTGCALLS_AVAILABLE:
        error_emoji = vz_emoji.getemoji('merah')
        gear_emoji = vz_emoji.getemoji('gear')
        petir_emoji = vz_emoji.getemoji('petir')
        main_emoji = vz_emoji.getemoji('utama')

        await vz_client.edit_with_premium_emoji(
            status_msg,
            f"{error_emoji} **pytgcalls not installed**\n\n"
            f"{gear_emoji} **Install Required:**\n"
            "`.install pytgcalls yt-dlp`\n\n"
            f"{petir_emoji} **Alternative:**\n"
            "`.install py-tgcalls`\n\n"
            f"{main_emoji} After install, restart bot"
        )
        return

    result = await join_vc_silent(chat_id)

    if result:
        hijau_emoji = vz_emoji.getemoji('hijau')
        await vz_client.edit_with_premium_emoji(
            status_msg,
            f"{hijau_emoji} **Joined voice chat!**\n\n"
            f"📍 Chat: `{chat_id}`\n"
            f"🎙 Mode: Silent (no admin)"
        )
    else:
        merah_emoji = vz_emoji.getemoji('merah')
        await vz_client.edit_with_premium_emoji(
            status_msg,
            f"{merah_emoji} **Failed to join VC**"
        )

@events.register(events.NewMessage(pattern=r'^\.leavevc$', outgoing=True))
async def leavevc_handler(event):
    global vz_client, vz_emoji

    """
    .leavevc - Leave voice chat manually

    Leaves current voice chat session.
    """
    chat_id = event.chat_id

    robot_emoji = vz_emoji.getemoji('robot')
    status_msg = await vz_client.edit_with_premium_emoji(event, f"{robot_emoji} **Leaving voice chat...**")

    result = await leave_vc(chat_id)

    if result:
        hijau_emoji = vz_emoji.getemoji('hijau')
        await vz_client.edit_with_premium_emoji(
            status_msg,
            f"{hijau_emoji} **Left voice chat**"
        )
    else:
        merah_emoji = vz_emoji.getemoji('merah')
        await vz_client.edit_with_premium_emoji(
            status_msg,
            f"{merah_emoji} **Failed to leave VC**"
        )

@events.register(events.NewMessage(pattern=r'^\.vcbridge$', outgoing=True))
async def vcbridge_handler(event):
    global vz_client, vz_emoji, bridge_monitor_task

    """
    .vcbridge - Start/stop bridge monitor

    Starts monitoring bridge for bot assistant commands.
    """
    robot_emoji = vz_emoji.getemoji('robot')

    if bridge_monitor_task and not bridge_monitor_task.done():
        # Stop monitor
        bridge_monitor_task.cancel()
        bridge_monitor_task = None
        await vz_client.edit_with_premium_emoji(
            event,
            f"{robot_emoji} **VC Bridge stopped**"
        )
    else:
        # Start monitor
        bridge_monitor_task = asyncio.create_task(monitor_bridge())
        hijau_emoji = vz_emoji.getemoji('hijau')
        await vz_client.edit_with_premium_emoji(
            event,
            f"{hijau_emoji} **VC Bridge started**\n\n"
            f"📡 Monitoring commands from bot assistant"
        )

print("✅ Plugin loaded: vc.py (with pytgcalls support)")
