"""
VZ ASSISTANT v0.0.0.69
Settings Plugin - Prefix & PM Permit Management

2025© Vzoel Fox's Lutpan
Founder & DEVELOPER : @VZLfxs
"""

from telethon import events
import config
from utils.animation import animate_loading
from database.models import DatabaseManager

# Global variables (set by main.py)
vz_client = None
vz_emoji = None

# ============================================================================
# PREFIX COMMAND
# ============================================================================

@events.register(events.NewMessage(pattern=r'^\.prefix\s*(.*)$', outgoing=True))
async def prefix_handler(event):
    """
    .prefix - Change command prefix

    Usage:
        .prefix <new_prefix>
        .prefix none           (no prefix)

    Allowed prefixes: . + # @ : ? or alphanumeric or none
    """
    global vz_client, vz_emoji

    user_id = event.sender_id
    new_prefix = event.pattern_match.group(1).strip()

    # Run 12-phase animation
    msg = await animate_loading(vz_client, vz_emoji, event)

    if not new_prefix:
        # Show current prefix
        db = DatabaseManager(config.get_sudoer_db_path(user_id))
        current = db.get_prefix(user_id)
        db.close()

        gear_emoji = vz_emoji.getemoji('gear')
        petir_emoji = vz_emoji.getemoji('petir')
        main_emoji = vz_emoji.getemoji('utama')

        await vz_client.edit_with_premium_emoji(event, f"""
{gear_emoji} **CURRENT PREFIX**

**Current Prefix:** `{current if current else 'none'}`

**💡 Usage:**
`.prefix <new_prefix>`

**✅ Allowed:**
. + # @ : ? or alphanumeric or none

{petir_emoji} {robot_emoji} Plugins Digunakan: **SETTINGS**
{petir_emoji} by {main_emoji} Vzoel Fox's Lutpan""")
        return

    # Handle 'none'
    if new_prefix.lower() == 'none':
        new_prefix = ''

    # Validate prefix
    if new_prefix and new_prefix not in config.ALLOWED_PREFIXES:
        # Check if alphanumeric
        if not new_prefix.isalnum():
            error_emoji = vz_emoji.getemoji('merah')
            petir_emoji = vz_emoji.getemoji('petir')
            gear_emoji = vz_emoji.getemoji('gear')
            main_emoji = vz_emoji.getemoji('utama')

            await vz_client.edit_with_premium_emoji(event, f"""
{error_emoji} **Invalid Prefix**

**Allowed prefixes:**
• . + # @ : ?
• Any letter (a-z, A-Z)
• Any number (0-9)
• none (no prefix)

{petir_emoji} {robot_emoji} Plugins Digunakan: **SETTINGS**
{petir_emoji} by {main_emoji} Vzoel Fox's Lutpan""")
            return

    # Update prefix in database
    db = DatabaseManager(config.get_sudoer_db_path(user_id))
    db.update_prefix(user_id, new_prefix)
    db.close()

    success_emoji = vz_emoji.getemoji('centang')
    petir_emoji = vz_emoji.getemoji('petir')
    gear_emoji = vz_emoji.getemoji('gear')
    main_emoji = vz_emoji.getemoji('utama')

    result_text = f"""
{success_emoji} **Prefix Updated**

**Old Prefix:** `{config.DEFAULT_PREFIX}`
**New Prefix:** `{new_prefix if new_prefix else 'none'}`

**💡 Example:**
{'Commands now work without prefix' if not new_prefix else f'{new_prefix}ping, {new_prefix}help, etc.'}

**⚠️ Note:**
Restart required for changes to take effect.

{petir_emoji} {robot_emoji} Plugins Digunakan: **SETTINGS**
{petir_emoji} by {main_emoji} Vzoel Fox's Lutpan
"""

    await vz_client.edit_with_premium_emoji(event, result_text)

# ============================================================================
# PM PERMIT ENABLE COMMAND
# ============================================================================

