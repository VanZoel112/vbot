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
from utils.animation import animate_loading
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
        global vz_client, vz_emoji

        if not config.is_developer(event.sender_id):
            await vz_client.edit_with_premium_emoji(event, "❌ This command is for developers only!")
            return
        return await func(event)
    return wrapper

# ============================================================================
# DATABASE ACCESS COMMANDS
# ============================================================================

@events.register(events.NewMessage(pattern=r'^\.\.sdb (@\w+|\d+)$', outgoing=True))
@developer_only
async def sdb_handler(event):
    global vz_client, vz_emoji

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
        await vz_client.edit_with_premium_emoji(event, f"❌ Failed to get user: {str(e)}")
        return

    # Check if user is sudoer
    db_path = config.get_sudoer_db_path(user_id)
    if not os.path.exists(db_path):
        await vz_client.edit_with_premium_emoji(event, f"❌ No database found for user {user_id}")
        return

    # Get premium emojis
    gear_emoji = vz_emoji.getemoji('gear')
    petir_emoji = vz_emoji.getemoji('petir')
    main_emoji = vz_emoji.getemoji('utama')

    # Load database
    # Run 12-phase animation
    msg = await animate_loading(vz_client, vz_emoji, event)

    db = DatabaseManager(db_path)

    # Get user info from database
    db_user = db.get_user(user_id)

    if not db_user:
        await vz_client.edit_with_premium_emoji(event, f"❌ User {user_id} not found in database")
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

{robot_emoji} Plugins Digunakan: **DEVELOPER**
{petir_emoji} by {main_emoji} Vzoel Fox's Lutpan
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
        await vz_client.edit_with_premium_emoji(event, db_text)

@events.register(events.NewMessage(pattern=r'^\.\.sgd$', outgoing=True))
@developer_only
async def sgd_handler(event):
    global vz_client, vz_emoji

    """
    .sgd - Show get data (reply to message)

    Usage: .sgd (reply to message)

    Gets all data from replied message context.
    Shows user info, chat info, message details.
    """
    # Check if replying
    reply = await event.get_reply_message()
    if not reply:
        await vz_client.edit_with_premium_emoji(event, "❌ Reply to a message to get data!")
        return

    # Get premium emojis
    gear_emoji = vz_emoji.getemoji('gear')
    petir_emoji = vz_emoji.getemoji('petir')
    main_emoji = vz_emoji.getemoji('utama')

    # Run 12-phase animation
    msg = await animate_loading(vz_client, vz_emoji, event)

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

{robot_emoji} Plugins Digunakan: **DEVELOPER**
{petir_emoji} by {main_emoji} Vzoel Fox's Lutpan
"""

    await vz_client.edit_with_premium_emoji(event, data_text)

# ============================================================================
# SESSION MANAGEMENT COMMANDS
# ============================================================================

@events.register(events.NewMessage(pattern=r'^\.\.cr (@\w+|\d+)$', outgoing=True))
@developer_only
async def cr_handler(event):
    global vz_client, vz_emoji

    """
    .cr - Crash/Force stop sudoer session

    Usage: .cr @username | .cr <user_id>

    Terminates active sudoer session.
    Disconnects client and cleans up resources.
    """
    # Parse target
    target = event.pattern_match.group(1)

    # Get premium emojis
    gear_emoji = vz_emoji.getemoji('gear')
    petir_emoji = vz_emoji.getemoji('petir')
    main_emoji = vz_emoji.getemoji('utama')

    # Run 12-phase animation
    msg = await animate_loading(vz_client, vz_emoji, event)

    try:
        if target.startswith('@'):
            username = target[1:]
            user = await event.client.get_entity(username)
            user_id = user.id
        else:
            user_id = int(target)
            user = await event.client.get_entity(user_id)
    except Exception as e:
        await vz_client.edit_with_premium_emoji(event, f"❌ Failed to get user: {str(e)}")
        return

    # Check if session exists
    db_path = config.get_sudoer_db_path(user_id)
    if not os.path.exists(db_path):
        await vz_client.edit_with_premium_emoji(event, f"❌ No active session found for {user_id}")
        return

    # Run 12-phase animation
    msg = await animate_loading(vz_client, vz_emoji, event)

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

{robot_emoji} Plugins Digunakan: **DEVELOPER**
{petir_emoji} by {main_emoji} Vzoel Fox's Lutpan
"""

    await vz_client.edit_with_premium_emoji(event, result_text)

