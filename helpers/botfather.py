"""
VZ ASSISTANT v0.0.0.69
BotFather Automation - Auto-create Assistant Bot

2025© Vzoel Fox's Lutpan
Founder & DEVELOPER : @VZLfxs
"""

import asyncio
import random
import os
from telethon import TelegramClient
from telethon.tl.functions.messages import SendMessageRequest
from telethon.errors import FloodWaitError, UsernameOccupiedError


class BotFatherClient:
    """Auto-create bot via BotFather."""

    BOTFATHER_USERNAME = "BotFather"
    BOTFATHER_ID = 93372553

    def __init__(self, client: TelegramClient):
        self.client = client

    async def get_bot_username_from_token(self, token):
        """
        Get bot username from token using Telegram Bot API.
        NEVER calls BotFather - only uses Bot API.

        Args:
            token: Bot token

        Returns:
            str: Bot username or None
        """
        # First check if username is in env (fastest)
        env_username = os.getenv("ASSISTANT_BOT_USERNAME")
        if env_username:
            # Remove @ if present
            env_username = env_username.lstrip("@")
            print(f"✅ Using username from .env: @{env_username}")
            return env_username

        # Try to get from Bot API (no BotFather interaction)
        try:
            # Use pyrogram to get bot info
            from pyrogram import Client as PyrogramClient
            import tempfile

            print("📡 Fetching bot info from Telegram Bot API...")

            # Create temporary pyrogram client
            with tempfile.TemporaryDirectory() as tmpdir:
                bot_client = PyrogramClient(
                    "temp_bot",
                    api_id=29919905,  # Use same API credentials
                    api_hash="717957f0e3ae20a7db004d08b66bfd30",
                    bot_token=token,
                    workdir=tmpdir
                )

                await bot_client.start()
                me = await bot_client.get_me()
                username = me.username
                await bot_client.stop()

                print(f"✅ Got username from Bot API: @{username}")
                return username

        except Exception as e:
            print(f"❌ Could not get bot username from API: {e}")
            print("💡 Tip: Add ASSISTANT_BOT_USERNAME to .env to skip API call")
            return None

    async def find_existing_bot(self, pattern="vzoelversi"):
        """
        Find existing bot matching pattern from BotFather.
        Pattern matching ignores numbers and common suffixes (bot, _bot, etc.)

        Args:
            pattern: Base username pattern to match (e.g., "vzoelversi")

        Returns:
            str: Bot username if found, None otherwise
        """
        try:
            # Cancel any pending operation first
            await self.client.send_message(self.BOTFATHER_USERNAME, "/cancel")
            await self._wait_for_response(timeout=5)

            # Send /mybots and wait for real response
            await self.client.send_message(self.BOTFATHER_USERNAME, "/mybots")
            response = await self._wait_for_response(timeout=10)
            if not response:
                print("⚠️  No response from BotFather")
                return None

            print(f"📋 BotFather response: {response[:200]}...")  # Debug

            # Parse bot list
            lines = response.split("\n")
            for line in lines:
                # Look for @username pattern in line
                if "@" in line:
                    # Extract username
                    parts = line.split("@")
                    if len(parts) > 1:
                        username = parts[1].split()[0].strip().rstrip(".").rstrip(",")

                        # Flexible matching: check if pattern is in username (ignore case)
                        # E.g., "vzoelversi" matches "vzoelversirobot", "vzoelversi123bot", etc.
                        if pattern.lower() in username.lower():
                            print(f"✅ Found bot matching '{pattern}': @{username}")
                            return username

            print(f"❌ No bot matching '{pattern}' found in list")
            return None

        except Exception as e:
            print(f"⚠️  Error finding existing bot: {e}")
            import traceback
            traceback.print_exc()
            return None

    async def get_token_from_botfather(self, username):
        """
        Get bot token from BotFather for specific username.

        Args:
            username: Bot username

        Returns:
            str: Bot token if found, None otherwise
        """
        try:
            # Cancel any pending operation first
            await self.client.send_message(self.BOTFATHER_USERNAME, "/cancel")
            await self._wait_for_response(timeout=5)

            # Send /token and wait for response
            await self.client.send_message(self.BOTFATHER_USERNAME, "/token")
            response = await self._wait_for_response(timeout=10)

            if not response or "Choose a bot" not in response:
                print(f"⚠️  Unexpected response from /token: {response[:200] if response else 'None'}")
                return None

            # Send bot username and wait for token
            await self.client.send_message(self.BOTFATHER_USERNAME, f"@{username}")
            response = await self._wait_for_response(timeout=10)
            if not response:
                print("⚠️  No token response from BotFather")
                return None

            print(f"🔑 Token response received: {response[:100]}...")  # Debug

            # Extract token
            token = self._extract_token(response)
            if token:
                print(f"✅ Token extracted: {token[:20]}...")
            else:
                print("❌ Could not extract token from response")

            return token

        except Exception as e:
            print(f"⚠️  Error getting token from BotFather: {e}")
            import traceback
            traceback.print_exc()
            return None

    async def create_assistant_bot(self, base_username="vzoelassistant"):
        """
        Auto-create assistant bot from BotFather.

        Args:
            base_username: Base username for bot (default: vzoelassistant)

        Returns:
            tuple: (bot_token, bot_username) or (None, None) if failed
        """
        try:
            # Generate unique username
            username = await self._generate_unique_username(base_username)

            # Send /newbot command and wait for response
            await self.client.send_message(self.BOTFATHER_USERNAME, "/newbot")
            response = await self._wait_for_response(timeout=10)
            if not response or "Alright" not in response:
                return None, None

            # Send bot name and wait for response
            bot_name = "VZ Assistant"
            await self.client.send_message(self.BOTFATHER_USERNAME, bot_name)
            response = await self._wait_for_response(timeout=10)
            if not response or "Good" not in response:
                return None, None

            # Send bot username and wait for token
            await self.client.send_message(self.BOTFATHER_USERNAME, username)
            response = await self._wait_for_response(timeout=10)

            if not response:
                return None, None

            # Extract token from response
            token = self._extract_token(response)
            if not token:
                # Check if username taken
                if "already taken" in response.lower() or "occupied" in response.lower():
                    # Retry with new username
                    return await self.create_assistant_bot(base_username)
                return None, None

            # Set bot description
            await self._set_bot_description(username)

            return token, username

        except FloodWaitError as e:
            print(f"⚠️  Rate limited by Telegram. Wait {e.seconds}s")
            await asyncio.sleep(e.seconds)
            return await self.create_assistant_bot(base_username)

        except Exception as e:
            print(f"❌ Error creating bot: {e}")
            return None, None

    async def _generate_unique_username(self, base_username):
        """Generate unique bot username."""
        # Just generate random username - availability will be checked during creation
        random_suffix = random.randint(1000, 9999)
        username = f"{base_username}{random_suffix}bot"
        return username

    async def _get_latest_message(self):
        """Get latest message from BotFather."""
        try:
            messages = await self.client.get_messages(self.BOTFATHER_USERNAME, limit=1)
            if messages and len(messages) > 0:
                return messages[0].text
        except Exception as e:
            print(f"❌ Error getting message: {e}")

        return None

    async def _wait_for_response(self, timeout=10):
        """Wait for new message from BotFather (not just sleep)."""
        try:
            # Get current latest message ID
            messages = await self.client.get_messages(self.BOTFATHER_USERNAME, limit=1)
            last_msg_id = messages[0].id if messages else 0

            # Wait for new message (check every 0.3s)
            for _ in range(int(timeout / 0.3)):
                await asyncio.sleep(0.3)
                messages = await self.client.get_messages(self.BOTFATHER_USERNAME, limit=1)
                if messages and messages[0].id > last_msg_id:
                    return messages[0].text

            # Timeout - return last message anyway
            return messages[0].text if messages else None

        except Exception as e:
            print(f"❌ Error waiting for response: {e}")
            await asyncio.sleep(2)  # Fallback delay
            return await self._get_latest_message()

    def _extract_token(self, message):
        """Extract bot token from BotFather response."""
        if not message:
            return None

        # Token format: 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
        lines = message.split("\n")
        for line in lines:
            if ":" in line and len(line.split(":")) > 1:
                potential_token = line.strip()
                # Basic validation
                parts = potential_token.split(":")
                if len(parts) == 2 and parts[0].isdigit() and len(parts[1]) > 20:
                    return potential_token

        return None

    async def _set_bot_description(self, username):
        """Set bot description and about text."""
        try:
            print(f"📝 Setting bot description for @{username}...")

            # Cancel any ongoing operation
            await self.client.send_message(self.BOTFATHER_USERNAME, "/cancel")
            await self._wait_for_response(timeout=5)

            # Set description
            await self.client.send_message(self.BOTFATHER_USERNAME, "/setdescription")
            response = await self._wait_for_response(timeout=10)

            # Select bot if prompted
            if response and "Choose a bot" in response:
                await self.client.send_message(self.BOTFATHER_USERNAME, f"@{username}")
                await self._wait_for_response(timeout=10)

            # Send description
            description = "Asisten untuk VzUserbot.. dengan string Telethone + Uvloop dan Pyrogram + Trio\n\nContact Founder jika menemukan masalah.. OWNER : Vzoel Fox's ( Lutpan ) @VZLfxs @itspizolpoks"
            await self.client.send_message(self.BOTFATHER_USERNAME, description)
            response = await self._wait_for_response(timeout=10)

            if response and "Success" in response:
                print("✅ Description set")

            # Set about text
            await self.client.send_message(self.BOTFATHER_USERNAME, "/setabouttext")
            response = await self._wait_for_response(timeout=10)

            # Select bot if prompted
            if response and "Choose a bot" in response:
                await self.client.send_message(self.BOTFATHER_USERNAME, f"@{username}")
                await self._wait_for_response(timeout=10)

            # Send about
            about = "by VzBot"
            await self.client.send_message(self.BOTFATHER_USERNAME, about)
            response = await self._wait_for_response(timeout=10)

            if response and "Success" in response:
                print("✅ About text set")

            # Enable inline mode
            await self.client.send_message(self.BOTFATHER_USERNAME, "/setinline")
            response = await self._wait_for_response(timeout=10)

            # Select bot if prompted
            if response and "Choose a bot" in response:
                await self.client.send_message(self.BOTFATHER_USERNAME, f"@{username}")
                await self._wait_for_response(timeout=10)

            # Set inline placeholder text
            inline_placeholder = "Type 'help' for plugin list..."
            await self.client.send_message(self.BOTFATHER_USERNAME, inline_placeholder)
            response = await self._wait_for_response(timeout=10)

            if response and "Success" in response:
                print("✅ Inline mode enabled")

            return True

        except Exception as e:
            print(f"⚠️  Could not set bot description: {e}")
            return False


