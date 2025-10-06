#!/usr/bin/env python3
"""
Test VC functionality
"""

import asyncio
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioQuality, Stream
from telethon import TelegramClient
from dotenv import load_dotenv
import os

load_dotenv()

async def test_vc():
    # Get session
    session_string = os.getenv('SESSION_STRING')

    if not session_string:
        print("❌ No SESSION_STRING in .env")
        return

    # Create client
    client = TelegramClient(
        "test_vc",
        api_id=int(os.getenv('API_ID', '0')),
        api_hash=os.getenv('API_HASH', '')
    )

    await client.start()

    # Create pytgcalls
    calls = PyTgCalls(client)
    await calls.start()

    print("✅ PyTgCalls started")
    print(f"Client: {client.session.filename}")
    print(f"Is connected: {calls.is_connected}")

    # Test chat ID (replace with your test group)
    chat_id = -1001234567890

    try:
        # Try to join with Stream instead of MediaStream
        await calls.play(
            chat_id,
            Stream(
                "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
                audio_parameters=AudioQuality.STUDIO
            )
        )
        print(f"✅ Joined VC in {chat_id}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(test_vc())
