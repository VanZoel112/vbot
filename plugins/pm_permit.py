"""
VZ ASSISTANT v0.0.0.69
PM Permit Plugin - Private Message Protection

Commands:
- .pmon - Enable PM permit
- .pmoff - Disable PM permit
- .ok / .approve - Approve user
- .no / .disapprove - Disapprove user

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

# PM permit data file
PM_DATA_FILE = "data/pm_permit.json"

# Default PM permit message
DEFAULT_PM_MESSAGE = """
⚠️ **PM SECURITY SYSTEM**

Halo! Saya sedang sibuk sekarang.
Tolong tunggu sampai owner menyetujui chat ini.

**Jangan spam**, atau Anda akan diblokir!

~VZ ASSISTANT
"""


def load_pm_data():
    """Load PM permit data."""
    if not os.path.exists(PM_DATA_FILE):
        return {
            "enabled": False,
            "approved": [],  # List of approved user IDs
            "warned": {}     # Dict of {user_id: warn_count}
        }

    try:
        with open(PM_DATA_FILE, 'r') as f:
            return json.load(f)
    except:
        return {
            "enabled": False,
            "approved": [],
            "warned": {}
        }


def save_pm_data(data):
    """Save PM permit data."""
    os.makedirs(os.path.dirname(PM_DATA_FILE), exist_ok=True)
    with open(PM_DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)


# ============================================================================
# PM GUARD - Auto respond to unapproved users
# ============================================================================

@events.register(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def pm_guard_handler(event):
    """Auto-respond to unapproved PMs."""
    global vz_client, vz_emoji

    # Skip if not a user (bots, channels, etc)
    if not isinstance(event.sender, User):
        return

    # Skip if bot/deleted account
    if event.sender.bot or event.sender.deleted:
        return

    # Load PM data
    pm_data = load_pm_data()

    # Skip if PM permit disabled
    if not pm_data.get("enabled", False):
        return

    user_id = event.sender_id

    # Skip if user is approved or developer
    if user_id in pm_data.get("approved", []) or config.is_developer(user_id):
        return

    # Get warn count
    warned = pm_data.get("warned", {})
    warn_count = warned.get(str(user_id), 0)

    # Block after 3 warnings
    if warn_count >= 3:
        await event.client.block(user_id)
        # Send block notification to self
        try:
            me = await event.client.get_me()
            await event.client.send_message(
                me.id,
                f"🚫 **User Blocked**\n\nUser ID: `{user_id}`\nReason: Exceeded PM warnings (3)\n\nVZ ASSISTANT"
            )
        except:
            pass
        return

    # Send warning
    warn_count += 1
    warned[str(user_id)] = warn_count
    pm_data["warned"] = warned
    save_pm_data(pm_data)

    warning_msg = DEFAULT_PM_MESSAGE + f"\n\n⚠️ Peringatan: {warn_count}/3"

    try:
        await event.reply(warning_msg)
    except:
        pass


# ============================================================================
# PM ON COMMAND
# ============================================================================

@events.register(events.NewMessage(pattern=r'^\.pmon$', outgoing=True))
async def pmon_handler(event):
    """Enable PM permit."""
    global vz_client, vz_emoji

    pm_data = load_pm_data()

    if pm_data.get("enabled", False):
        kuning_emoji = vz_emoji.getemoji('kuning')
        await vz_client.edit_with_premium_emoji(
            event,
            f"{kuning_emoji} PM Permit sudah aktif\n\nVZ ASSISTANT"
        )
        return

    pm_data["enabled"] = True
    save_pm_data(pm_data)

    centang_emoji = vz_emoji.getemoji('centang')
    hijau_emoji = vz_emoji.getemoji('hijau')
    robot_emoji = vz_emoji.getemoji('robot')
    petir_emoji = vz_emoji.getemoji('petir')
    main_emoji = vz_emoji.getemoji('utama')

    response = f"""{centang_emoji} **PM PERMIT ENABLED**

{hijau_emoji} Private message protection aktif
{robot_emoji} Unapproved users akan diberi warning
⚠️ Setelah 3 warning → auto block

**Commands:**
• `.ok` / `.approve` - Approve user
• `.no` / `.disapprove` - Disapprove user
• `.pmoff` - Disable PM permit

{robot_emoji} Plugins Digunakan: **PM PERMIT**
{petir_emoji} by {main_emoji} Vzoel Fox's Lutpan"""

    await vz_client.edit_with_premium_emoji(event, response)


# ============================================================================
# PM OFF COMMAND
# ============================================================================

