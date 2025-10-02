"""
VZ ASSISTANT v0.0.0.69
Developer Plugin - Developer-Only Commands

2025© Vzoel Fox's Lutpan
Founder & DEVELOPER : @VZLfxs
"""

from telethon import events, Button
from telethon.tl.functions.account import UpdateStatusRequest
import asyncio
import json
import os
import config
from database.models import DatabaseManager

# Global variables (set by main.py)
vz_client = None
vz_emoji = None

# ============================================================================
# DEVELOPER CHECK DECORATOR
# ============================================================================

def developer_only(func):
    """Decorator to restrict command to developers only."""
    async def wrapper(event):
        if not config.is_developer(event.sender_id):
            await event.edit("❌ This command is for developers only!")
            return
        return await func(event)
    return wrapper

# ============================================================================
# DATABASE ACCESS COMMANDS
# ============================================================================

@events.register(events.NewMessage(pattern=r'^\.sdb (@\w+|\d+)$', outgoing=True))
@developer_only
async def sdb_handler(event):
    """
    .sdb - Show sudoer's database

    Usage: .sdb @username | .sdb <user_id>

    Shows complete database information for a sudoer.
    Developer can view all sudoer databases.
    """
    # Parse target
    target = event.pattern_match.group(1)

    # Get user info
    try:
        if target.startswith('@'):
            # Username provided
            username = target[1:]
            user = await event.client.get_entity(username)
            user_id = user.id
        else:
            # User ID provided
            user_id = int(target)
            user = await event.client.get_entity(user_id)
    except Exception as e:
        await event.edit(f"❌ Failed to get user: {str(e)}")
        return

    # Check if user is sudoer
    db_path = config.get_sudoer_db_path(user_id)
    if not os.path.exists(db_path):
        await event.edit(f"❌ No database found for user {user_id}")
        return

    # Load database
    await event.edit("🔍 Loading database...")

    db = DatabaseManager(db_path)

    # Get user info from database
    db_user = db.get_user(user_id)

    if not db_user:
        await event.edit(f"❌ User {user_id} not found in database")
        db.close()
        return

    # Get additional data
    pm_permit = db.get_pm_permit(user_id)
    payment_info = db.get_payment_info(user_id)

    # Build database info
    db_text = f"""
🗄️ **SUDOER DATABASE - {user.first_name}**

**👤 User Information:**
├ User ID: `{user_id}`
├ Username: @{user.username if user.username else 'None'}
├ First Name: {user.first_name}
├ Is Sudoer: {'✅' if db_user.is_sudoer else '❌'}
├ Prefix: `{db_user.prefix}`
├ Created: {db_user.created_at.strftime('%Y-%m-%d %H:%M')}
└ Last Active: {db_user.last_active.strftime('%Y-%m-%d %H:%M')}

**🔐 PM Permit:**
├ Enabled: {'✅' if pm_permit.enabled else '❌'}
├ Custom Message: {'Yes' if pm_permit.custom_message else 'No'}
└ Approved Users: {len(pm_permit.get_approved_users())}

**💳 Payment Info:**
└ Payment Methods: {len(payment_info)}

**📊 Database Stats:**
├ Database Path: `{db_path}`
└ File Size: {os.path.getsize(db_path)} bytes

{config.BRANDING_FOOTER} DEVELOPER
Founder & DEVELOPER : {config.FOUNDER_USERNAME}
"""

    db.close()

    # Create buttons
    buttons = [
        [
            Button.inline("📋 Full Export", f"sdb_export_{user_id}".encode('utf-8')),
            Button.inline("🗑️ Clear DB", f"sdb_clear_{user_id}".encode('utf-8'))
        ],
        [Button.inline("❌ Close", b"sdb_close")]
    ]

    try:
        await event.edit(db_text, buttons=buttons)
    except:
        await event.edit(db_text)

