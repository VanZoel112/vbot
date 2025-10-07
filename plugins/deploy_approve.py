"""
VZ ASSISTANT v0.0.0.69
Deploy Approval Plugin - Approve users for deployment

Commands:
- ..ok - Approve user for deployment (in bot PM)
- ..no - Disapprove user
- ..approvedlist - List approved users
- ..deploystatus - Check bot status

2025© Vzoel Fox's Lutpan
Founder & DEVELOPER : @VZLfxs
"""

import json
import os
from telethon import events
from telethon.tl.types import User
import config

# Global variables (set by main.py)
vz_client = None
vz_emoji = None

# Data file
APPROVED_USERS_FILE = "data/approved_users.json"
DEPLOYER_BOT_USERNAME = "vzdeployertest_bot"  # Update with your deployer bot username


def load_approved_users():
    """Load approved users data."""
    if not os.path.exists(APPROVED_USERS_FILE):
        return {"approved": []}

    try:
        with open(APPROVED_USERS_FILE, 'r') as f:
            return json.load(f)
    except:
        return {"approved": []}


def save_approved_users(data):
    """Save approved users data."""
    os.makedirs(os.path.dirname(APPROVED_USERS_FILE), exist_ok=True)
    with open(APPROVED_USERS_FILE, 'w') as f:
        json.dump(data, f, indent=2)


# ============================================================================
# APPROVE COMMAND (..ok)
# ============================================================================

@events.register(events.NewMessage(pattern=r'^\\.\\.\\.ok$', outgoing=True))
async def approve_deploy_handler(event):
    """Approve user for deployment (developer only)."""
    global vz_client, vz_emoji

    # Check if developer
    if event.sender_id not in config.DEVELOPER_IDS:
        merah_emoji = vz_emoji.getemoji('merah')
        await vz_client.edit_with_premium_emoji(
            event,
            f"{merah_emoji} Developer only command\\n\\nVZ ASSISTANT"
        )
        return

    # Must be used in PM
    if not event.is_private:
        kuning_emoji = vz_emoji.getemoji('kuning')
        await vz_client.edit_with_premium_emoji(
            event,
            f"{kuning_emoji} Command ini hanya untuk PM bot deployer\\n\\nVZ ASSISTANT"
        )
        return

    # Get chat (should be deployer bot)
    chat = await event.get_chat()

    # Check if bot
    if not isinstance(chat, User) or not chat.bot:
        kuning_emoji = vz_emoji.getemoji('kuning')
        await vz_client.edit_with_premium_emoji(
            event,
            f"{kuning_emoji} Command ini hanya untuk PM dengan bot deployer\\n\\nVZ ASSISTANT"
        )
        return

    # Get user ID from chat - this is the USER who sent message to bot
    # We need to get this from the chat context
    # For now, we'll approve based on forwarded message or reply

    if not event.is_reply:
        kuning_emoji = vz_emoji.getemoji('kuning')
        await vz_client.edit_with_premium_emoji(
            event,
            f"{kuning_emoji} Reply ke pesan user untuk approve\\n\\nVZ ASSISTANT"
        )
        return

    # Get replied message
    replied = await event.get_reply_message()

    # Try to extract user ID from message text
    import re
    user_id_match = re.search(r'User ID.*?`(\\d+)`', replied.text)

    if not user_id_match:
        merah_emoji = vz_emoji.getemoji('merah')
        await vz_client.edit_with_premium_emoji(
            event,
            f"{merah_emoji} Tidak dapat menemukan User ID\\n\\nVZ ASSISTANT"
        )
        return

    user_id = int(user_id_match.group(1))

    # Load approved users
    approved = load_approved_users()

    # Add to approved list
    if user_id not in approved.get("approved", []):
        if "approved" not in approved:
            approved["approved"] = []
        approved["approved"].append(user_id)
        save_approved_users(approved)

        centang_emoji = vz_emoji.getemoji('centang')
        hijau_emoji = vz_emoji.getemoji('hijau')
        robot_emoji = vz_emoji.getemoji('robot')
        petir_emoji = vz_emoji.getemoji('petir')
        main_emoji = vz_emoji.getemoji('utama')

        response = f"""{centang_emoji} **USER APPROVED FOR DEPLOYMENT**

{hijau_emoji} User ID: `{user_id}`
{robot_emoji} Status: Approved

User ini sekarang bisa deploy vbot.

{robot_emoji} Plugins Digunakan: **DEPLOY APPROVE**
{petir_emoji} by {main_emoji} Vzoel Fox's Lutpan"""

        await vz_client.edit_with_premium_emoji(event, response)

    else:
        kuning_emoji = vz_emoji.getemoji('kuning')
        await vz_client.edit_with_premium_emoji(
            event,
            f"{kuning_emoji} User sudah di-approve\\n\\nVZ ASSISTANT"
        )


