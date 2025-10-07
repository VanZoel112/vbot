"""
VZ ASSISTANT v0.0.0.69
Voice Chat Plugin - PyTgCalls with Telethon (vzl2 style)

Commands:
- .joinvc / .jvc - Join voice chat silently
- .leavevc / .lvc - Leave voice chat
- .vcstatus - Show VC status

2025© Vzoel Fox's Lutpan
Founder & DEVELOPER : @VZLfxs
"""

import asyncio
import os
import time
from typing import Dict, Optional
from telethon import events
from telethon.utils import get_display_name
from telethon.tl.functions.phone import JoinGroupCallRequest, LeaveGroupCallRequest
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.types import DataJSON

# Global variables (set by main.py)
vz_client = None
vz_emoji = None

# Silence audio URL
SILENCE_URL = "https://raw.githubusercontent.com/anars/blank-audio/master/1-second-of-silence.mp3"

# PyTgCalls setup
try:
    from pytgcalls import PyTgCalls
    from pytgcalls.types import GroupCallConfig, MediaStream
    from pytgcalls.exceptions import NoActiveGroupCall, NotInCallError, PyTgCallsAlreadyRunning
    PYTGCALLS_AVAILABLE = True
except ImportError:
    class NoActiveGroupCall(Exception): pass
    class NotInCallError(Exception): pass
    class PyTgCallsAlreadyRunning(Exception): pass
    PyTgCalls = None
    GroupCallConfig = None
    MediaStream = None
    PYTGCALLS_AVAILABLE = False

# Runtime state
_voice_client: Optional[PyTgCalls] = None
_voice_client_lock: Optional[asyncio.Lock] = None
_state_lock: Optional[asyncio.Lock] = None
_active_calls: Dict[int, Dict] = {}


async def _ensure_locks():
    """Create locks once event loop is running."""
    global _voice_client_lock, _state_lock
    if _voice_client_lock is None:
        _voice_client_lock = asyncio.Lock()
    if _state_lock is None:
        _state_lock = asyncio.Lock()


async def _ensure_voice_client(telethon_client) -> Optional[PyTgCalls]:
    """Ensure PyTgCalls with Telethon client."""
    await _ensure_locks()

    if not PYTGCALLS_AVAILABLE or PyTgCalls is None:
        return None

    global _voice_client
    async with _voice_client_lock:
        if _voice_client is None:
            _voice_client = PyTgCalls(telethon_client)  # ← Telethon directly!
            try:
                await _voice_client.start()
            except PyTgCallsAlreadyRunning:
                pass
            except Exception:
                _voice_client = None
                raise

    return _voice_client


async def _join_vc_silent(client, chat_id) -> bool:
    """
    Join VC silently using raw Telethon (pure listener mode).
    No audio streaming - like regular user joining.
    """
    try:
        chat = await client.get_entity(chat_id)
        full_chat = await client(GetFullChannelRequest(chat))

        if not full_chat.full_chat.call:
            raise NoActiveGroupCall("No active voice chat")

        # Join as pure listener (no audio/video)
        await client(JoinGroupCallRequest(
            call=full_chat.full_chat.call,
            join_as=await client.get_me(),
            params=DataJSON(data='{"ufrag":"","pwd":"","fingerprints":[],"ssrc":0}'),
            muted=True,
            video_stopped=True
        ))
        return True
    except Exception:
        return False


async def _leave_vc_silent(client, chat_id) -> bool:
    """Leave VC using raw Telethon."""
    try:
        chat = await client.get_entity(chat_id)
        full_chat = await client(GetFullChannelRequest(chat))

        if not full_chat.full_chat.call:
            return False

        await client(LeaveGroupCallRequest(call=full_chat.full_chat.call))
        return True
    except Exception:
        return False


