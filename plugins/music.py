"""
VZ ASSISTANT v0.0.0.69
Music Plugin - Pure userbot music with VC streaming

Commands:
- .play <query> - Play/stream music
- .song <query> - Download song
- .pause - Pause stream
- .resume - Resume stream
- .stop - Stop and clear
- .queue - Show queue

2025© Vzoel Fox's Lutpan
Founder & DEVELOPER : @VZLfxs
"""

from telethon import events
import os
from pathlib import Path
import config
from core.music_manager import MusicManager

# Global variables (set by main.py)
vz_client = None
vz_emoji = None
music_manager = None

def format_duration(seconds):
    """Format duration to MM:SS"""
    try:
        if not seconds:
            return "00:00"
        minutes = int(seconds) // 60
        secs = int(seconds) % 60
        return f"{minutes:02d}:{secs:02d}"
    except:
        return "00:00"

# ============================================================================
# PLAY COMMAND
# ============================================================================

@events.register(events.NewMessage(pattern=r'^\.play (.+)$', outgoing=True))
async def play_handler(event):
    """
    .play - Play music

    Usage:
        .play <song name or URL>

    Streams to voice chat if available, otherwise downloads
    """
    global vz_client, vz_emoji, music_manager

    # Initialize music manager if not done
    if music_manager is None:
        try:
            # Get the client from event
            client = event.client
            music_manager = MusicManager(client)
            await music_manager.start()
        except Exception as e:
            merah_emoji = vz_emoji.getemoji('merah')
            await vz_client.edit_with_premium_emoji(
                event,
                f"{merah_emoji} Music system initialization failed: {str(e)[:100]}\n\nVZ ASSISTANT"
            )
            return

    if not music_manager:
        merah_emoji = vz_emoji.getemoji('merah')
        await vz_client.edit_with_premium_emoji(
            event,
            f"{merah_emoji} Music system not initialized\n\nVZ ASSISTANT"
        )
        return

    query = event.pattern_match.group(1).strip()

    loading_emoji = vz_emoji.getemoji('loading')
    proses_emoji = vz_emoji.getemoji('robot')

    processing_msg = f"""{loading_emoji} **PROCESSING**

{proses_emoji} Searching: {query}

VZ ASSISTANT"""
    await vz_client.edit_with_premium_emoji(event, processing_msg)

    result = await music_manager.play_stream(event.chat_id, query, event.sender_id)

    if result['success']:
        song = result['song']
        duration = format_duration(song.get('duration', 0))

        centang_emoji = vz_emoji.getemoji('centang')
        aktif_emoji = vz_emoji.getemoji('aktif')
        proses_emoji = vz_emoji.getemoji('robot')
        kuning_emoji = vz_emoji.getemoji('kuning')
        utama_emoji = vz_emoji.getemoji('utama')
        biru_emoji = vz_emoji.getemoji('camera')

        if result.get('streaming'):
            if result.get('queued'):
                response = f"""{centang_emoji} **QUEUED**

{proses_emoji} {song['title']}
{aktif_emoji} Duration: {duration}
{kuning_emoji} Position: #{result['position']}

VZ ASSISTANT
~2025 by Vzoel Fox's Lutpan"""
            else:
                response = f"""{utama_emoji} **NOW STREAMING**

{proses_emoji} {song['title']}
{aktif_emoji} Duration: {duration}
{centang_emoji} Mode: Voice chat

VZ ASSISTANT
~2025 by Vzoel Fox's Lutpan"""
        else:
            file_path = result.get('file_path', '')
            file_name = Path(file_path).name if file_path else 'Unknown'
            response = f"""{centang_emoji} **DOWNLOADED**

{proses_emoji} {song['title']}
{aktif_emoji} Duration: {duration}
{biru_emoji} File: {file_name}

VZ ASSISTANT
~2025 by Vzoel Fox's Lutpan"""
            await vz_client.edit_with_premium_emoji(event, response)
            if file_path and os.path.exists(file_path):
                try:
                    await event.client.send_file(
                        event.chat_id,
                        file_path,
                        caption=f"{song['title']}\n\nVZ ASSISTANT",
                        reply_to=event.id
                    )
                except:
                    pass
            return

        await vz_client.edit_with_premium_emoji(event, response)
    else:
        error = result.get('error', 'Unknown error')
        merah_emoji = vz_emoji.getemoji('merah')
        kuning_emoji = vz_emoji.getemoji('kuning')

        response = f"""{merah_emoji} **FAILED**

{kuning_emoji} Error: {error}

VZ ASSISTANT"""
        await vz_client.edit_with_premium_emoji(event, response)

# ============================================================================
# SONG COMMAND (Alias for .play)
# ============================================================================

@events.register(events.NewMessage(pattern=r'^\.song (.+)$', outgoing=True))
async def song_handler(event):
    """
    .song - Download song (alias for .play)

    Usage:
        .song <song name or URL>
    """
    await play_handler(event)

