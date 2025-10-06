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

async def setup_assistant_bot(client: TelegramClient):
    """
    Setup assistant bot - create if not exists, start bot process.

    Flow:
    1. Check .env for ASSISTANT_BOT_TOKEN + ASSISTANT_BOT_USERNAME
    2. If BOTH exist → use directly, skip ALL BotFather operations
    3. If token only → get username from BotFather
    4. If neither → create new bot

    Args:
        client: Telethon client instance

    Returns:
        bool: True if bot is ready, False otherwise
    """
    # Reload .env to get latest values
    from dotenv import load_dotenv, dotenv_values

    # Find .env file
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    if not os.path.exists(env_path):
        env_path = os.path.join(os.getcwd(), ".env")

    print(f"📁 Loading .env from: {env_path}")

    if os.path.exists(env_path):
        # Read .env directly to get values
        env_values = dotenv_values(env_path)

        # Get token and username from .env file directly (not os.getenv)
        bot_token = env_values.get("ASSISTANT_BOT_TOKEN")
        bot_username = env_values.get("ASSISTANT_BOT_USERNAME", "").lstrip("@")

        print(f"📋 Token from .env: {bot_token[:20] + '...' if bot_token else 'NOT FOUND'}")
        print(f"📋 Username from .env: @{bot_username if bot_username else 'NOT FOUND'}")
    else:
        print(f"❌ .env file not found at {env_path}")
        bot_token = None
        bot_username = None

    botfather = BotFatherClient(client)

    # SIMPLE FLOW: If token+username in .env, use directly
    if bot_token and bot_username:
        print(f"✅ Bot configured in .env:")
        print(f"   Token: {bot_token[:20]}...")
        print(f"   Username: @{bot_username}")
        print("✅ Skipping all BotFather operations - using .env values")

        # Check if description already set
        if _check_bot_setup_completed(bot_username):
            print("✅ Bot already configured")
        else:
            print("📝 Setting bot description...")
            try:
                # Check for rate limit first
                await client.send_message(botfather.BOTFATHER_USERNAME, "/cancel")
                await botfather._wait_for_response(timeout=5)

                await botfather._set_bot_description(bot_username)
                _mark_bot_setup_completed(bot_username)
            except Exception as e:
                print(f"⚠️  Could not set description: {e}")
                print("💡 Bot will still start - description update not critical")

    if not bot_token:
        print("\n🤖 Assistant Bot Token not configured")
        print("🔍 Checking existing bots...")

        # Step 1: Check if username is in .env (use that to get token)
        if bot_username:
            print(f"📋 Username from .env: @{bot_username}")
            print(f"🔑 Getting token for @{bot_username}...")

            # Get token directly for this username
            bot_token = await botfather.get_token_from_botfather(bot_username)

            if bot_token:
                print(f"✅ Token retrieved: {bot_token[:20]}...")

                # Check if description already set
                if _check_bot_setup_completed(bot_username):
                    print("✅ Bot already configured")
                else:
                    print("📝 Setting bot description...")
                    await botfather._set_bot_description(bot_username)
                    _mark_bot_setup_completed(bot_username)
            else:
                print(f"⚠️  Could not get token for @{bot_username}")
                print("🔍 Will search for bots with pattern instead...")
                bot_username = None  # Reset for search

        # Step 2: If no token yet, search for bot with pattern
        if not bot_token:
            # Use base pattern that matches multiple variants
            existing_bot = await botfather.find_existing_bot("vzoelversi")

            if existing_bot:
                print(f"✅ Found existing bot: @{existing_bot}")
                print("🔑 Getting token from BotFather...")

                # Try to get token
                bot_token = await botfather.get_token_from_botfather(existing_bot)

                if bot_token:
                    bot_username = existing_bot
                    print(f"✅ Token retrieved: {bot_token[:20]}...")

                    # Check if description already set
                    if _check_bot_setup_completed(bot_username):
                        print("✅ Bot already configured - skipping description update")
                    else:
                        print("📝 Setting bot description...")
                        await botfather._set_bot_description(bot_username)
                        _mark_bot_setup_completed(bot_username)
                else:
                    print("⚠️  Could not retrieve token")

        # Step 3: If still no token, create new bot (LAST RESORT)
        if not bot_token:
            print("📝 Creating new bot via BotFather...")

            # Create bot via BotFather
            bot_token, bot_username = await botfather.create_assistant_bot()

            if not bot_token:
                print("❌ Failed to create assistant bot")
                return False

            print(f"✅ Bot created: @{bot_username}")
            print(f"🔑 Token: {bot_token[:20]}...")

            # Mark as completed (description was set during creation)
            _mark_bot_setup_completed(bot_username)

        # Save token and username to .env
        if bot_token and bot_username:
            env_path = os.path.join(os.getcwd(), ".env")

            # Read existing .env
            env_content = ""
            if os.path.exists(env_path):
                with open(env_path, "r") as f:
                    env_content = f.read()

            # Add or update token
            if "ASSISTANT_BOT_TOKEN=" in env_content:
                lines = env_content.split("\n")
                for i, line in enumerate(lines):
                    if line.startswith("ASSISTANT_BOT_TOKEN="):
                        lines[i] = f"ASSISTANT_BOT_TOKEN={bot_token}"
                env_content = "\n".join(lines)
            else:
                env_content += f"\nASSISTANT_BOT_TOKEN={bot_token}\n"

            # Add or update username
            if "ASSISTANT_BOT_USERNAME=" in env_content:
                lines = env_content.split("\n")
                for i, line in enumerate(lines):
                    if line.startswith("ASSISTANT_BOT_USERNAME="):
                        lines[i] = f"ASSISTANT_BOT_USERNAME={bot_username}"
                env_content = "\n".join(lines)
            else:
                env_content += f"ASSISTANT_BOT_USERNAME={bot_username}\n"

            # Write back
            with open(env_path, "w") as f:
                f.write(env_content)

            print(f"✅ Token and username saved to .env")

            # Update environment
            os.environ["ASSISTANT_BOT_TOKEN"] = bot_token
            os.environ["ASSISTANT_BOT_USERNAME"] = bot_username

    # Start assistant bot process
    print("🚀 Starting Assistant Bot...")

    try:
        import subprocess

        script_path = os.path.join(os.getcwd(), "assistant_bot_pyrogram.py")

        if not os.path.exists(script_path):
            print(f"❌ Bot script not found: {script_path}")
            return False

        # Try PM2 first
        try:
            # Stop existing if running
            subprocess.run(
                ["pm2", "delete", "vz-assistant"],
                capture_output=True,
                stderr=subprocess.DEVNULL
            )

            # Start new
            result = subprocess.run(
                ["pm2", "start", script_path, "--name", "vz-assistant", "--interpreter", "python3"],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                print("✅ Assistant Bot started via PM2")
                return True

        except FileNotFoundError:
            # PM2 not installed, use background process
            subprocess.Popen(
                ["python3", script_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )
            print("✅ Assistant Bot started (background process)")
            return True

    except Exception as e:
        print(f"❌ Error starting assistant bot: {e}")
        return False

    return True