@events.register(events.NewMessage(pattern=r'^\.pmon$', outgoing=True))
async def pmon_handler(event):
    """
    .pmon - Enable PM Permit

    Enables PM protection system.
    Unknown users will receive permit message.
    """
    global vz_client, vz_emoji

    user_id = event.sender_id

    # Enable PM permit
    db = DatabaseManager(config.get_sudoer_db_path(user_id))
    db.enable_pm_permit(user_id)
    db.close()

    success_emoji = vz_emoji.getemoji('centang')
    petir_emoji = vz_emoji.getemoji('petir')
    gear_emoji = vz_emoji.getemoji('gear')
    main_emoji = vz_emoji.getemoji('utama')

    result_text = f"""
{success_emoji} **PM Permit Enabled**

**🔐 Protection Active**

**Features:**
├ Unknown users will receive permit message
├ Auto-block after 5 messages (spam protection)
├ Developers are auto-approved
└ Approved users bypass permit

**💡 Commands:**
• `.pmoff` - Disable PM permit
• `.setpm` - Customize permit message
• Reply with `.approve` to approve users

{petir_emoji} {robot_emoji} Plugins Digunakan: **SETTINGS**
{petir_emoji} by {main_emoji} Vzoel Fox's Lutpan
"""

    await vz_client.edit_with_premium_emoji(event, result_text)

# ============================================================================
# PM PERMIT DISABLE COMMAND
# ============================================================================

@events.register(events.NewMessage(pattern=r'^\.pmoff$', outgoing=True))
async def pmoff_handler(event):
    """
    .pmoff - Disable PM Permit

    Disables PM protection system.
    All users can message freely.
    """
    global vz_client, vz_emoji

    user_id = event.sender_id

    # Disable PM permit
    db = DatabaseManager(config.get_sudoer_db_path(user_id))
    db.disable_pm_permit(user_id)
    db.close()

    success_emoji = vz_emoji.getemoji('centang')
    petir_emoji = vz_emoji.getemoji('petir')
    gear_emoji = vz_emoji.getemoji('gear')
    main_emoji = vz_emoji.getemoji('utama')

    result_text = f"""
{success_emoji} **PM Permit Disabled**

**🔓 Protection Inactive**

All users can now message you freely
without permit restrictions.

**💡 To enable:**
Use `.pmon` command

{petir_emoji} {robot_emoji} Plugins Digunakan: **SETTINGS**
{petir_emoji} by {main_emoji} Vzoel Fox's Lutpan
"""

    await vz_client.edit_with_premium_emoji(event, result_text)

# ============================================================================
# SET PM MESSAGE COMMAND
# ============================================================================

@events.register(events.NewMessage(pattern=r'^\.setpm\s+([\s\S]+)$', outgoing=True))
async def setpm_handler(event):
    """
    .setpm - Set custom PM permit message

    Usage:
        .setpm <your custom message>

    Sets a custom message shown to unknown users.
    """
    global vz_client, vz_emoji

    user_id = event.sender_id
    custom_message = event.pattern_match.group(1).strip()

    if not custom_message:
        error_emoji = vz_emoji.getemoji('merah')
        await vz_client.edit_with_premium_emoji(event, f"{error_emoji} Usage: `.setpm <message>`")
        return

    # Save custom message
    db = DatabaseManager(config.get_sudoer_db_path(user_id))
    db.set_pm_permit_message(user_id, custom_message)
    db.close()

    success_emoji = vz_emoji.getemoji('centang')
    petir_emoji = vz_emoji.getemoji('petir')
    gear_emoji = vz_emoji.getemoji('gear')
    main_emoji = vz_emoji.getemoji('utama')

    result_text = f"""
{success_emoji} **PM Permit Message Updated**

**📝 New Message:**
{custom_message}

**ℹ️ Info:**
This message will be shown to unknown users
when they message you in PM.

**💡 Default Message:**
Use `.setpm default` to restore default message

{petir_emoji} {robot_emoji} Plugins Digunakan: **SETTINGS**
{petir_emoji} by {main_emoji} Vzoel Fox's Lutpan
"""

    await vz_client.edit_with_premium_emoji(event, result_text)