# ============================================================================
# DISAPPROVE COMMAND (..no)
# ============================================================================

@events.register(events.NewMessage(pattern=r'^\\.\\.\\.no$', outgoing=True))
async def disapprove_deploy_handler(event):
    """Disapprove user for deployment (developer only)."""
    global vz_client, vz_emoji

    # Check if developer
    if event.sender_id not in config.DEVELOPER_IDS:
        merah_emoji = vz_emoji.getemoji('merah')
        await vz_client.edit_with_premium_emoji(
            event,
            f"{merah_emoji} Developer only command\\n\\nVZ ASSISTANT"
        )
        return

    # Must be used in PM
    if not event.is_private:
        kuning_emoji = vz_emoji.getemoji('kuning')
        await vz_client.edit_with_premium_emoji(
            event,
            f"{kuning_emoji} Command ini hanya untuk PM bot deployer\\n\\nVZ ASSISTANT"
        )
        return

    # Get chat (should be deployer bot)
    chat = await event.get_chat()

    # Check if bot
    if not isinstance(chat, User) or not chat.bot:
        kuning_emoji = vz_emoji.getemoji('kuning')
        await vz_client.edit_with_premium_emoji(
            event,
            f"{kuning_emoji} Command ini hanya untuk PM dengan bot deployer\\n\\nVZ ASSISTANT"
        )
        return

    if not event.is_reply:
        kuning_emoji = vz_emoji.getemoji('kuning')
        await vz_client.edit_with_premium_emoji(
            event,
            f"{kuning_emoji} Reply ke pesan user untuk disapprove\\n\\nVZ ASSISTANT"
        )
        return

    # Get replied message
    replied = await event.get_reply_message()

    # Try to extract user ID from message text
    import re
    user_id_match = re.search(r'User ID.*?`(\\d+)`', replied.text)

    if not user_id_match:
        merah_emoji = vz_emoji.getemoji('merah')
        await vz_client.edit_with_premium_emoji(
            event,
            f"{merah_emoji} Tidak dapat menemukan User ID\\n\\nVZ ASSISTANT"
        )
        return

    user_id = int(user_id_match.group(1))

    # Load approved users
    approved = load_approved_users()

    # Remove from approved list
    if user_id in approved.get("approved", []):
        approved["approved"].remove(user_id)
        save_approved_users(approved)

        centang_emoji = vz_emoji.getemoji('centang')
        merah_emoji = vz_emoji.getemoji('merah')
        robot_emoji = vz_emoji.getemoji('robot')
        petir_emoji = vz_emoji.getemoji('petir')
        main_emoji = vz_emoji.getemoji('utama')

        response = f"""{centang_emoji} **USER DISAPPROVED**

{merah_emoji} User ID: `{user_id}`
{robot_emoji} Status: Removed

User ini dihapus dari approval list.

{robot_emoji} Plugins Digunakan: **DEPLOY APPROVE**
{petir_emoji} by {main_emoji} Vzoel Fox's Lutpan"""

        await vz_client.edit_with_premium_emoji(event, response)

    else:
        kuning_emoji = vz_emoji.getemoji('kuning')
        await vz_client.edit_with_premium_emoji(
            event,
            f"{kuning_emoji} User tidak ada di approval list\\n\\nVZ ASSISTANT"
        )