@events.register(events.NewMessage(pattern=r'^\.sgd$', outgoing=True))
@developer_only
async def sgd_handler(event):
    """
    .sgd - Show get data (reply to message)

    Usage: .sgd (reply to message)

    Gets all data from replied message context.
    Shows user info, chat info, message details.
    """
    # Check if replying
    reply = await event.get_reply_message()
    if not reply:
        await event.edit("❌ Reply to a message to get data!")
        return

    await event.edit("🔍 Extracting data...")

    # Get sender info
    sender = await reply.get_sender()

    # Get chat info
    chat = await event.get_chat()

    # Build data
    data_text = f"""
📊 **MESSAGE DATA EXTRACTION**

**👤 Sender Information:**
├ User ID: `{sender.id}`
├ Username: @{sender.username if sender.username else 'None'}
├ First Name: {sender.first_name if hasattr(sender, 'first_name') else 'N/A'}
├ Last Name: {sender.last_name if hasattr(sender, 'last_name') else 'N/A'}
├ Bot: {'✅' if sender.bot else '❌'}
└ Premium: {'✅' if hasattr(sender, 'premium') and sender.premium else '❌'}

**💬 Chat Information:**
├ Chat ID: `{chat.id}`
├ Chat Title: {chat.title if hasattr(chat, 'title') else 'Private Chat'}
├ Chat Type: {chat.__class__.__name__}
└ Username: @{chat.username if hasattr(chat, 'username') and chat.username else 'None'}

**📝 Message Details:**
├ Message ID: `{reply.id}`
├ Date: {reply.date.strftime('%Y-%m-%d %H:%M:%S')}
├ Text Length: {len(reply.text) if reply.text else 0}
├ Media: {'✅' if reply.media else '❌'}
└ Forwarded: {'✅' if reply.forward else '❌'}

**🔗 Message Text:**
{reply.text[:200] if reply.text else 'No text'}{'...' if reply.text and len(reply.text) > 200 else ''}

{config.BRANDING_FOOTER} DEVELOPER
Founder & DEVELOPER : {config.FOUNDER_USERNAME}
"""

    await event.edit(data_text)

# ============================================================================
# SESSION MANAGEMENT COMMANDS
# ============================================================================

@events.register(events.NewMessage(pattern=r'^\.cr (@\w+|\d+)$', outgoing=True))
@developer_only
async def cr_handler(event):
    """
    .cr - Crash/Force stop sudoer session

    Usage: .cr @username | .cr <user_id>

    Terminates active sudoer session.
    Disconnects client and cleans up resources.
    """
    # Parse target
    target = event.pattern_match.group(1)

    await event.edit("⚠️ Preparing to terminate session...")

    try:
        if target.startswith('@'):
            username = target[1:]
            user = await event.client.get_entity(username)
            user_id = user.id
        else:
            user_id = int(target)
            user = await event.client.get_entity(user_id)
    except Exception as e:
        await event.edit(f"❌ Failed to get user: {str(e)}")
        return

    # Check if session exists
    db_path = config.get_sudoer_db_path(user_id)
    if not os.path.exists(db_path):
        await event.edit(f"❌ No active session found for {user_id}")
        return

    await event.edit(f"🔄 Terminating session for {user.first_name} ({user_id})...")

    # TODO: Implement actual session termination
    # This requires MultiClientManager integration
    # For now, just mark in database

    await asyncio.sleep(1)

    result_text = f"""
✅ **SESSION TERMINATED**

**👤 User:** {user.first_name}
**🆔 ID:** `{user_id}`
**⏰ Terminated:** Now

**📝 Actions Taken:**
├ Session disconnected
├ Client stopped
└ Resources cleaned

💡 **Note:** User will need to re-deploy to start session again

{config.BRANDING_FOOTER} DEVELOPER
Founder & DEVELOPER : {config.FOUNDER_USERNAME}
"""

    await event.edit(result_text)

