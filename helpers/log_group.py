"""
VZ ASSISTANT v0.0.0.69
Log Group Manager - Auto-create or join log group

2025© Vzoel Fox's Lutpan
Founder & DEVELOPER : @VZLfxs
"""

import os
import random
from telethon import TelegramClient
from telethon.tl.functions.channels import CreateChannelRequest, CheckUsernameRequest, UpdateUsernameRequest
from telethon.tl.functions.messages import GetFullChatRequest
from telethon.errors import UsernameOccupiedError, FloodWaitError
import asyncio


class LogGroupManager:
    """Manage log group creation and setup."""

    def __init__(self, client: TelegramClient):
        self.client = client

    async def verify_log_group(self, group_id: int) -> bool:
        """
        Verify if log group exists and is accessible.

        Args:
            group_id: Log group ID

        Returns:
            bool: True if accessible, False otherwise
        """
        try:
            # Try to get group info
            entity = await self.client.get_entity(group_id)

            # Check if we're in the group
            if entity:
                print(f"✅ Log group verified: {entity.title}")
                return True

            return False

        except Exception as e:
            print(f"⚠️  Could not verify log group: {e}")
            return False

    async def create_log_group(self, base_username="vzlog", group_name="Vzoel Logger"):
        """
        Create log group with specific username.

        Args:
            base_username: Base username for group (default: vzlog)
            group_name: Display name for group (default: Vzoel Logger)

        Returns:
            tuple: (group_id, username) or (None, None) if failed
        """
        try:
            username = base_username

            # Create supergroup
            print(f"📝 Creating log group: {group_name}")

            result = await self.client(CreateChannelRequest(
                title=group_name,
                about="VZ Assistant Log Group - Auto-generated logs from userbot",
                megagroup=True  # Supergroup (not channel)
            ))

            # Get created group
            group = result.chats[0]
            group_id = group.id

            print(f"✅ Group created: {group_name} (ID: {group_id})")

            # Set username (try base, then add random if taken)
            username_set = False
            for attempt in range(10):
                try:
                    # Try to set username
                    if attempt > 0:
                        random_suffix = random.randint(100, 999)
                        username = f"{base_username}{random_suffix}"

                    # Check username availability
                    check = await self.client(CheckUsernameRequest(
                        channel=group_id,
                        username=username
                    ))

                    if check:
                        # Set username
                        await self.client(UpdateUsernameRequest(
                            channel=group_id,
                            username=username
                        ))
                        username_set = True
                        print(f"✅ Username set: @{username}")
                        break

                except UsernameOccupiedError:
                    if attempt < 9:
                        continue
                    else:
                        print("⚠️  Could not set username - using without username")
                        username = None
                        break

                except Exception as e:
                    print(f"⚠️  Error setting username: {e}")
                    username = None
                    break

            # Convert to full group ID format (add -100 prefix for supergroups)
            full_group_id = int(f"-100{group_id}")

            return full_group_id, username

        except FloodWaitError as e:
            print(f"⚠️  Rate limited. Wait {e.seconds}s")
            await asyncio.sleep(e.seconds)
            return await self.create_log_group(base_username, group_name)

        except Exception as e:
            print(f"❌ Error creating log group: {e}")
            import traceback
            traceback.print_exc()
            return None, None


def _check_log_group_setup_completed():
    """Check if log group setup is already completed."""
    setup_file = "data/log_group_setup_completed.txt"
    return os.path.exists(setup_file)

def _mark_log_group_setup_completed():
    """Mark log group setup as completed."""
    setup_file = "data/log_group_setup_completed.txt"
    os.makedirs("data", exist_ok=True)
    with open(setup_file, "w") as f:
        f.write("completed")


async def setup_log_group(client: TelegramClient):
    """
    Setup log group - verify or create for assistant bot logging.

    IMPORTANT: This function does NOT make user account join the group.
    Only the ASSISTANT BOT will join and send logs.

    Flow:
    1. Check .env for LOG_GROUP_ID
    2. If exists → verify only (no join) → skip creation
    3. If not exists → create new group for bot to join later
    4. Save to .env

    Args:
        client: Telethon client instance (for verification only)

    Returns:
        bool: True if log group is ready, False otherwise
    """
    # Check if LOG_GROUP_ID already exists
    log_group_id = os.getenv("LOG_GROUP_ID")
    manager = LogGroupManager(client)

    if log_group_id:
        # LOG_GROUP_ID exists - verify and skip creation
        print(f"✅ Log Group ID found: {log_group_id}")

        # Check if already setup
        if _check_log_group_setup_completed():
            print("✅ Log group already configured - ready for logging")
            return True

        # Verify group
        print("📝 Verifying log group...")
        try:
            log_group_id = int(log_group_id)
            verified = await manager.verify_log_group(log_group_id)

            if verified:
                print("✅ Log group verified - ready for logging")
                _mark_log_group_setup_completed()
                return True
            else:
                print("⚠️  Could not verify log group - will create new one")
                log_group_id = None

        except ValueError:
            print("⚠️  Invalid LOG_GROUP_ID format - will create new one")
            log_group_id = None

    if not log_group_id:
        # No LOG_GROUP_ID - create new group
        print("\n📝 Log Group not configured")
        print("🔧 Creating new log group...")

        group_id, username = await manager.create_log_group()

        if not group_id:
            print("❌ Failed to create log group")
            return False

        print(f"✅ Log group created!")
        print(f"   ID: {group_id}")
        if username:
            print(f"   Username: @{username}")

        # Save to .env
        env_path = os.path.join(os.getcwd(), ".env")

        # Read existing .env
        env_content = ""
        if os.path.exists(env_path):
            with open(env_path, "r") as f:
                env_content = f.read()

        # Add or update LOG_GROUP_ID
        if "LOG_GROUP_ID=" in env_content:
            lines = env_content.split("\n")
            for i, line in enumerate(lines):
                if line.startswith("LOG_GROUP_ID="):
                    lines[i] = f"LOG_GROUP_ID={group_id}"
            env_content = "\n".join(lines)
        else:
            env_content += f"\nLOG_GROUP_ID={group_id}\n"

        # Write back
        with open(env_path, "w") as f:
            f.write(env_content)

        print(f"✅ Log Group ID saved to .env")

        # Update environment
        os.environ["LOG_GROUP_ID"] = str(group_id)

        # Mark as completed
        _mark_log_group_setup_completed()

    print("✅ Log group ready for logging")
    return True