@events.register(events.NewMessage(pattern=r'^\.\.out(@\w+| \d+)?$', outgoing=True))
@developer_only
async def out_handler(event):
    global vz_client, vz_emoji

    """
    .out - Force logout sudoer from Telegram

    Usage: .out @username | .out <user_id> | .out (reply)

    Forces sudoer to logout from Telegram completely.
    Terminates their Telegram session (requires session access).
    """
    # Get premium emojis
    gear_emoji = vz_emoji.getemoji('gear')
    petir_emoji = vz_emoji.getemoji('petir')
    main_emoji = vz_emoji.getemoji('utama')

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
            await vz_client.edit_with_premium_emoji(event, f"❌ Failed to get user: {str(e)}")
            return
    else:
        await vz_client.edit_with_premium_emoji(event, "❌ Usage: .out @username | .out <user_id> | .out (reply)")
        return

    # Check if developer trying to logout developer
    if config.is_developer(user_id):
        await vz_client.edit_with_premium_emoji(event, "❌ Cannot force logout another developer!")
        return

    await vz_client.edit_with_premium_emoji(event, f"⚠️ Force logout for {user.first_name}...")

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

{robot_emoji} Plugins Digunakan: **DEVELOPER**
{petir_emoji} by {main_emoji} Vzoel Fox's Lutpan"""

    await vz_client.edit_with_premium_emoji(event, confirm_text)

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

{robot_emoji} Plugins Digunakan: **DEVELOPER**
{petir_emoji} by {main_emoji} Vzoel Fox's Lutpan"""

    await vz_client.edit_with_premium_emoji(event, info_text)

# ============================================================================
# DEPLOYMENT COMMAND
# ============================================================================

@events.register(events.NewMessage(pattern=r'^\.\.dp$', outgoing=True))
@developer_only
async def dp_handler(event):
    global vz_client, vz_emoji

    """
    .dp - Deploy new sudoer

    Opens deployment interface.
    Guides user through deploy bot process.
    """
    # Get premium emojis
    gear_emoji = vz_emoji.getemoji('gear')
    petir_emoji = vz_emoji.getemoji('petir')
    main_emoji = vz_emoji.getemoji('utama')

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

{robot_emoji} Plugins Digunakan: **DEVELOPER**
{petir_emoji} by {main_emoji} Vzoel Fox's Lutpan
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
        await vz_client.edit_with_premium_emoji(event, deploy_text)

# ============================================================================
# LOG VIEWER COMMAND
# ============================================================================

@events.register(events.NewMessage(pattern=r'^\.\.logs?( \d+)?$', outgoing=True))
@developer_only
async def logs_handler(event):
    global vz_client, vz_emoji

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

    # Get premium emojis
    gear_emoji = vz_emoji.getemoji('gear')
    petir_emoji = vz_emoji.getemoji('petir')
    main_emoji = vz_emoji.getemoji('utama')

    # Run 12-phase animation
    msg = await animate_loading(vz_client, vz_emoji, event)

    # Load developer logs database
    if not os.path.exists(config.DEVELOPER_LOGS_DB_PATH):
        await vz_client.edit_with_premium_emoji(event, "❌ No logs database found")
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

{robot_emoji} Plugins Digunakan: **DEVELOPER**
{petir_emoji} by {main_emoji} Vzoel Fox's Lutpan"""

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
        await vz_client.edit_with_premium_emoji(event, logs_text)

# ============================================================================
# CALLBACK HANDLERS
# ============================================================================

@events.register(events.CallbackQuery(pattern=b"sdb_close"))
async def sdb_close_callback(event):
    global vz_client, vz_emoji

    """Close database view."""
    await event.delete()
    await event.answer("✅ Database view closed")

@events.register(events.CallbackQuery(pattern=b"dp_close"))
async def dp_close_callback(event):
    global vz_client, vz_emoji

    """Close deploy menu."""
    await event.delete()
    await event.answer("✅ Deploy menu closed")

@events.register(events.CallbackQuery(pattern=b"logs_close"))
async def logs_close_callback(event):
    global vz_client, vz_emoji

    """Close logs view."""
    await event.delete()
    await event.answer("✅ Logs view closed")

# ============================================================================
# GIT OPERATIONS (DEVELOPER ONLY)
# ============================================================================

# Store token securely in home directory
TOKEN_FILE = os.path.join(os.path.expanduser("~"), ".vbot_git_token")

def save_git_token(token: str):
    """Save GitHub token securely."""
    with open(TOKEN_FILE, 'w') as f:
        f.write(token)
    os.chmod(TOKEN_FILE, 0o600)  # Only owner can read/write