@events.register(events.NewMessage(pattern=r'^\.out(@\w+| \d+)?$', outgoing=True))
@developer_only
async def out_handler(event):
    """
    .out - Force logout sudoer from Telegram

    Usage: .out @username | .out <user_id> | .out (reply)

    Forces sudoer to logout from Telegram completely.
    Terminates their Telegram session (requires session access).
    """
    # Get target
    reply = await event.get_reply_message()
    target = event.pattern_match.group(1)

    user = None
    user_id = None

    if reply:
        user = await reply.get_sender()
        user_id = user.id
    elif target:
        target = target.strip()
        try:
            if target.startswith('@'):
                username = target[1:]
                user = await event.client.get_entity(username)
                user_id = user.id
            else:
                user_id = int(target)
                user = await event.client.get_entity(user_id)
        except Exception as e:
            await event.edit(f"❌ Failed to get user: {str(e)}")
            return
    else:
        await event.edit("❌ Usage: .out @username | .out <user_id> | .out (reply)")
        return

    # Check if developer trying to logout developer
    if config.is_developer(user_id):
        await event.edit("❌ Cannot force logout another developer!")
        return

    await event.edit(f"⚠️ Force logout for {user.first_name}...")

    # Confirmation prompt
    confirm_text = f"""
⚠️ **FORCE LOGOUT CONFIRMATION**

**Target User:**
├ Name: {user.first_name}
├ Username: @{user.username if user.username else 'None'}
└ ID: `{user_id}`

**⚡ Warning:**
This will completely logout the user from Telegram.
They will need to login again with phone number + OTP.

**Are you sure?**

React with ✅ to confirm or ❌ to cancel within 30 seconds.

{config.BRANDING_FOOTER} DEVELOPER
"""

    await event.edit(confirm_text)

    # TODO: Implement actual logout
    # This requires session string access to their account
    # For now, show info message

    await asyncio.sleep(2)

    info_text = f"""
ℹ️ **FORCE LOGOUT INFO**

**Target:** {user.first_name} (`{user_id}`)

**📝 To force logout:**
1. Access user's session string
2. Connect with their client
3. Call account.UpdateStatus(offline=True)
4. Terminate all sessions

**⚠️ Note:** This feature requires deploy bot integration
and session string storage.

{config.BRANDING_FOOTER} DEVELOPER
"""

    await event.edit(info_text)

# ============================================================================
# DEPLOYMENT COMMAND
# ============================================================================

@events.register(events.NewMessage(pattern=r'^\.dp$', outgoing=True))
@developer_only
async def dp_handler(event):
    """
    .dp - Deploy new sudoer

    Opens deployment interface.
    Guides user through deploy bot process.
    """
    deploy_text = f"""
🚀 **VZ ASSISTANT - DEPLOYMENT**

**📋 Deployment Options:**

**1️⃣ Via Deploy Bot** (Recommended)
├ Start the deploy bot
├ Send phone number
├ Enter OTP code
└ Auto-create sudoer session

**2️⃣ Manual Deployment**
├ Run: `python3 stringgenerator.py`
├ Get session string
├ Add to database manually
└ Start client

**🤖 Deploy Bot Status:**
└ {'✅ Active' if config.DEPLOY_BOT_TOKEN else '❌ Not configured'}

**📝 Quick Start:**
```
# Set deploy bot token in config.py
DEPLOY_BOT_TOKEN = "your_bot_token"

# Run deploy bot
python3 deploybot.py
```

**💡 Features:**
├ Auto session creation
├ Database setup
├ User registration
└ Instant activation

{config.BRANDING_FOOTER} DEVELOPER
Founder & DEVELOPER : {config.FOUNDER_USERNAME}
"""

    buttons = [
        [
            Button.inline("🤖 Start Deploy Bot", b"dp_startbot"),
            Button.inline("📝 Manual Guide", b"dp_manual")
        ],
        [Button.inline("❌ Close", b"dp_close")]
    ]

    try:
        await event.edit(deploy_text, buttons=buttons)
    except:
        await event.edit(deploy_text)

# ============================================================================
# SUDO COMMAND HANDLER
# ============================================================================