def _check_bot_setup_completed(bot_username):
    """Check if bot setup (description) is already completed."""
    setup_file = "data/bot_setup_completed.txt"
    if os.path.exists(setup_file):
        with open(setup_file, "r") as f:
            completed_bots = f.read().strip().split("\n")
            return bot_username in completed_bots
    return False

def _mark_bot_setup_completed(bot_username):
    """Mark bot setup (description) as completed."""
    setup_file = "data/bot_setup_completed.txt"
    os.makedirs("data", exist_ok=True)

    # Read existing
    completed_bots = []
    if os.path.exists(setup_file):
        with open(setup_file, "r") as f:
            completed_bots = f.read().strip().split("\n")

    # Add if not exists
    if bot_username not in completed_bots:
        completed_bots.append(bot_username)

    # Write back
    with open(setup_file, "w") as f:
        f.write("\n".join(completed_bots))

def _load_developer_assistant_config():
    """Load developer assistant config from config/developer_assistant.json"""
    import json

    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "developer_assistant.json")

    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️  Error loading developer assistant config: {e}")
            return None
    return None


async def setup_assistant_bot(client: TelegramClient):
    """
    Setup assistant bot with role-based logic.

    Flow:
    - DEVELOPER: Use existing bot (from developer_assistant.json or .env)
    - SUDOER: Auto-create new bot from scratch

    Args:
        client: Telethon client instance

    Returns:
        bool: True if bot is ready, False otherwise
    """
    import config

    # Get current user info
    me = await client.get_me()
    user_id = me.id
    user_id_str = str(user_id)

    print(f"👤 Current user: {me.first_name} (@{me.username}) - ID: {user_id}")

    # Check if user is developer
    is_developer = config.is_developer(user_id)
    role = "DEVELOPER" if is_developer else "SUDOER"
    print(f"🔑 Role: {role}")

    botfather = BotFatherClient(client)
    bot_token = None
    bot_username = None

    # ========================================================================
    # DEVELOPER LOGIC: Use existing bot (shared)
    # ========================================================================
    if is_developer:
        print("\n🔧 DEVELOPER MODE: Using existing bot configuration")

        # 1. Check developer_assistant.json
        dev_config = _load_developer_assistant_config()
        if dev_config and "developers" in dev_config:
            if user_id_str in dev_config["developers"]:
                dev_data = dev_config["developers"][user_id_str]
                bot_config = dev_data.get("assistant_bot", {})

                bot_token = bot_config.get("token")
                bot_username = bot_config.get("username", "").lstrip("@")

                if bot_token and bot_username:
                    print(f"✅ Found in developer_assistant.json")
                    print(f"   Developer: {dev_data.get('name', 'Unknown')}")
                    print(f"   Token: {bot_token[:20]}...")
                    print(f"   Username: @{bot_username}")

        # 2. Fallback to .env
        if not bot_token or not bot_username:
            from dotenv import dotenv_values
            env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
            if not os.path.exists(env_path):
                env_path = os.path.join(os.getcwd(), ".env")

            if os.path.exists(env_path):
                env_values = dotenv_values(env_path)
                bot_token = bot_token or env_values.get("ASSISTANT_BOT_TOKEN")
                bot_username = bot_username or env_values.get("ASSISTANT_BOT_USERNAME", "").lstrip("@")

                if bot_token and bot_username:
                    print(f"✅ Found in .env file")
                    print(f"   Token: {bot_token[:20]}...")
                    print(f"   Username: @{bot_username}")

        # Developer MUST have bot configured
        if not bot_token or not bot_username:
            print("\n❌ ERROR: Developer bot not configured!")
            print("💡 Add bot credentials to config/developer_assistant.json or .env")
            return False

    # ========================================================================
    # SUDOER LOGIC: Auto-create new bot
    # ========================================================================
    else:
        print("\n🔧 SUDOER MODE: Auto-creating new bot")

        # Generate unique bot username
        base_username = "vzoelassistant"
        username_suffix = str(user_id)[-6:]  # Last 6 digits of user ID
        bot_username = f"{base_username}{username_suffix}bot"

        print(f"📝 Bot username: @{bot_username}")
        print(f"🤖 Creating bot via BotFather...")

        # Create bot
        bot_token = await botfather.create_bot_auto(
            bot_name=f"VZ Assistant ({me.first_name})",
            bot_username=bot_username
        )

        if not bot_token:
            print("❌ Failed to create bot")
            return False

        print(f"✅ Bot created successfully!")
        print(f"   Token: {bot_token[:20]}...")

        # Save to .env for next startup
        _save_to_env(bot_token, bot_username)

    # ========================================================================
    # COMMON: Setup bot (description + inline mode)
    # ========================================================================
    print(f"\n📝 Configuring bot @{bot_username}...")

    # Check if already configured
    if _check_bot_setup_completed(bot_username):
        print("✅ Bot already configured (description + inline mode)")
    else:
        print("📝 Setting up bot (description + inline mode)...")
        try:
            # Cancel any ongoing operations
            await client.send_message(botfather.BOTFATHER_USERNAME, "/cancel")
            await botfather._wait_for_response(timeout=5)

            # Set description
            await botfather._set_bot_description(bot_username)

            # Enable inline mode
            print("📝 Enabling inline mode...")
            await client.send_message(botfather.BOTFATHER_USERNAME, "/setinline")
            response = await botfather._wait_for_response(timeout=10)

            if response and "Choose a bot" in response:
                await client.send_message(botfather.BOTFATHER_USERNAME, f"@{bot_username}")
                await botfather._wait_for_response(timeout=10)

                inline_placeholder = "Type 'help' for plugin list..."
                await client.send_message(botfather.BOTFATHER_USERNAME, inline_placeholder)
                response = await botfather._wait_for_response(timeout=10)

                if response and "successfully" in response.lower():
                    print("✅ Inline mode enabled")
                else:
                    print(f"⚠️  Inline mode response: {response}")
            else:
                print(f"⚠️  Unexpected inline mode response: {response}")

            _mark_bot_setup_completed(bot_username)
            print("✅ Bot setup completed")

        except Exception as e:
            print(f"⚠️  Error during bot setup: {e}")
            print("💡 Bot will still start - setup not critical")

    # Save to .env for all users (developer and sudoer)
    _save_to_env(bot_token, bot_username)

    print("\n✅ Assistant bot ready!")
    return True


def _save_to_env(bot_token, bot_username):
    """Save bot credentials to .env file."""
    try:
        from dotenv import set_key

        env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
        if not os.path.exists(env_path):
            env_path = os.path.join(os.getcwd(), ".env")

        # Update or create entries
        set_key(env_path, "ASSISTANT_BOT_TOKEN", bot_token)
        set_key(env_path, "ASSISTANT_BOT_USERNAME", bot_username)

        print(f"✅ Saved to .env: @{bot_username}")

    except Exception as e:
        print(f"⚠️  Could not save to .env: {e}")