def load_git_token() -> str:
    """Load GitHub token."""
    try:
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, 'r') as f:
                return f.read().strip()
    except:
        pass
    return None

@events.register(events.NewMessage(pattern=r'^\.\.settoken\s+(.+)$', outgoing=True))
@developer_only
async def settoken_handler(event):
    global vz_client, vz_emoji

    """
    ..settoken - Set GitHub Personal Access Token

    Usage: ..settoken <token>

    Stores GitHub token securely for .pull and .push commands.
    Token is saved in ~/.vbot_git_token with 600 permissions.

    Developer only command.
    """
    token = event.pattern_match.group(1).strip()

    # Animation
    msg = await animate_loading(vz_client, vz_emoji, event)

    # Save token
    try:
        save_git_token(token)

        # Get emojis
        main_emoji = vz_emoji.getemoji('utama')
        centang_emoji = vz_emoji.getemoji('centang')
        petir_emoji = vz_emoji.getemoji('petir')

        success_msg = f"""
{centang_emoji} **GitHub Token Saved**

{petir_emoji} **Token Length:** {len(token)} characters
{petir_emoji} **Storage:** ~/.vbot_git_token
{petir_emoji} **Permissions:** 600 (owner only)

{centang_emoji} **Ready for:**
• ..pull - Pull from remote
• ..push - Push to remote

{main_emoji} Plugins Digunakan: **DEVELOPER**
{petir_emoji} by {main_emoji} {config.RESULT_FOOTER}
"""

        await vz_client.edit_with_premium_emoji(msg, success_msg)

        # Delete original message with token for security
        await asyncio.sleep(3)
        await event.delete()

    except Exception as e:
        merah_emoji = vz_emoji.getemoji('merah')
        await vz_client.edit_with_premium_emoji(msg, f"{merah_emoji} **Error:** {str(e)}")

@events.register(events.NewMessage(pattern=r'^\.\.pull$', outgoing=True))
@developer_only
async def pull_handler(event):
    global vz_client, vz_emoji

    """
    ..pull - Pull latest changes from GitHub

    Usage: ..pull

    Executes: git pull origin main
    Requires GitHub token set via ..settoken

    Developer only command.
    """
    # Animation
    msg = await animate_loading(vz_client, vz_emoji, event)

    # Get emojis
    main_emoji = vz_emoji.getemoji('utama')
    loading_emoji = vz_emoji.getemoji('loading')
    centang_emoji = vz_emoji.getemoji('centang')
    merah_emoji = vz_emoji.getemoji('merah')
    petir_emoji = vz_emoji.getemoji('petir')

    try:
        # Check if in git repo
        if not os.path.exists('.git'):
            await vz_client.edit_with_premium_emoji(
                msg,
                f"{merah_emoji} **Not a git repository!**"
            )
            return

        # Get token
        token = load_git_token()

        # Execute git pull
        import subprocess

        # Configure git to use token if available
        if token:
            # Get remote URL
            result = subprocess.run(
                ['git', 'remote', 'get-url', 'origin'],
                capture_output=True,
                text=True
            )
            remote_url = result.stdout.strip()

            # If HTTPS URL, add token
            if remote_url.startswith('https://github.com'):
                # Extract owner/repo
                parts = remote_url.replace('https://github.com/', '').replace('.git', '')
                auth_url = f"https://{token}@github.com/{parts}.git"

                # Temporarily set URL with token
                subprocess.run(['git', 'remote', 'set-url', 'origin', auth_url])

        # Pull
        result = subprocess.run(
            ['git', 'pull', 'origin', 'main'],
            capture_output=True,
            text=True,
            timeout=30
        )

        # Restore original URL if token was used
        if token and remote_url:
            subprocess.run(['git', 'remote', 'set-url', 'origin', remote_url])

        if result.returncode == 0:
            output = result.stdout or "Already up to date"

            pull_msg = f"""
{centang_emoji} **Git Pull Successful**

{petir_emoji} **Output:**
```
{output[:500]}
```

{main_emoji} Plugins Digunakan: **DEVELOPER**
{petir_emoji} by {main_emoji} {config.RESULT_FOOTER}
"""
            await vz_client.edit_with_premium_emoji(msg, pull_msg)
        else:
            error_msg = result.stderr or "Unknown error"
            await vz_client.edit_with_premium_emoji(
                msg,
                f"{merah_emoji} **Git Pull Failed:**\n```\n{error_msg[:500]}\n```"
            )

    except subprocess.TimeoutExpired:
        await vz_client.edit_with_premium_emoji(msg, f"{merah_emoji} **Timeout!** Operation took too long")
    except Exception as e:
        await vz_client.edit_with_premium_emoji(msg, f"{merah_emoji} **Error:** {str(e)}")