@events.register(events.NewMessage(pattern=r'^\.(?:jvc|joinvc)$', outgoing=True))
async def joinvc_handler(event):
    """Join voice chat silently."""
    global vz_client, vz_emoji

    if event.is_private:
        kuning_emoji = vz_emoji.getemoji('kuning')
        await vz_client.edit_with_premium_emoji(event, f"{kuning_emoji} Only works in groups\n\nVZ ASSISTANT")
        return

    try:
        voice_client = await _ensure_voice_client(event.client)
    except Exception as exc:
        merah_emoji = vz_emoji.getemoji('merah')
        await vz_client.edit_with_premium_emoji(
            event,
            f"{merah_emoji} **PyTgCalls failed**\n\nError: {str(exc)[:80]}\n\nVZ ASSISTANT"
        )
        return

    if voice_client is None:
        merah_emoji = vz_emoji.getemoji('merah')
        await vz_client.edit_with_premium_emoji(
            event,
            f"{merah_emoji} **PyTgCalls not installed**\n\nInstall: `.install py-tgcalls`\n\nVZ ASSISTANT"
        )
        return

    await _ensure_locks()
    async with _state_lock:
        if event.chat_id in _active_calls:
            kuning_emoji = vz_emoji.getemoji('kuning')
            await vz_client.edit_with_premium_emoji(event, f"{kuning_emoji} Already connected\n\nVZ ASSISTANT")
            return

    loading_emoji = vz_emoji.getemoji('loading')
    robot_emoji = vz_emoji.getemoji('robot')
    msg = await vz_client.edit_with_premium_emoji(
        event,
        f"{loading_emoji} **JOINING VOICE CHAT**\n\n{robot_emoji} Pure listener mode\n\nVZ ASSISTANT"
    )

    try:
        # Method 1: Raw Telethon (pure listener, zero audio)
        silent_join = await _join_vc_silent(event.client, event.chat_id)

        if not silent_join:
            # Method 2: PyTgCalls fallback with video disabled
            config = GroupCallConfig(auto_start=False) if GroupCallConfig else None

            # Use MediaStream to disable video
            if MediaStream:
                stream = MediaStream(
                    SILENCE_URL,
                    video_flags=MediaStream.Flags.IGNORE
                )
                await voice_client.play(event.chat_id, stream, config=config)
            else:
                await voice_client.play(event.chat_id, SILENCE_URL, config=config)

            try:
                await voice_client.mute(event.chat_id)
            except NotInCallError:
                pass
            await asyncio.sleep(0.1)

        chat = await event.get_chat()
        title = get_display_name(chat) or str(event.chat_id)

        async with _state_lock:
            _active_calls[event.chat_id] = {
                "title": title,
                "joined_at": time.time(),
                "method": "silent" if silent_join else "pytgcalls"
            }

        centang_emoji = vz_emoji.getemoji('centang')
        hijau_emoji = vz_emoji.getemoji('hijau')
        telegram_emoji = vz_emoji.getemoji('telegram')
        petir_emoji = vz_emoji.getemoji('petir')
        main_emoji = vz_emoji.getemoji('utama')

        method = "🎧 Pure Listener" if silent_join else "🔇 Muted Stream"
        response = f"""{centang_emoji} **JOINED VOICE CHAT**

{hijau_emoji} Connected to: {title}
{telegram_emoji} Mode: {method}
{petir_emoji} Zero audio disturbance

{robot_emoji} Plugins Digunakan: **VOICE CHAT**
{petir_emoji} by {main_emoji} Vzoel Fox's Lutpan"""

    except NoActiveGroupCall:
        merah_emoji = vz_emoji.getemoji('merah')
        kuning_emoji = vz_emoji.getemoji('kuning')
        response = f"""{merah_emoji} **JOIN FAILED**

{kuning_emoji} Start the voice chat first

VZ ASSISTANT"""

    except Exception as exc:
        merah_emoji = vz_emoji.getemoji('merah')
        response = f"""{merah_emoji} **JOIN FAILED**

Error: {str(exc)[:80]}

VZ ASSISTANT"""

    await vz_client.edit_with_premium_emoji(msg, response)