# ============================================================================
# APPROVED LIST COMMAND
# ============================================================================

@events.register(events.NewMessage(pattern=r'^\\.approvedlist$', outgoing=True))
async def approvedlist_handler(event):
    """List all approved users (developer only)."""
    global vz_client, vz_emoji

    # Check if developer
    if event.sender_id not in config.DEVELOPER_IDS:
        merah_emoji = vz_emoji.getemoji('merah')
        await vz_client.edit_with_premium_emoji(
            event,
            f"{merah_emoji} Developer only command\\n\\nVZ ASSISTANT"
        )
        return

    approved = load_approved_users()
    approved_list = approved.get("approved", [])

    if not approved_list:
        kuning_emoji = vz_emoji.getemoji('kuning')
        await vz_client.edit_with_premium_emoji(
            event,
            f"{kuning_emoji} Tidak ada user yang di-approve\\n\\nVZ ASSISTANT"
        )
        return

    main_emoji = vz_emoji.getemoji('utama')
    robot_emoji = vz_emoji.getemoji('robot')
    hijau_emoji = vz_emoji.getemoji('hijau')
    petir_emoji = vz_emoji.getemoji('petir')

    response = [f"{main_emoji} **APPROVED USERS**\\n"]

    for uid in approved_list:
        try:
            user = await event.client.get_entity(uid)
            name = user.first_name
            username = f"@{user.username}" if user.username else "No username"
            response.append(f"{hijau_emoji} {name} ({username})")
            response.append(f"{robot_emoji} ID: `{uid}`\\n")
        except:
            response.append(f"{hijau_emoji} User `{uid}`\\n")

    response.append(f"{robot_emoji} Total: {len(approved_list)} users")
    response.append("\\nVZ ASSISTANT")

    await vz_client.edit_with_premium_emoji(event, "\\n".join(response))


# ============================================================================
# DEPLOYER BOT STATUS
# ============================================================================

@events.register(events.NewMessage(pattern=r'^\\.deploystatus$', outgoing=True))
async def deploystatus_handler(event):
    """Check deployer bot status (developer only)."""
    global vz_client, vz_emoji

    # Check if developer
    if event.sender_id not in config.DEVELOPER_IDS:
        merah_emoji = vz_emoji.getemoji('merah')
        await vz_client.edit_with_premium_emoji(
            event,
            f"{merah_emoji} Developer only command\\n\\nVZ ASSISTANT"
        )
        return

    main_emoji = vz_emoji.getemoji('utama')
    robot_emoji = vz_emoji.getemoji('robot')
    hijau_emoji = vz_emoji.getemoji('hijau')
    petir_emoji = vz_emoji.getemoji('petir')

    # Check if deployer bot is online
    try:
        bot = await event.client.get_entity(DEPLOYER_BOT_USERNAME)
        bot_name = bot.first_name
        bot_id = bot.id
        status = "Online" if not bot.status or hasattr(bot.status, 'was_online') else "Offline"
    except:
        bot_name = "Unknown"
        bot_id = "N/A"
        status = "Not Found"

    # Get approved users count
    approved = load_approved_users()
    approved_count = len(approved.get("approved", []))

    response = f"""{main_emoji} **DEPLOYER BOT STATUS**

{robot_emoji} Bot: {bot_name}
{petir_emoji} Username: @{DEPLOYER_BOT_USERNAME}
{hijau_emoji} Status: {status}
{robot_emoji} Approved Users: {approved_count}

Commands:
• `..ok` - Approve user (reply di PM bot)
• `..no` - Disapprove user
• `.approvedlist` - List approved users

VZ ASSISTANT"""

    await vz_client.edit_with_premium_emoji(event, response)
