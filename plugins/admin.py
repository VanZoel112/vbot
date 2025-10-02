"""
VZ ASSISTANT v0.0.0.69
Admin Plugin - Admin Management Commands

2025© Vzoel Fox's Lutpan
Founder & DEVELOPER : @VZLfxs
"""

from telethon import events
from telethon.tl.functions.channels import EditAdminRequest
from telethon.tl.types import ChatAdminRights
import config

# Global variables (set by main.py)
vz_client = None
vz_emoji = None

# ============================================================================
# ADMIN COMMAND
# ============================================================================

@events.register(events.NewMessage(pattern=r'^\.admin\s*(@\w+)?\s*(.*)$', outgoing=True))
async def admin_handler(event):
    """
    .admin - Promote user to admin

    Usage:
        .admin @username <title>
        .admin (reply) <title>

    Title is optional, defaults to "admin"
    Requires admin permission to add new admins.
    """
    # Get target and title
    reply = await event.get_reply_message()
    username = event.pattern_match.group(1)
    title = event.pattern_match.group(2).strip()

    if not title:
        title = "admin"

    # Get target user
    if reply:
        target = await reply.get_sender()
    elif username:
        try:
            username = username[1:]  # Remove @
            target = await event.client.get_entity(username)
        except Exception as e:
            await event.edit(f"❌ Failed to get user: {str(e)}")
            return
    else:
        await event.edit("❌ Usage: `.admin @username <title>` or `.admin` (reply) <title>")
        return

    # Check if user is developer (developers can't be promoted)
    if config.is_developer(target.id):
        await event.edit("⚠️ Developers cannot be promoted (already have full access)!")
        return

    await event.edit(f"⚙️ Promoting {target.first_name}...")

    # Set admin rights
    try:
        # Full admin rights
        rights = ChatAdminRights(
            change_info=True,
            post_messages=True,
            edit_messages=True,
            delete_messages=True,
            ban_users=True,
            invite_users=True,
            pin_messages=True,
            add_admins=True,
            manage_call=True,
            other=True
        )

        # Promote user
        await event.client(EditAdminRequest(
            event.chat_id,
            target,
            rights,
            title
        ))

        result_text = f"""
✅ **User Promoted**

**👤 User:**
├ Name: {target.first_name}
├ Username: @{target.username if target.username else 'None'}
├ ID: `{target.id}`
└ Title: {title}

**🔑 Admin Rights:**
├ Change Info: ✅
├ Delete Messages: ✅
├ Ban Users: ✅
├ Invite Users: ✅
├ Pin Messages: ✅
└ Add Admins: ✅

{config.BRANDING_FOOTER} ADMIN
Founder & DEVELOPER : {config.FOUNDER_USERNAME}
"""

        await event.edit(result_text)

    except Exception as e:
        await event.edit(f"❌ Failed to promote user: {str(e)}\n\nMake sure you have 'Add Admin' permission!")

# ============================================================================
# UNADMIN COMMAND
# ============================================================================

@events.register(events.NewMessage(pattern=r'^\.unadmin\s*(@\w+)?$', outgoing=True))
async def unadmin_handler(event):
    """
    .unadmin - Demote admin to regular user

    Usage:
        .unadmin @username
        .unadmin (reply)

    Removes all admin rights.
    Developer users are immune to unadmin.
    """
    # Get target
    reply = await event.get_reply_message()
    username = event.pattern_match.group(1)

    # Get target user
    if reply:
        target = await reply.get_sender()
    elif username:
        try:
            username = username[1:]  # Remove @
            target = await event.client.get_entity(username)
        except Exception as e:
            await event.edit(f"❌ Failed to get user: {str(e)}")
            return
    else:
        await event.edit("❌ Usage: `.unadmin @username` or `.unadmin` (reply)")
        return

    # Check if user is developer (developers can't be demoted)
    if config.is_developer(target.id):
        await event.edit("⚠️ Developers are immune to unadmin!")
        return

    await event.edit(f"⚙️ Demoting {target.first_name}...")

    # Remove admin rights
    try:
        # No admin rights
        rights = ChatAdminRights(
            change_info=False,
            post_messages=False,
            edit_messages=False,
            delete_messages=False,
            ban_users=False,
            invite_users=False,
            pin_messages=False,
            add_admins=False,
            manage_call=False
        )

        # Demote user
        await event.client(EditAdminRequest(
            event.chat_id,
            target,
            rights,
            ""
        ))

        result_text = f"""
✅ **User Demoted**

**👤 User:**
├ Name: {target.first_name}
├ Username: @{target.username if target.username else 'None'}
└ ID: `{target.id}`

**📝 Status:**
All admin rights have been removed.
User is now a regular member.

{config.BRANDING_FOOTER} ADMIN
Founder & DEVELOPER : {config.FOUNDER_USERNAME}
"""

        await event.edit(result_text)

    except Exception as e:
        await event.edit(f"❌ Failed to demote user: {str(e)}\n\nMake sure you have 'Add Admin' permission!")

print("✅ Plugin loaded: admin.py")