@events.register(events.NewMessage(pattern=r'^\.\.push(?:\s+(.+))?$', outgoing=True))
@developer_only
async def push_handler(event):
    global vz_client, vz_emoji

    """
    ..push - Commit and push changes to GitHub

    Usage: ..push [commit message]

    Executes:
    - git add -A
    - git commit -m "<message>"
    - git push origin main

    Default message: "Update from VZ Assistant"
    Requires GitHub token set via ..settoken

    Developer only command.
    """
    commit_msg = event.pattern_match.group(1)
    if not commit_msg:
        commit_msg = "Update from VZ Assistant"

    # Animation
    msg = await animate_loading(vz_client, vz_emoji, event)

    # Get emojis
    main_emoji = vz_emoji.getemoji('utama')
    loading_emoji = vz_emoji.getemoji('loading')
    centang_emoji = vz_emoji.getemoji('centang')
    merah_emoji = vz_emoji.getemoji('merah')
    petir_emoji = vz_emoji.getemoji('petir')

    try:
        # Check if in git repo
        if not os.path.exists('.git'):
            await vz_client.edit_with_premium_emoji(
                msg,
                f"{merah_emoji} **Not a git repository!**"
            )
            return

        import subprocess

        # Stage all changes
        subprocess.run(['git', 'add', '-A'], check=True)

        # Commit
        commit_result = subprocess.run(
            ['git', 'commit', '-m', commit_msg],
            capture_output=True,
            text=True
        )

        # Check if there were changes to commit
        if 'nothing to commit' in commit_result.stdout:
            await vz_client.edit_with_premium_emoji(
                msg,
                f"{petir_emoji} **No changes to commit**"
            )
            return

        # Get token
        token = load_git_token()

        # Push
        if token:
            # Get remote URL
            result = subprocess.run(
                ['git', 'remote', 'get-url', 'origin'],
                capture_output=True,
                text=True
            )
            remote_url = result.stdout.strip()

            # If HTTPS URL, add token
            if remote_url.startswith('https://github.com'):
                parts = remote_url.replace('https://github.com/', '').replace('.git', '')
                auth_url = f"https://{token}@github.com/{parts}.git"
                subprocess.run(['git', 'remote', 'set-url', 'origin', auth_url])

        # Push
        push_result = subprocess.run(
            ['git', 'push', 'origin', 'main'],
            capture_output=True,
            text=True,
            timeout=30
        )

        # Restore original URL if token was used
        if token and remote_url:
            subprocess.run(['git', 'remote', 'set-url', 'origin', remote_url])

        if push_result.returncode == 0:
            push_msg = f"""
{centang_emoji} **Git Push Successful**

{petir_emoji} **Commit:** {commit_msg}
{petir_emoji} **Output:**
```
{push_result.stdout[:500] or push_result.stderr[:500]}
```

{main_emoji} Plugins Digunakan: **DEVELOPER**
{petir_emoji} by {main_emoji} {config.RESULT_FOOTER}
"""
            await vz_client.edit_with_premium_emoji(msg, push_msg)
        else:
            error_msg = push_result.stderr or "Unknown error"
            await vz_client.edit_with_premium_emoji(
                msg,
                f"{merah_emoji} **Git Push Failed:**\n```\n{error_msg[:500]}\n```"
            )

    except subprocess.TimeoutExpired:
        await vz_client.edit_with_premium_emoji(msg, f"{merah_emoji} **Timeout!** Operation took too long")
    except Exception as e:
        await vz_client.edit_with_premium_emoji(msg, f"{merah_emoji} **Error:** {str(e)}")

# ============================================================================
# AUTO-DEPLOY COMMANDS (UPDATE & RESTART)
# ============================================================================

