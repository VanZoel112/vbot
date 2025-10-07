"""
VZ ASSISTANT v0.0.0.69
VC Client - Pyrogram client for pytgcalls
Separate from main Telethon client

2025© Vzoel Fox's Lutpan
Founder & DEVELOPER : @VZLfxs
"""

import os
import logging
from pyrogram import Client
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv()

# Global Pyrogram client instance for VC
_vc_client = None


def get_vc_client():
    """
    Get or create Pyrogram client for VC operations.
    This client is ONLY used for pytgcalls, NOT for commands.
    Main bot uses Telethon for all commands.

    Returns:
        pyrogram.Client: Pyrogram client instance
    """
    global _vc_client

    if _vc_client is not None:
        return _vc_client

    # Get credentials from env
    api_id = os.getenv('API_ID')
    api_hash = os.getenv('API_HASH')
    session_string = os.getenv('SESSION_STRING')

    if not all([api_id, api_hash, session_string]):
        logger.error("Missing API_ID, API_HASH, or SESSION_STRING for VC client")
        return None

    try:
        # Create Pyrogram client from session string
        _vc_client = Client(
            name="vz_vc_client",
            api_id=int(api_id),
            api_hash=api_hash,
            session_string=session_string,
            workdir="sessions",
            in_memory=True  # Don't create session file
        )

        logger.info("VC Pyrogram client created")
        return _vc_client

    except Exception as e:
        logger.error(f"Failed to create VC client: {e}")
        return None


async def start_vc_client():
    """
    Start Pyrogram client for VC.
    Called during bot startup.
    """
    client = get_vc_client()
    if client and not client.is_connected:
        try:
            await client.start()
            logger.info("VC Pyrogram client started")
            me = await client.get_me()
            logger.info(f"VC Client connected as: {me.first_name} (@{me.username})")
            return True
        except Exception as e:
            logger.error(f"Failed to start VC client: {e}")
            return False
    return client is not None


async def stop_vc_client():
    """
    Stop Pyrogram client.
    Called during bot shutdown.
    """
    global _vc_client
    if _vc_client and _vc_client.is_connected:
        try:
            await _vc_client.stop()
            logger.info("VC Pyrogram client stopped")
        except Exception as e:
            logger.error(f"Error stopping VC client: {e}")
    _vc_client = None