# ============================================================================
# PAUSE COMMAND
# ============================================================================

@events.register(events.NewMessage(pattern=r'^\.pause$', outgoing=True))
async def pause_handler(event):
    """
    .pause - Pause playback

    Pauses current streaming music
    """
    global vz_client, vz_emoji, music_manager

    if not music_manager:
        return

    success = await music_manager.pause_stream(event.chat_id)

    centang_emoji = vz_emoji.getemoji('centang')
    aktif_emoji = vz_emoji.getemoji('aktif')
    kuning_emoji = vz_emoji.getemoji('kuning')

    if success:
        response = f"""{centang_emoji} **PAUSED**

{aktif_emoji} Use .resume to continue

VZ ASSISTANT"""
    else:
        response = f"""{kuning_emoji} **NOT PLAYING**

VZ ASSISTANT"""
    await vz_client.edit_with_premium_emoji(event, response)

# ============================================================================
# RESUME COMMAND
# ============================================================================

@events.register(events.NewMessage(pattern=r'^\.resume$', outgoing=True))
async def resume_handler(event):
    """
    .resume - Resume playback

    Resumes paused music
    """
    global vz_client, vz_emoji, music_manager

    if not music_manager:
        return

    success = await music_manager.resume_stream(event.chat_id)

    centang_emoji = vz_emoji.getemoji('centang')
    aktif_emoji = vz_emoji.getemoji('aktif')
    kuning_emoji = vz_emoji.getemoji('kuning')

    if success:
        response = f"""{centang_emoji} **RESUMED**

{aktif_emoji} Now playing

VZ ASSISTANT"""
    else:
        response = f"""{kuning_emoji} **NOT PAUSED**

VZ ASSISTANT"""
    await vz_client.edit_with_premium_emoji(event, response)

# ============================================================================
# STOP COMMAND
# ============================================================================

@events.register(events.NewMessage(pattern=r'^\.stop$', outgoing=True))
async def stop_handler(event):
    """
    .stop - Stop playback

    Stops music and clears queue
    """
    global vz_client, vz_emoji, music_manager

    if not music_manager:
        return

    current = music_manager.get_current_song(event.chat_id)
    success = await music_manager.stop_stream(event.chat_id)

    centang_emoji = vz_emoji.getemoji('centang')
    proses_emoji = vz_emoji.getemoji('robot')
    aktif_emoji = vz_emoji.getemoji('aktif')
    kuning_emoji = vz_emoji.getemoji('kuning')

    if success or current:
        track = current.get('title', 'Unknown') if current else 'Unknown'
        response = f"""{centang_emoji} **STOPPED**

{proses_emoji} Last: {track}
{aktif_emoji} Queue cleared

VZ ASSISTANT"""
    else:
        response = f"""{kuning_emoji} **NOT PLAYING**

VZ ASSISTANT"""
    await vz_client.edit_with_premium_emoji(event, response)

# ============================================================================
# QUEUE COMMAND
# ============================================================================

@events.register(events.NewMessage(pattern=r'^\.queue$', outgoing=True))
async def queue_handler(event):
    """
    .queue - Show queue

    Displays current song and queued songs
    """
    global vz_client, vz_emoji, music_manager

    if not music_manager:
        return

    current = music_manager.get_current_song(event.chat_id)
    queue = music_manager.get_queue(event.chat_id)

    kuning_emoji = vz_emoji.getemoji('kuning')
    telegram_emoji = vz_emoji.getemoji('telegram')
    utama_emoji = vz_emoji.getemoji('utama')
    proses_emoji = vz_emoji.getemoji('robot')
    aktif_emoji = vz_emoji.getemoji('aktif')

    if not current and not queue:
        response = f"""{kuning_emoji} **QUEUE EMPTY**

{telegram_emoji} Use .play to add songs

VZ ASSISTANT"""
    else:
        response = f"""{utama_emoji} **MUSIC QUEUE**\n\n"""
        if current:
            duration = format_duration(current.get('duration', 0))
            response += f"""{proses_emoji} NOW PLAYING:
{current.get('title', 'Unknown')} ({duration})\n\n"""
        if queue:
            response += f"""{aktif_emoji} QUEUE ({len(queue)}):\n"""
            for i, song in enumerate(queue[:5], 1):
                duration = format_duration(song.get('duration', 0))
                response += f"{i}. {song.get('title', 'Unknown')} ({duration})\n"
            if len(queue) > 5:
                response += f"\n{telegram_emoji} +{len(queue) - 5} more\n"
        response += f"\nVZ ASSISTANT\n~2025 by Vzoel Fox's Lutpan"

    await vz_client.edit_with_premium_emoji(event, response)

print("✅ Plugin loaded: music.py")
