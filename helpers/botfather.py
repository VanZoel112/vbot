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

        Args:
            token: Bot token

        Returns:
            str: Bot username or None
        """
        try:
            # Use pyrogram to get bot info
            from pyrogram import Client as PyrogramClient
            import tempfile

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

                return username

        except Exception as e:
            print(f"⚠️  Could not get bot username: {e}")
            # Fallback: ask BotFather
            try:
                await self.client.send_message(self.BOTFATHER_USERNAME, "/mybots")
                await asyncio.sleep(1.5)
                response = await self._get_latest_message()

                # Try to extract username from response
                if response and "@" in response:
                    lines = response.split("\n")
                    for line in lines:
                        if "@" in line and "bot" in line.lower():
                            # Extract @username
                            parts = line.split("@")
                            if len(parts) > 1:
                                username = parts[1].split()[0].strip()
                                return username
            except:
                pass

            return None

    async def find_existing_bot(self, pattern="vzoelassistant"):
        """
        Find existing bot matching pattern from BotFather.

        Args:
            pattern: Username pattern to match

        Returns:
            str: Bot username if found, None otherwise
        """
        try:
            # Cancel any pending operation first
            await self.client.send_message(self.BOTFATHER_USERNAME, "/cancel")
            await asyncio.sleep(1)

            # Send /mybots
            await self.client.send_message(self.BOTFATHER_USERNAME, "/mybots")
            await asyncio.sleep(2)  # Longer delay for rate limit

            response = await self._get_latest_message()
            if not response:
                print("⚠️  No response from BotFather")
                return None

            print(f"📋 BotFather response: {response[:200]}...")  # Debug

            # Parse bot list
            lines = response.split("\n")
            for line in lines:
                # Look for @username pattern in line
                if "@" in line and pattern.lower() in line.lower():
                    # Try multiple extraction methods
                    # Method 1: Split by @
                    parts = line.split("@")
                    if len(parts) > 1:
                        username = parts[1].split()[0].strip().rstrip(".").rstrip(",")
                        print(f"✅ Found bot: @{username}")
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
            await asyncio.sleep(1)

            # Send /token
            await self.client.send_message(self.BOTFATHER_USERNAME, "/token")
            await asyncio.sleep(2)  # Longer delay

            # Get bot list
            response = await self._get_latest_message()
            if not response or "Choose a bot" not in response:
                print(f"⚠️  Unexpected response from /token: {response[:200] if response else 'None'}")
                return None

            # Send bot username
            await self.client.send_message(self.BOTFATHER_USERNAME, f"@{username}")
            await asyncio.sleep(2.5)  # Longer delay for token retrieval

            # Get token response
            response = await self._get_latest_message()
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

            # Send /newbot command
            await self.client.send_message(self.BOTFATHER_USERNAME, "/newbot")
            await asyncio.sleep(1.5)

            # Get response
            response = await self._get_latest_message()
            if not response or "Alright" not in response:
                return None, None

            # Send bot name
            bot_name = "VZ Assistant"
            await self.client.send_message(self.BOTFATHER_USERNAME, bot_name)
            await asyncio.sleep(1.5)

            # Get response
            response = await self._get_latest_message()
            if not response or "Good" not in response:
                return None, None

            # Send bot username
            await self.client.send_message(self.BOTFATHER_USERNAME, username)
            await asyncio.sleep(2)

            # Get token response
            response = await self._get_latest_message()

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
        # Try base username first
        username = f"{base_username}bot"

        # Add random 4-digit number if needed
        for _ in range(10):  # Max 10 retries
            random_suffix = random.randint(1000, 9999)
            username = f"{base_username}{random_suffix}bot"

            # Check if username is available (simple check)
            try:
                await self.client.send_message(self.BOTFATHER_USERNAME, "/cancel")
                await asyncio.sleep(0.5)
                return username
            except:
                continue

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
            await asyncio.sleep(1)

            # Set description
            await self.client.send_message(self.BOTFATHER_USERNAME, "/setdescription")
            await asyncio.sleep(1.5)

            # Get response and select bot
            response = await self._get_latest_message()
            if response and "Choose a bot" in response:
                await self.client.send_message(self.BOTFATHER_USERNAME, f"@{username}")
                await asyncio.sleep(1.5)

            # Send description
            description = "Asisten untuk VzUserbot.. dengan string Telethone + Uvloop dan Pyrogram + Trio\n\nContact Founder jika menemukan masalah.. OWNER : Vzoel Fox's ( Lutpan ) @VZLfxs @itspizolpoks"
            await self.client.send_message(self.BOTFATHER_USERNAME, description)
            await asyncio.sleep(2)

            # Verify description set
            response = await self._get_latest_message()
            if response and "Success" in response:
                print("✅ Description set")

            # Set about text
            await self.client.send_message(self.BOTFATHER_USERNAME, "/setabouttext")
            await asyncio.sleep(1.5)

            # Get response and select bot
            response = await self._get_latest_message()
            if response and "Choose a bot" in response:
                await self.client.send_message(self.BOTFATHER_USERNAME, f"@{username}")
                await asyncio.sleep(1.5)

            # Send about
            about = "by VzBot"
            await self.client.send_message(self.BOTFATHER_USERNAME, about)
            await asyncio.sleep(2)

            # Verify about set
            response = await self._get_latest_message()
            if response and "Success" in response:
                print("✅ About text set")

            return True

        except Exception as e:
            print(f"⚠️  Could not set bot description: {e}")
            return False


async def setup_assistant_bot(client: TelegramClient):
    """
    Setup assistant bot - create if not exists, start bot process.

    Flow:
    1. Check .env for ASSISTANT_BOT_TOKEN
    2. If exists → verify & update description
    3. If not exists → check existing bots in BotFather (/mybots)
    4. If found existing → get token via /token & save
    5. If not found → create new bot (LAST RESORT)

    Args:
        client: Telethon client instance

    Returns:
        bool: True if bot is ready, False otherwise
    """
    # Check if token already exists
    bot_token = os.getenv("ASSISTANT_BOT_TOKEN")
    botfather = BotFatherClient(client)
    bot_username = None

    # Check for rate limit first
    try:
        await client.send_message(botfather.BOTFATHER_USERNAME, "/cancel")
        await asyncio.sleep(0.5)
        response = await botfather._get_latest_message()
        if response and "too many attempts" in response.lower():
            print("❌ BotFather rate limited!")
            print(f"   Response: {response}")
            print("⚠️  Cannot create/check bots. Please wait and try again later.")
            return False
    except:
        pass

    if bot_token:
        # Token exists - verify and update description
        print(f"✅ Assistant Bot Token found: {bot_token[:20]}...")
        print("📝 Verifying bot...")

        # Get bot username from token
        bot_username = await botfather.get_bot_username_from_token(bot_token)

        if bot_username:
            print(f"🤖 Bot username: @{bot_username}")
            # Set description
            await botfather._set_bot_description(bot_username)
        else:
            print("⚠️  Could not verify bot - token might be invalid")
            # Reset token to try fallback
            bot_token = None

    if not bot_token:
        print("\n🤖 Assistant Bot Token not configured")
        print("🔍 Checking existing bots...")

        # Check for existing bot
        existing_bot = await botfather.find_existing_bot("vzoelassistant")

        if existing_bot:
            print(f"✅ Found existing bot: @{existing_bot}")
            print("🔑 Getting token from BotFather...")

            # Try to get token
            bot_token = await botfather.get_token_from_botfather(existing_bot)

            if bot_token:
                bot_username = existing_bot
                print(f"✅ Token retrieved: {bot_token[:20]}...")
                print("📝 Updating description...")
                await botfather._set_bot_description(bot_username)
            else:
                print("⚠️  Could not retrieve token - will create new bot")
                existing_bot = None

        if not existing_bot:
            print("📝 Creating new bot via BotFather...")

            # Create bot via BotFather
            bot_token, bot_username = await botfather.create_assistant_bot()

            if not bot_token:
                print("❌ Failed to create assistant bot")
                return False

            print(f"✅ Bot created: @{bot_username}")
            print(f"🔑 Token: {bot_token[:20]}...")

        # Save token to .env
        if bot_token:
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

            # Write back
            with open(env_path, "w") as f:
                f.write(env_content)

            print(f"✅ Token saved to .env")

            # Update environment
            os.environ["ASSISTANT_BOT_TOKEN"] = bot_token

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