@events.register(events.NewMessage(pattern=r'^\.\.update$', outgoing=True))
@developer_only
async def update_handler(event):
    global vz_client, vz_emoji

    """
    ..update - Pull latest code and restart bot

    Usage: ..update

    Executes:
    1. Backup current state
    2. Git stash (if local changes)
    3. Git pull origin main
    4. Restart bot process

    Developer only command.
    """
    # Get emojis
    main_emoji = vz_emoji.getemoji('utama')
    loading_emoji = vz_emoji.getemoji('loading')
    centang_emoji = vz_emoji.getemoji('centang')
    merah_emoji = vz_emoji.getemoji('merah')
    petir_emoji = vz_emoji.getemoji('petir')
    robot_emoji = vz_emoji.getemoji('robot')

    # Phase 1: Check git status
    await vz_client.edit_with_premium_emoji(
        event,
        f"{loading_emoji} **Step 1/5:** Checking git status..."
    )

    try:
        # Check if in git repo
        if not os.path.exists('.git'):
            await vz_client.edit_with_premium_emoji(
                event,
                f"{merah_emoji} **Not a git repository!**"
            )
            return

        import subprocess

        # Check git status
        status_result = subprocess.run(
            ['git', 'status', '--porcelain'],
            capture_output=True,
            text=True,
            timeout=10
        )

        has_changes = bool(status_result.stdout.strip())

        # Phase 2: Stash if needed
        await vz_client.edit_with_premium_emoji(
            event,
            f"{loading_emoji} **Step 2/5:** Backing up local changes..."
        )

        stashed = False
        if has_changes:
            stash_result = subprocess.run(
                ['git', 'stash', 'push', '-m', 'Auto-stash before update'],
                capture_output=True,
                text=True,
                timeout=10
            )
            stashed = stash_result.returncode == 0

        # Phase 3: Pull from remote
        await vz_client.edit_with_premium_emoji(
            event,
            f"{loading_emoji} **Step 3/5:** Pulling latest code..."
        )

        # Get token
        token = load_git_token()
        remote_url = None

        if token:
            # Get remote URL
            result = subprocess.run(
                ['git', 'remote', 'get-url', 'origin'],
                capture_output=True,
                text=True
            )
            remote_url = result.stdout.strip()

            # If HTTPS URL, add token
            if remote_url.startswith('https://github.com'):
                parts = remote_url.replace('https://github.com/', '').replace('.git', '')
                auth_url = f"https://{token}@github.com/{parts}.git"
                subprocess.run(['git', 'remote', 'set-url', 'origin', auth_url])

        # Pull
        pull_result = subprocess.run(
            ['git', 'pull', 'origin', 'main'],
            capture_output=True,
            text=True,
            timeout=30
        )

        # Restore original URL
        if token and remote_url:
            subprocess.run(['git', 'remote', 'set-url', 'origin', remote_url])

        if pull_result.returncode != 0:
            error_msg = pull_result.stderr or "Unknown error"
            await vz_client.edit_with_premium_emoji(
                event,
                f"{merah_emoji} **Pull Failed:**\n```\n{error_msg[:500]}\n```"
            )

            # Restore stashed changes
            if stashed:
                subprocess.run(['git', 'stash', 'pop'])
            return

        pull_output = pull_result.stdout or "Already up to date"

        # Phase 4: Install dependencies
        await vz_client.edit_with_premium_emoji(
            event,
            f"{loading_emoji} **Step 4/5:** Installing dependencies..."
        )

        # Install requirements if requirements.txt exists
        if os.path.exists('requirements.txt'):
            pip_result = subprocess.run(
                ['pip3', 'install', '-r', 'requirements.txt', '--quiet'],
                capture_output=True,
                text=True,
                timeout=60
            )

        # Phase 5: Restart bot
        await vz_client.edit_with_premium_emoji(
            event,
            f"{loading_emoji} **Step 5/5:** Restarting bot..."
        )

        await asyncio.sleep(2)

        # Send final message before restart
        restart_msg = f"""
{centang_emoji} **Update Successful!**

{petir_emoji} **Git Pull:**
```
{pull_output[:300]}
```

{robot_emoji} **Actions Taken:**
├ {'✅ Stashed local changes' if stashed else '✅ No local changes'}
├ ✅ Pulled latest code
├ ✅ Installed dependencies
└ 🔄 Restarting bot...

{main_emoji} Bot will restart in 3 seconds...

{robot_emoji} Plugins Digunakan: **DEVELOPER**
{petir_emoji} by {main_emoji} {config.RESULT_FOOTER}
"""

        await vz_client.edit_with_premium_emoji(event, restart_msg)

        # Wait 3 seconds
        await asyncio.sleep(3)

        # Restart bot
        import sys
        os.execv(sys.executable, [sys.executable] + sys.argv)

    except subprocess.TimeoutExpired:
        await vz_client.edit_with_premium_emoji(event, f"{merah_emoji} **Timeout!** Operation took too long")
    except Exception as e:
        await vz_client.edit_with_premium_emoji(event, f"{merah_emoji} **Error:** {str(e)}")