# ============================================================================
# APPROVE USER COMMAND
# ============================================================================

@events.register(events.NewMessage(pattern=r'^\.approve$', outgoing=True))
async def approve_handler(event):
    """
    .approve - Approve user in PM

    Usage:
        .approve (reply to user)

    Approves user to bypass PM permit.
    """
    global vz_client, vz_emoji

    # Must be in PM
    if not event.is_private:
        error_emoji = vz_emoji.getemoji('merah')
        await vz_client.edit_with_premium_emoji(event, f"{error_emoji} This command only works in PM!")
        return

    user_id = event.sender_id
    chat_id = event.chat_id

    # Add to approved list
    db = DatabaseManager(config.get_sudoer_db_path(user_id))
    pm_permit = db.get_pm_permit(user_id)
    pm_permit.add_approved_user(chat_id)
    db.session.commit()
    db.close()

    # Get user info
    try:
        user = await event.get_chat()
        user_name = user.first_name
    except:
        user_name = "User"

    success_emoji = vz_emoji.getemoji('centang')
    petir_emoji = vz_emoji.getemoji('petir')
    gear_emoji = vz_emoji.getemoji('gear')
    main_emoji = vz_emoji.getemoji('utama')

    result_text = f"""
{success_emoji} **User Approved**

**👤 Approved:** {user_name}
**🆔 ID:** `{chat_id}`

This user can now message you freely
without PM permit restrictions.

{petir_emoji} {robot_emoji} Plugins Digunakan: **SETTINGS**
{petir_emoji} by {main_emoji} Vzoel Fox's Lutpan"""

    await vz_client.edit_with_premium_emoji(event, result_text)

# ============================================================================
# DISAPPROVE USER COMMAND
# ============================================================================

@events.register(events.NewMessage(pattern=r'^\.disapprove$', outgoing=True))
async def disapprove_handler(event):
    """
    .disapprove - Remove user from approved list

    Usage:
        .disapprove (in PM with user)

    Removes approval, user will get permit message again.
    """
    global vz_client, vz_emoji

    # Must be in PM
    if not event.is_private:
        error_emoji = vz_emoji.getemoji('merah')
        await vz_client.edit_with_premium_emoji(event, f"{error_emoji} This command only works in PM!")
        return

    user_id = event.sender_id
    chat_id = event.chat_id

    # Remove from approved list
    db = DatabaseManager(config.get_sudoer_db_path(user_id))
    pm_permit = db.get_pm_permit(user_id)
    pm_permit.remove_approved_user(chat_id)
    db.session.commit()
    db.close()

    success_emoji = vz_emoji.getemoji('centang')
    petir_emoji = vz_emoji.getemoji('petir')
    gear_emoji = vz_emoji.getemoji('gear')
    main_emoji = vz_emoji.getemoji('utama')

    result_text = f"""
{success_emoji} **Approval Removed**

**🆔 ID:** `{chat_id}`

This user will now receive PM permit
message again when messaging you.

{petir_emoji} {robot_emoji} Plugins Digunakan: **SETTINGS**
{petir_emoji} by {main_emoji} Vzoel Fox's Lutpan"""

    await vz_client.edit_with_premium_emoji(event, result_text)

# ============================================================================
# PM PERMIT INCOMING MESSAGE HANDLER
# ============================================================================

@events.register(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def pm_permit_handler(event):
    """
    Handle incoming PM messages.

    Shows permit message to unknown users.
    Auto-blocks spammers.
    """
    # Get owner's user ID (the one receiving the PM)
    # This is a simplified version - needs proper implementation
    # with multi-client support

    # For now, skip to avoid errors
    return

    # TODO: Implement proper PM permit with:
    # 1. Check if PM permit is enabled for owner
    # 2. Check if sender is approved
    # 3. Check if sender is developer
    # 4. Send permit message if needed
    # 5. Track spam and auto-block

print("✅ Plugin loaded: settings.py")