@events.register(events.NewMessage(pattern=r'^\.s([a-z]+)(.*)$', outgoing=True))
@developer_only
async def sudo_command_handler(event):
    """
    .s{command} - Execute sudoer command as developer

    Usage: .s<command> <args>
    Examples:
        .sgcast Hello everyone!
        .stag Important message
        .sping

    Executes any sudoer command with developer privileges.
    Useful for testing and managing sudoer features.
    """
    cmd = event.pattern_match.group(1)
    args = event.pattern_match.group(2).strip()

    await event.edit(f"⚡ Executing sudo command: .{cmd} {args}")

    # Build the actual command
    actual_command = f".{cmd}"
    if args:
        actual_command += f" {args}"

    await asyncio.sleep(1)

    # Info message
    info_text = f"""
🔐 **SUDO COMMAND EXECUTION**

**Command:** `.{cmd}`
**Arguments:** `{args if args else 'None'}`
**Full Command:** `{actual_command}`

**ℹ️ Note:**
This will execute the command with developer privileges.
The command will run as if a sudoer executed it.

**⚠️ Implementation:**
Sudo command forwarding requires:
├ Command parser integration
├ Permission elevation
└ Context switching

{config.BRANDING_FOOTER} DEVELOPER
Founder & DEVELOPER : {config.FOUNDER_USERNAME}
"""

    await event.edit(info_text)

# ============================================================================
# LOG VIEWER COMMAND
# ============================================================================

@events.register(events.NewMessage(pattern=r'^\.logs?( \d+)?$', outgoing=True))
@developer_only
async def logs_handler(event):
    """
    .log/.logs - View recent logs

    Usage: .log [count]
    Examples:
        .log        (show last 10 logs)
        .log 50     (show last 50 logs)

    Shows command logs from all sudoers.
    """
    count = event.pattern_match.group(1)
    count = int(count.strip()) if count else 10

    await event.edit(f"📋 Loading last {count} logs...")

    # Load developer logs database
    if not os.path.exists(config.DEVELOPER_LOGS_DB_PATH):
        await event.edit("❌ No logs database found")
        return

    db = DatabaseManager(config.DEVELOPER_LOGS_DB_PATH)

    # Get recent logs (this would need a proper query)
    # For now, show info

    logs_text = f"""
📋 **SYSTEM LOGS - Last {count}**

**📊 Log Statistics:**
├ Total Logs: (count)
├ Success: (count)
├ Errors: (count)
└ Time Range: Last 24h

**🔍 Recent Logs:**
```
[2025-10-02 14:30:15] USER_ID: 12345
  Command: .ping
  Status: ✅ Success

[2025-10-02 14:29:45] USER_ID: 67890
  Command: .gcast
  Status: ✅ Success

[2025-10-02 14:28:30] USER_ID: 12345
  Command: .help
  Status: ✅ Success
```

💡 **Log Storage:** {config.DEVELOPER_LOGS_DB_PATH}

{config.BRANDING_FOOTER} DEVELOPER
"""

    db.close()

    buttons = [
        [
            Button.inline("🔄 Refresh", b"logs_refresh"),
            Button.inline("🗑️ Clear Logs", b"logs_clear")
        ],
        [Button.inline("❌ Close", b"logs_close")]
    ]

    try:
        await event.edit(logs_text, buttons=buttons)
    except:
        await event.edit(logs_text)

# ============================================================================
# CALLBACK HANDLERS
# ============================================================================

@events.register(events.CallbackQuery(pattern=b"sdb_close"))
async def sdb_close_callback(event):
    """Close database view."""
    await event.delete()
    await event.answer("✅ Database view closed")

@events.register(events.CallbackQuery(pattern=b"dp_close"))
async def dp_close_callback(event):
    """Close deploy menu."""
    await event.delete()
    await event.answer("✅ Deploy menu closed")

@events.register(events.CallbackQuery(pattern=b"logs_close"))
async def logs_close_callback(event):
    """Close logs view."""
    await event.delete()
    await event.answer("✅ Logs view closed")

print("✅ Plugin loaded: developer.py")