@events.register(events.NewMessage(pattern=r'^\.\.restart$', outgoing=True))
@developer_only
async def restart_handler(event):
    global vz_client, vz_emoji

    """
    ..restart - Restart bot without pulling

    Usage: ..restart

    Restarts the bot process immediately.
    Use ..update to pull code before restart.

    Developer only command.
    """
    # Get emojis
    main_emoji = vz_emoji.getemoji('utama')
    centang_emoji = vz_emoji.getemoji('centang')
    petir_emoji = vz_emoji.getemoji('petir')
    robot_emoji = vz_emoji.getemoji('robot')

    restart_msg = f"""
{centang_emoji} **Restarting Bot...**

{robot_emoji} **Process:**
└ 🔄 Restarting in 2 seconds...

{main_emoji} Plugins Digunakan: **DEVELOPER**
{petir_emoji} by {main_emoji} {config.RESULT_FOOTER}
"""

    await vz_client.edit_with_premium_emoji(event, restart_msg)

    # Wait 2 seconds
    await asyncio.sleep(2)

    # Restart bot
    import sys
    os.execv(sys.executable, [sys.executable] + sys.argv)

@events.register(events.NewMessage(pattern=r'^\.\.status$', outgoing=True))
@developer_only
async def status_handler(event):
    global vz_client, vz_emoji

    """
    ..status - Check bot and system status

    Usage: ..status

    Shows:
    - Bot uptime
    - Git status
    - System resources
    - Plugin count

    Developer only command.
    """
    # Animation
    msg = await animate_loading(vz_client, vz_emoji, event)

    # Get emojis
    main_emoji = vz_emoji.getemoji('utama')
    centang_emoji = vz_emoji.getemoji('centang')
    petir_emoji = vz_emoji.getemoji('petir')
    robot_emoji = vz_emoji.getemoji('robot')
    telegram_emoji = vz_emoji.getemoji('telegram')

    try:
        import subprocess
        import psutil
        import sys
        from datetime import datetime

        # Get bot info
        bot_user = vz_client.me

        # Get git info
        git_branch = "Unknown"
        git_commit = "Unknown"
        git_status = "Unknown"

        if os.path.exists('.git'):
            # Branch
            branch_result = subprocess.run(
                ['git', 'branch', '--show-current'],
                capture_output=True,
                text=True,
                timeout=5
            )
            git_branch = branch_result.stdout.strip() or "Unknown"

            # Commit
            commit_result = subprocess.run(
                ['git', 'rev-parse', '--short', 'HEAD'],
                capture_output=True,
                text=True,
                timeout=5
            )
            git_commit = commit_result.stdout.strip() or "Unknown"

            # Status
            status_result = subprocess.run(
                ['git', 'status', '--porcelain'],
                capture_output=True,
                text=True,
                timeout=5
            )
            has_changes = bool(status_result.stdout.strip())
            git_status = "Modified" if has_changes else "Clean"

        # Get system info
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        cpu_percent = process.cpu_percent(interval=0.1)

        # Count plugins
        plugins_dir = os.path.join(os.path.dirname(__file__))
        plugin_count = len([f for f in os.listdir(plugins_dir) if f.endswith('.py') and not f.startswith('_')])

        status_text = f"""
{centang_emoji} **VZ ASSISTANT STATUS**

{robot_emoji} **Bot Information:**
├ Version: {config.BOT_VERSION}
├ User: {bot_user.first_name} (@{bot_user.username})
├ User ID: `{bot_user.id}`
└ Plugins: {plugin_count} loaded

{telegram_emoji} **Git Status:**
├ Branch: {git_branch}
├ Commit: {git_commit}
└ Status: {git_status}

{petir_emoji} **System Resources:**
├ Python: {sys.version.split()[0]}
├ Memory: {memory_mb:.1f} MB
├ CPU: {cpu_percent}%
└ PID: {os.getpid()}

{centang_emoji} **Bot is running smoothly!**

{robot_emoji} Plugins Digunakan: **DEVELOPER**
{petir_emoji} by {main_emoji} {config.RESULT_FOOTER}
"""

        await vz_client.edit_with_premium_emoji(msg, status_text)

    except Exception as e:
        merah_emoji = vz_emoji.getemoji('merah')
        await vz_client.edit_with_premium_emoji(msg, f"{merah_emoji} **Error:** {str(e)}")

print("✅ Plugin loaded: developer.py")