@events.register(events.NewMessage(pattern=r'^\.pmoff$', outgoing=True))
async def pmoff_handler(event):
    """Disable PM permit."""
    global vz_client, vz_emoji

    pm_data = load_pm_data()

    if not pm_data.get("enabled", False):
        kuning_emoji = vz_emoji.getemoji('kuning')
        await vz_client.edit_with_premium_emoji(
            event,
            f"{kuning_emoji} PM Permit sudah nonaktif\n\nVZ ASSISTANT"
        )
        return

    pm_data["enabled"] = False
    save_pm_data(pm_data)

    centang_emoji = vz_emoji.getemoji('centang')
    merah_emoji = vz_emoji.getemoji('merah')
    robot_emoji = vz_emoji.getemoji('robot')
    petir_emoji = vz_emoji.getemoji('petir')
    main_emoji = vz_emoji.getemoji('utama')

    response = f"""{centang_emoji} **PM PERMIT DISABLED**

{merah_emoji} Private message protection nonaktif
{robot_emoji} Semua user bisa PM tanpa approval

{robot_emoji} Plugins Digunakan: **PM PERMIT**
{petir_emoji} by {main_emoji} Vzoel Fox's Lutpan"""

    await vz_client.edit_with_premium_emoji(event, response)


# ============================================================================
# APPROVE COMMAND (.ok)
# ============================================================================

@events.register(events.NewMessage(pattern=r'^\.(?:ok|approve)$', outgoing=True))
async def approve_handler(event):
    """Approve user in PM."""
    global vz_client, vz_emoji

    # Must be used in PM
    if not event.is_private:
        kuning_emoji = vz_emoji.getemoji('kuning')
        await vz_client.edit_with_premium_emoji(
            event,
            f"{kuning_emoji} Command ini hanya untuk PM\n\nVZ ASSISTANT"
        )
        return

    # Must be reply
    if not event.is_reply:
        kuning_emoji = vz_emoji.getemoji('kuning')
        await vz_client.edit_with_premium_emoji(
            event,
            f"{kuning_emoji} Reply ke pesan user untuk approve\n\nVZ ASSISTANT"
        )
        return

    # Get user from chat
    user_id = event.chat_id

    # Load PM data
    pm_data = load_pm_data()

    # Add to approved list
    if user_id not in pm_data.get("approved", []):
        if "approved" not in pm_data:
            pm_data["approved"] = []
        pm_data["approved"].append(user_id)

    # Clear warnings
    if "warned" in pm_data and str(user_id) in pm_data["warned"]:
        del pm_data["warned"][str(user_id)]

    save_pm_data(pm_data)

    # Get user info
    try:
        user = await event.client.get_entity(user_id)
        user_name = user.first_name
    except:
        user_name = f"User {user_id}"

    centang_emoji = vz_emoji.getemoji('centang')
    hijau_emoji = vz_emoji.getemoji('hijau')
    robot_emoji = vz_emoji.getemoji('robot')
    petir_emoji = vz_emoji.getemoji('petir')
    main_emoji = vz_emoji.getemoji('utama')

    response = f"""{centang_emoji} **USER APPROVED**

{hijau_emoji} User: {user_name}
{robot_emoji} ID: `{user_id}`

User ini sekarang bisa PM tanpa warning

{robot_emoji} Plugins Digunakan: **PM PERMIT**
{petir_emoji} by {main_emoji} Vzoel Fox's Lutpan"""

    await vz_client.edit_with_premium_emoji(event, response)


# ============================================================================
# DISAPPROVE COMMAND (.no)
# ============================================================================

@events.register(events.NewMessage(pattern=r'^\.(?:no|disapprove)$', outgoing=True))
async def disapprove_handler(event):
    """Disapprove user in PM."""
    global vz_client, vz_emoji

    # Must be used in PM
    if not event.is_private:
        kuning_emoji = vz_emoji.getemoji('kuning')
        await vz_client.edit_with_premium_emoji(
            event,
            f"{kuning_emoji} Command ini hanya untuk PM\n\nVZ ASSISTANT"
        )
        return

    # Must be reply
    if not event.is_reply:
        kuning_emoji = vz_emoji.getemoji('kuning')
        await vz_client.edit_with_premium_emoji(
            event,
            f"{kuning_emoji} Reply ke pesan user untuk disapprove\n\nVZ ASSISTANT"
        )
        return

    # Get user from chat
    user_id = event.chat_id

    # Load PM data
    pm_data = load_pm_data()

    # Remove from approved list
    if user_id in pm_data.get("approved", []):
        pm_data["approved"].remove(user_id)
        save_pm_data(pm_data)

    # Get user info
    try:
        user = await event.client.get_entity(user_id)
        user_name = user.first_name
    except:
        user_name = f"User {user_id}"

    centang_emoji = vz_emoji.getemoji('centang')
    merah_emoji = vz_emoji.getemoji('merah')
    robot_emoji = vz_emoji.getemoji('robot')
    petir_emoji = vz_emoji.getemoji('petir')
    main_emoji = vz_emoji.getemoji('utama')

    response = f"""{centang_emoji} **USER DISAPPROVED**

{merah_emoji} User: {user_name}
{robot_emoji} ID: `{user_id}`

User ini dihapus dari approval list

{robot_emoji} Plugins Digunakan: **PM PERMIT**
{petir_emoji} by {main_emoji} Vzoel Fox's Lutpan"""

    await vz_client.edit_with_premium_emoji(event, response)