@events.register(events.NewMessage(pattern=r'^\.(?:lvc|leavevc)$', outgoing=True))
async def leavevc_handler(event):
    """Leave voice chat."""
    global vz_client, vz_emoji

    try:
        voice_client = await _ensure_voice_client(event.client)
    except Exception:
        merah_emoji = vz_emoji.getemoji('merah')
        await vz_client.edit_with_premium_emoji(event, f"{merah_emoji} PyTgCalls failed\n\nVZ ASSISTANT")
        return

    if voice_client is None:
        merah_emoji = vz_emoji.getemoji('merah')
        await vz_client.edit_with_premium_emoji(event, f"{merah_emoji} PyTgCalls not installed\n\nVZ ASSISTANT")
        return

    await _ensure_locks()
    async with _state_lock:
        if event.chat_id not in _active_calls:
            kuning_emoji = vz_emoji.getemoji('kuning')
            await vz_client.edit_with_premium_emoji(event, f"{kuning_emoji} Not connected to VC\n\nVZ ASSISTANT")
            return

    try:
        async with _state_lock:
            call_info = _active_calls.get(event.chat_id, {})
            method = call_info.get("method", "pytgcalls")

        if method == "silent":
            leave_ok = await _leave_vc_silent(event.client, event.chat_id)
            if not leave_ok and voice_client:
                await voice_client.leave_call(event.chat_id)
        else:
            await voice_client.leave_call(event.chat_id)

        async with _state_lock:
            _active_calls.pop(event.chat_id, None)

        centang_emoji = vz_emoji.getemoji('centang')
        hijau_emoji = vz_emoji.getemoji('hijau')
        robot_emoji = vz_emoji.getemoji('robot')
        petir_emoji = vz_emoji.getemoji('petir')
        main_emoji = vz_emoji.getemoji('utama')

        response = f"""{centang_emoji} **LEFT VOICE CHAT**

{hijau_emoji} Successfully disconnected

{robot_emoji} Plugins Digunakan: **VOICE CHAT**
{petir_emoji} by {main_emoji} Vzoel Fox's Lutpan"""

    except NotInCallError:
        async with _state_lock:
            _active_calls.pop(event.chat_id, None)
        kuning_emoji = vz_emoji.getemoji('kuning')
        response = f"{kuning_emoji} Not in voice chat\n\nVZ ASSISTANT"

    except Exception as exc:
        merah_emoji = vz_emoji.getemoji('merah')
        response = f"{merah_emoji} **LEAVE FAILED**\n\nError: {str(exc)[:80]}\n\nVZ ASSISTANT"

    await vz_client.edit_with_premium_emoji(event, response)


@events.register(events.NewMessage(pattern=r'^\.vcstatus$', outgoing=True))
async def vcstatus_handler(event):
    """Show VC status."""
    global vz_client, vz_emoji

    await _ensure_locks()

    async with _state_lock:
        active_copy = dict(_active_calls)

    main_emoji = vz_emoji.getemoji('utama')
    hijau_emoji = vz_emoji.getemoji('hijau')
    robot_emoji = vz_emoji.getemoji('robot')
    loading_emoji = vz_emoji.getemoji('loading')
    telegram_emoji = vz_emoji.getemoji('telegram')

    status = [
        f"{main_emoji} **VOICE CHAT STATUS**",
        "",
        f"{hijau_emoji} PyTgCalls: {'Ready' if PYTGCALLS_AVAILABLE else 'Missing'}",
        f"{robot_emoji} Client: {'Started' if _voice_client else 'No'}",
        f"{loading_emoji} Active calls: {len(active_copy)}"
    ]

    if active_copy:
        status.append("")
        status.append(f"{telegram_emoji} **Sessions:**")
        now = time.time()
        for chat_id, info in active_copy.items():
            title = info.get("title", str(chat_id))
            joined_at = info.get("joined_at")
            method = info.get("method", "unknown")

            if isinstance(joined_at, (int, float)):
                duration = int(now - joined_at)
                m, s = divmod(duration, 60)
                h, m = divmod(m, 60)
                uptime = f"{h:02d}:{m:02d}:{s:02d}"
            else:
                uptime = "--:--"

            mode = "🎧" if method == "silent" else "🔇"
            status.append(f"• {title} — {uptime} ({mode})")

    status.append("")
    status.append("VZ ASSISTANT")

    await vz_client.edit_with_premium_emoji(event, "\n".join(status))
