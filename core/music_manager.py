#!/usr/bin/env python3
"""
Music Manager with Voice Chat Streaming
Uses py-tgcalls for real-time audio streaming

Author: VanZoel112
Version: 2.1.0 Python (Streaming) - Pure Userbot
"""

import asyncio
import logging
import os
import time
from typing import Dict, Optional, List
from pathlib import Path
import config

logger = logging.getLogger(__name__)

try:
    import yt_dlp
    YTDLP_AVAILABLE = True
except ImportError:
    YTDLP_AVAILABLE = False
    logger.warning("yt-dlp not available")

try:
    from pytgcalls import PyTgCalls
    from pytgcalls.types import MediaStream, AudioQuality, GroupCallConfig
    PYTGCALLS_AVAILABLE = True
except ImportError:
    PYTGCALLS_AVAILABLE = False
    logger.warning("py-tgcalls not available - install with: pip install py-tgcalls")
    MediaStream = None
    AudioQuality = None
    GroupCallConfig = None

class MusicManager:
    """Music manager with voice chat streaming support"""

    def __init__(self, client):
        self.client = client  # Pure userbot client (untuk messages & voice chat)
        self.download_path = Path("downloads/musik")
        self.download_path.mkdir(parents=True, exist_ok=True)

        # PyTgCalls instance
        self.pytgcalls = None
        self.streaming_available = PYTGCALLS_AVAILABLE and client is not None

        # Queue per chat
        self.queues: Dict[int, List[Dict]] = {}

        # Currently playing
        self.current_song: Dict[int, Dict] = {}

        # Active voice chats
        self.active_calls: Dict[int, bool] = {}

        # Rate limiting
        self.last_request: Dict[int, float] = {}
        self.cooldown_seconds = 3

        # Cache for join_as entity
        self._join_as_cache = None
        self._join_as_resolved = False

        # Initialize PyTgCalls if available
        if self.streaming_available:
            try:
                self.pytgcalls = PyTgCalls(self.client)
                logger.info("PyTgCalls initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize PyTgCalls: {e}")
                self.streaming_available = False

    async def start(self):
        """Start music manager"""
        if self.pytgcalls and self.streaming_available:
            try:
                await self.pytgcalls.start()
                logger.info("🎵 Music streaming system ready (voice chat mode)")
            except Exception as e:
                logger.error(f"Failed to start PyTgCalls: {e}")
                self.streaming_available = False

        if not self.streaming_available:
            logger.info("🎵 Music system ready (download mode - no streaming)")

    async def stop(self):
        """Stop music manager and leave all voice chats"""
        if self.pytgcalls:
            try:
                # Leave all active voice chats
                for chat_id in list(self.active_calls.keys()):
                    await self.leave_voice_chat(chat_id)
                logger.info("Stopped music manager")
            except Exception as e:
                logger.error(f"Error stopping music manager: {e}")

    async def search_song(self, query: str) -> Optional[Dict]:
        """Search for song on YouTube"""
        if not YTDLP_AVAILABLE:
            return None

        try:
            ydl_opts = {
                'format': 'bestaudio/best',
                'noplaylist': True,
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
            }

            # Add cookies
            if Config.YOUTUBE_COOKIES_FROM_BROWSER:
                ydl_opts['cookiesfrombrowser'] = (Config.YOUTUBE_COOKIES_FROM_BROWSER,)
            elif Config.YOUTUBE_COOKIES_FILE and os.path.exists(Config.YOUTUBE_COOKIES_FILE):
                ydl_opts['cookiefile'] = Config.YOUTUBE_COOKIES_FILE

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Search YouTube
                search_query = f"ytsearch:{query}" if not query.startswith('http') else query
                info = ydl.extract_info(search_query, download=False)

                if 'entries' in info:
                    info = info['entries'][0]

                return {
                    'title': info.get('title', 'Unknown'),
                    'url': info.get('url'),
                    'webpage_url': info.get('webpage_url'),
                    'duration': info.get('duration', 0),
                    'thumbnail': info.get('thumbnail'),
                }

        except Exception as e:
            logger.error(f"Error searching song: {e}")
            return None

    async def download_audio(self, url: str, title: str, audio_only: bool = True) -> Optional[str]:
        """Download media from YouTube"""
        if not YTDLP_AVAILABLE:
            return None

        try:
            # Clean title for filename
            safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_'))[:50]
            output_template = str(self.download_path / f"{safe_title}.%(ext)s")

            if audio_only:
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': output_template,
                    'noplaylist': True,
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                    'quiet': True,
                    'no_warnings': True,
                }
                # Add cookies
                if Config.YOUTUBE_COOKIES_FROM_BROWSER:
                    ydl_opts['cookiesfrombrowser'] = (Config.YOUTUBE_COOKIES_FROM_BROWSER,)
                elif Config.YOUTUBE_COOKIES_FILE and os.path.exists(Config.YOUTUBE_COOKIES_FILE):
                    ydl_opts['cookiefile'] = Config.YOUTUBE_COOKIES_FILE
                extensions = ['mp3', 'm4a', 'webm', 'opus']
            else:
                ydl_opts = {
                    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                    'outtmpl': output_template,
                    'noplaylist': True,
                    'merge_output_format': 'mp4',
                    'quiet': True,
                    'no_warnings': True,
                }
                # Add cookies
                if Config.YOUTUBE_COOKIES_FROM_BROWSER:
                    ydl_opts['cookiesfrombrowser'] = (Config.YOUTUBE_COOKIES_FROM_BROWSER,)
                elif Config.YOUTUBE_COOKIES_FILE and os.path.exists(Config.YOUTUBE_COOKIES_FILE):
                    ydl_opts['cookiefile'] = Config.YOUTUBE_COOKIES_FILE
                extensions = ['mp4', 'mkv', 'webm']

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            # Find downloaded file
            for ext in extensions:
                file_path = self.download_path / f"{safe_title}.{ext}"
                if file_path.exists():
                    return str(file_path)

            return None

        except Exception as e:
            logger.error(f"Error downloading media: {e}")
            return None

    async def play_stream(self, chat_id: int, query: str, requester_id: int, audio_only: bool = True) -> Dict:
        """Play media in voice chat (streaming mode) or download if streaming unavailable"""
        # Rate limiting
        current_time = time.time()
        if requester_id in self.last_request:
            if current_time - self.last_request[requester_id] < self.cooldown_seconds:
                return {
                    'success': False,
                    'error': f"Please wait {self.cooldown_seconds} seconds between requests"
                }

        self.last_request[requester_id] = current_time

        try:
            # Search song
            song_info = await self.search_song(query)
            if not song_info:
                return {'success': False, 'error': 'Song not found'}

            # STREAMING MODE - if py-tgcalls available
            if self.streaming_available and self.pytgcalls:
                # Check if already playing in this chat
                if chat_id in self.active_calls and self.active_calls[chat_id]:
                    # Add to queue
                    if chat_id not in self.queues:
                        self.queues[chat_id] = []
                    self.queues[chat_id].append(song_info)
                    return {
                        'success': True,
                        'queued': True,
                        'position': len(self.queues[chat_id]),
                        'song': song_info,
                        'streaming': True
                    }

                # Join voice chat and play
                try:
                    # Use YouTube URL for streaming
                    youtube_url = song_info.get('webpage_url')

                    # Create MediaStream with YouTube URL
                    media_stream = MediaStream(
                        youtube_url,
                        AudioQuality.HIGH
                    )

                    # Build group call config
                    group_config = GroupCallConfig(auto_start=True)

                    # Play in voice chat
                    await self.pytgcalls.play(
                        chat_id,
                        media_stream,
                        config=group_config
                    )

                    self.active_calls[chat_id] = True
                    self.current_song[chat_id] = song_info

                    logger.info(f"Started streaming in chat {chat_id}: {song_info['title']}")

                    return {
                        'success': True,
                        'song': song_info,
                        'streaming': True,
                        'joined_vc': True
                    }

                except Exception as e:
                    logger.error(f"Error starting stream: {e}")
                    # Fallback to download mode
                    self.streaming_available = False

            # DOWNLOAD MODE - fallback if streaming not available
            logger.info("Using download mode (streaming not available)")

            # Check if queue exists
            if chat_id in self.queues and len(self.queues[chat_id]) > 0:
                self.queues[chat_id].append(song_info)
                return {
                    'success': True,
                    'queued': True,
                    'position': len(self.queues[chat_id]),
                    'song': song_info,
                    'streaming': False
                }

            # Download media
            file_path = await self.download_audio(song_info['url'], song_info['title'][:50], audio_only)

            if not file_path:
                media_type = "audio" if audio_only else "video"
                return {'success': False, 'error': f'Failed to download {media_type}'}

            self.current_song[chat_id] = {
                **song_info,
                'file_path': file_path
            }

            return {
                'success': True,
                'song': song_info,
                'file_path': file_path,
                'streaming': False
            }

        except Exception as e:
            logger.error(f"Error in play_stream: {e}")
            return {'success': False, 'error': str(e)}

    async def stop_stream(self, chat_id: int) -> bool:
        """Stop stream and leave voice chat"""
        try:
            # Leave voice chat if in streaming mode
            if self.streaming_available and chat_id in self.active_calls:
                await self.leave_voice_chat(chat_id)

            # Clear queue and current song
            if chat_id in self.queues:
                self.queues[chat_id].clear()
            if chat_id in self.current_song:
                del self.current_song[chat_id]

            return True
        except Exception as e:
            logger.error(f"Error stopping: {e}")
            return False

    async def join_voice_chat(self, chat_id: int) -> bool:
        """Join voice chat without playing"""
        try:
            if not self.streaming_available or not self.pytgcalls:
                return False

            # Check if already in call
            if chat_id in self.active_calls and self.active_calls[chat_id]:
                return True

            # Note: PyTgCalls joins automatically when play() is called
            # This is a placeholder - actual join happens with first play
            logger.info(f"Voice chat connection ready for {chat_id}")
            return True

        except Exception as e:
            logger.error(f"Error preparing voice chat: {e}")
            return False

    async def leave_voice_chat(self, chat_id: int) -> bool:
        """Leave voice chat"""
        try:
            if self.pytgcalls and chat_id in self.active_calls:
                await self.pytgcalls.leave_call(chat_id)
                self.active_calls.pop(chat_id, None)
                logger.info(f"Left voice chat in {chat_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error leaving voice chat: {e}")
            return False

    async def pause_stream(self, chat_id: int) -> bool:
        """Pause current stream"""
        try:
            if self.streaming_available and self.pytgcalls and chat_id in self.active_calls:
                await self.pytgcalls.pause_stream(chat_id)
                logger.info(f"Paused stream in {chat_id}")
                return True
        except Exception as e:
            logger.error(f"Error pausing: {e}")
        return False

    async def resume_stream(self, chat_id: int) -> bool:
        """Resume paused stream"""
        try:
            if self.streaming_available and self.pytgcalls and chat_id in self.active_calls:
                await self.pytgcalls.resume_stream(chat_id)
                logger.info(f"Resumed stream in {chat_id}")
                return True
        except Exception as e:
            logger.error(f"Error resuming: {e}")
        return False

    def get_current_song(self, chat_id: int) -> Optional[Dict]:
        """Get current song"""
        return self.current_song.get(chat_id)

    def get_queue(self, chat_id: int) -> List[Dict]:
        """Get queue"""
        return self.queues.get(chat_id, [])

    def get_stream_stats(self) -> Dict:
        """Get streaming statistics"""
        return {
            'active_songs': len(self.current_song),
            'active_calls': len(self.active_calls),
            'total_queued': sum(len(q) for q in self.queues.values()),
            'mode': 'streaming' if self.streaming_available else 'download',
            'streaming_available': self.streaming_available
        }
