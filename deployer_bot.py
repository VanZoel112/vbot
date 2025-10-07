#!/usr/bin/env python3
"""
VZ DEPLOYER BOT v0.0.0.69
Multi-user deployment manager with approval system

Features:
- User request deployment via /deploy
- Developer approve/reject with inline buttons
- Auto-generate .env for each user
- PM2 management for each deployment

2025© Vzoel Fox's Lutpan
Founder & DEVELOPER : @VZLfxs
"""

import os
import sys
import json
import logging
import asyncio
import subprocess
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
    Message
)

# ============================================================================
# LOGGING SETUP
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger('VZDeployerBot')

# ============================================================================
# CONFIGURATION
# ============================================================================

BOT_TOKEN = "7257252641:AAGKRXlf-GCJxsaqFUT1BgH8gRxUptIvQLQ"

# API credentials for deployed bots
API_ID = 29919905
API_HASH = "717957f0e3ae20a7db004d08b66bfd30"

# Authorization
DEVELOPER_IDS = [8024282347, 7553981355]  # From config.py
SUDOER_IDS = [7553981355]  # Can request deployment

# Data files
DEPLOY_DATA_FILE = "data/deployments.json"
SESSION_DATA_FILE = "data/deploy_sessions.json"
DEPLOY_BASE_DIR = "deployments"

# ============================================================================
# DATA MANAGEMENT
# ============================================================================

def load_json(filepath, default=None):
    """Load JSON file"""
    if default is None:
        default = {}

    if not os.path.exists(filepath):
        return default

    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except:
        return default


def save_json(filepath, data):
    """Save JSON file"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)


def load_deployments():
    """Load deployment data"""
    return load_json(DEPLOY_DATA_FILE, {
        "active": {},
        "pending": {},
        "history": []
    })


def save_deployments(data):
    """Save deployment data"""
    save_json(DEPLOY_DATA_FILE, data)


def load_sessions():
    """Load session strings"""
    return load_json(SESSION_DATA_FILE, {})


def save_sessions(data):
    """Save session strings"""
    save_json(SESSION_DATA_FILE, data)


def get_next_port():
    """Get next available port"""
    deployments = load_deployments()
    used_ports = [d.get('port', 0) for d in deployments['active'].values()]

    port = 8000
    while port in used_ports:
        port += 1

    return port


# ============================================================================
# PYROGRAM CLIENT
# ============================================================================

app = Client(
    "vz_deployer_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    workdir="sessions"
)

# ============================================================================
# AUTHORIZATION
# ============================================================================

def is_authorized(user_id: int) -> bool:
    """Check if user is authorized"""
    return user_id in DEVELOPER_IDS or user_id in SUDOER_IDS


def is_developer(user_id: int) -> bool:
    """Check if user is developer"""
    return user_id in DEVELOPER_IDS


def is_sudoer(user_id: int) -> bool:
    """Check if user is sudoer"""
    return user_id in SUDOER_IDS


# ============================================================================
# DEPLOYMENT FUNCTIONS
# ============================================================================

def create_user_env(user_id, session_string, port, log_group_id=None):
    """Create deployment environment for user"""
    user_dir = os.path.join(DEPLOY_BASE_DIR, str(user_id))
    os.makedirs(user_dir, exist_ok=True)

    # Create .env file
    env_content = f"""# VZ ASSISTANT Deployment - User {user_id}
API_ID={API_ID}
API_HASH={API_HASH}
SESSION_STRING={session_string}
LOG_GROUP_ID={log_group_id or ''}
DEVELOPER_IDS={','.join(map(str, DEVELOPER_IDS))}
OWNER_ID={user_id}
"""

    env_file = os.path.join(user_dir, '.env')
    with open(env_file, 'w') as f:
        f.write(env_content)

    logger.info(f"Created env for user {user_id} in {user_dir}")
    return user_dir


async def start_deployment(user_id, user_dir):
    """Start PM2 deployment for user"""
    try:
        pm2_name = f"vbot_{user_id}"

        # Check if already running
        check = subprocess.run(
            ["pm2", "id", pm2_name],
            capture_output=True,
            text=True
        )

        if check.returncode == 0:
            # Already running, restart
            subprocess.run(["pm2", "restart", pm2_name])
            logger.info(f"Restarted existing deployment for {user_id}")
        else:
            # Start new
            cmd = [
                "pm2", "start", "main.py",
                "--name", pm2_name,
                "--interpreter", "python3",
                "--", f"--env-file={os.path.join(user_dir, '.env')}"
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                logger.error(f"Failed to start PM2 for {user_id}: {result.stderr}")
                return False, result.stderr

            logger.info(f"Started new deployment for {user_id}")

        # Get PID
        pm2_list = subprocess.run(
            ["pm2", "jlist"],
            capture_output=True,
            text=True
        )

        if pm2_list.returncode == 0:
            processes = json.loads(pm2_list.stdout)
            for proc in processes:
                if proc.get('name') == pm2_name:
                    return True, proc.get('pid')

        return True, None

    except Exception as e:
        logger.error(f"Deployment error for {user_id}: {e}", exc_info=True)
        return False, str(e)


async def stop_deployment(user_id):
    """Stop PM2 deployment for user"""
    try:
        pm2_name = f"vbot_{user_id}"

        # Stop and delete
        subprocess.run(["pm2", "stop", pm2_name], capture_output=True)
        subprocess.run(["pm2", "delete", pm2_name], capture_output=True)

        logger.info(f"Stopped deployment for {user_id}")
        return True, None

    except Exception as e:
        logger.error(f"Stop error for {user_id}: {e}")
        return False, str(e)


# ============================================================================
# START COMMAND
# ============================================================================

@app.on_message(filters.command("start") & filters.private)
async def start_handler(client: Client, message: Message):
    """Handle /start command"""
    user_id = message.from_user.id

    if not is_authorized(user_id):
        await message.reply(
            "❌ **Access Denied**\n\n"
            "This bot is for authorized users only.\n\n"
            "🤖 VZ Deployer Bot"
        )
        return

    role = "DEVELOPER" if is_developer(user_id) else "SUDOER"

    welcome_text = f"""
🤖 **VZ DEPLOYER BOT**

Hello {message.from_user.first_name}!

**Your Role:** {role}

**Available Commands:**
"""

    if is_sudoer(user_id):
        welcome_text += """
• `/deploy` - Request deployment
• `/mystatus` - Check deployment status
• `/setsession` - Set your session string
"""

    if is_developer(user_id):
        welcome_text += """
• `/deploylist` - List all deployments
• `/deploystop <user_id>` - Stop deployment
• `/pending` - View pending requests
"""

    welcome_text += "\n🔐 Powered by VZ Assistant"

    await message.reply(welcome_text)


# ============================================================================
# SET SESSION COMMAND
# ============================================================================

@app.on_message(filters.command("setsession") & filters.private)
async def setsession_handler(client: Client, message: Message):
    """Set user session string"""
    user_id = message.from_user.id

    if not is_sudoer(user_id):
        await message.reply("❌ **Access Denied**\n\nSudoers only.")
        return

    # Get session from command
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply(
            "**Set Session String**\n\n"
            "**Usage:** `/setsession <your_session_string>`\n\n"
            "⚠️ **IMPORTANT:**\n"
            "• Session string = full access\n"
            "• Use DIFFERENT account from owner\n"
            "• Get session from string generator\n\n"
            "This message will auto-delete in 10 seconds."
        )
        return

    session_string = args[1].strip()

    # Validate session (basic check)
    if len(session_string) < 100:
        await message.reply(
            "❌ **Invalid session string**\n\n"
            "Session string too short. Please check again."
        )
        return

    # Save session
    sessions = load_sessions()
    sessions[str(user_id)] = {
        'session': session_string,
        'updated_at': datetime.now().isoformat()
    }
    save_sessions(sessions)

    await message.reply(
        "✅ **Session Saved**\n\n"
        "Your session string has been saved securely.\n"
        "You can now request deployment with `/deploy`\n\n"
        "⚠️ Delete your message containing session!"
    )

    # Delete user message for security
    try:
        await message.delete()
    except:
        pass

    logger.info(f"Session saved for user {user_id}")


# ============================================================================
# DEPLOY REQUEST COMMAND
# ============================================================================

@app.on_message(filters.command("deploy") & filters.private)
async def deploy_handler(client: Client, message: Message):
    """Request deployment"""
    user_id = message.from_user.id

    if not is_sudoer(user_id):
        await message.reply("❌ **Access Denied**\n\nSudoers only.")
        return

    # Check if session exists
    sessions = load_sessions()
    if str(user_id) not in sessions:
        await message.reply(
            "❌ **Session Not Found**\n\n"
            "Please set your session string first:\n"
            "`/setsession <your_session_string>`"
        )
        return

    # Check if already deployed
    deployments = load_deployments()
    if str(user_id) in deployments['active']:
        info = deployments['active'][str(user_id)]
        await message.reply(
            f"⚠️ **Already Deployed**\n\n"
            f"**Port:** {info.get('port', 'N/A')}\n"
            f"**Status:** Running\n"
            f"**Started:** {info.get('started_at', 'N/A')}\n\n"
            f"Use `/mystatus` for details."
        )
        return

    # Check if pending request
    if str(user_id) in deployments['pending']:
        await message.reply(
            "⚠️ **Pending Request**\n\n"
            "Your deployment request is waiting for approval.\n"
            "Please wait for developer response."
        )
        return

    # Create pending request
    user_name = message.from_user.first_name
    username = f"@{message.from_user.username}" if message.from_user.username else "No username"

    deployments['pending'][str(user_id)] = {
        'user_name': user_name,
        'username': username,
        'requested_at': datetime.now().isoformat()
    }
    save_deployments(deployments)

    await message.reply(
        "✅ **Request Sent**\n\n"
        "Your deployment request has been sent to developers.\n"
        "You will be notified when approved.\n\n"
        "⏳ Please wait..."
    )

    # Notify developers
    for dev_id in DEVELOPER_IDS:
        try:
            request_msg = f"""
🔔 **NEW DEPLOYMENT REQUEST**

**User:** {user_name}
**Username:** {username}
**User ID:** `{user_id}`
**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Approve deployment?
"""

            buttons = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("✅ Approve", callback_data=f"approve_{user_id}"),
                    InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user_id}")
                ]
            ])

            await client.send_message(dev_id, request_msg, reply_markup=buttons)
        except Exception as e:
            logger.error(f"Failed to notify developer {dev_id}: {e}")

    logger.info(f"Deployment request from {user_id} ({user_name})")


# ============================================================================
# APPROVAL CALLBACK
# ============================================================================

@app.on_callback_query(filters.regex(r"^approve_(\d+)$"))
async def approve_callback(client: Client, callback: CallbackQuery):
    """Handle deployment approval"""
    if not is_developer(callback.from_user.id):
        await callback.answer("❌ Developers only", show_alert=True)
        return

    user_id = callback.matches[0].group(1).decode()

    deployments = load_deployments()

    if str(user_id) not in deployments['pending']:
        await callback.answer("❌ Request not found or already processed", show_alert=True)
        return

    await callback.answer("⏳ Processing approval...", show_alert=False)

    request_info = deployments['pending'][str(user_id)]

    try:
        # Get session
        sessions = load_sessions()
        if str(user_id) not in sessions:
            await callback.edit_message_text(
                "❌ **Approval Failed**\n\n"
                "User session not found.\n"
                "User needs to set session with `/setsession`"
            )
            return

        session_string = sessions[str(user_id)]['session']

        # Get port
        port = get_next_port()

        # Create env
        user_dir = create_user_env(user_id, session_string, port)

        # Start deployment
        success, result = await start_deployment(user_id, user_dir)

        if success:
            # Move to active
            deployments['active'][str(user_id)] = {
                'user_name': request_info['user_name'],
                'username': request_info['username'],
                'port': port,
                'pid': result,
                'started_at': datetime.now().isoformat(),
                'approved_by': callback.from_user.id
            }

            del deployments['pending'][str(user_id)]
            save_deployments(deployments)

            await callback.edit_message_text(
                f"✅ **DEPLOYMENT APPROVED**\n\n"
                f"**User:** {request_info['user_name']}\n"
                f"**User ID:** `{user_id}`\n"
                f"**Port:** {port}\n"
                f"**PID:** {result}\n"
                f"**Status:** Running\n\n"
                f"🤖 VZ Deployer Bot"
            )

            # Notify user
            try:
                await client.send_message(
                    int(user_id),
                    f"✅ **DEPLOYMENT APPROVED**\n\n"
                    f"Your bot is now running!\n\n"
                    f"**Port:** {port}\n"
                    f"**Status:** Active\n\n"
                    f"Check status with `/mystatus`"
                )
            except:
                pass

            logger.info(f"Deployment approved for {user_id} by {callback.from_user.id}")

        else:
            await callback.edit_message_text(
                f"❌ **DEPLOYMENT FAILED**\n\n"
                f"Error: {str(result)[:200]}\n\n"
                f"Contact developer."
            )

            # Remove from pending
            del deployments['pending'][str(user_id)]
            save_deployments(deployments)

    except Exception as e:
        logger.error(f"Approval error: {e}", exc_info=True)
        await callback.edit_message_text(
            f"❌ **APPROVAL FAILED**\n\n"
            f"Error: {str(e)[:200]}"
        )


# ============================================================================
# REJECTION CALLBACK
# ============================================================================

@app.on_callback_query(filters.regex(r"^reject_(\d+)$"))
async def reject_callback(client: Client, callback: CallbackQuery):
    """Handle deployment rejection"""
    if not is_developer(callback.from_user.id):
        await callback.answer("❌ Developers only", show_alert=True)
        return

    user_id = callback.matches[0].group(1).decode()

    deployments = load_deployments()

    if str(user_id) not in deployments['pending']:
        await callback.answer("❌ Request not found", show_alert=True)
        return

    request_info = deployments['pending'][str(user_id)]
    del deployments['pending'][str(user_id)]
    save_deployments(deployments)

    await callback.edit_message_text(
        f"❌ **DEPLOYMENT REJECTED**\n\n"
        f"**User:** {request_info['user_name']}\n"
        f"**User ID:** `{user_id}`\n"
        f"**Rejected by:** Developer\n\n"
        f"🤖 VZ Deployer Bot"
    )

    # Notify user
    try:
        await client.send_message(
            int(user_id),
            "❌ **DEPLOYMENT REJECTED**\n\n"
            "Your deployment request was rejected.\n"
            "Contact developer for more info."
        )
    except:
        pass

    await callback.answer("✅ Request rejected", show_alert=False)
    logger.info(f"Deployment rejected for {user_id} by {callback.from_user.id}")


# ============================================================================
# MY STATUS COMMAND
# ============================================================================

@app.on_message(filters.command("mystatus") & filters.private)
async def mystatus_handler(client: Client, message: Message):
    """Check own deployment status"""
    user_id = message.from_user.id

    if not is_sudoer(user_id):
        await message.reply("❌ Access Denied")
        return

    deployments = load_deployments()

    # Check pending
    if str(user_id) in deployments['pending']:
        info = deployments['pending'][str(user_id)]
        await message.reply(
            f"⏳ **PENDING REQUEST**\n\n"
            f"**Status:** Waiting for approval\n"
            f"**Requested:** {info['requested_at']}\n\n"
            f"Please wait for developer response."
        )
        return

    # Check active
    if str(user_id) in deployments['active']:
        info = deployments['active'][str(user_id)]
        await message.reply(
            f"✅ **DEPLOYMENT ACTIVE**\n\n"
            f"**Port:** {info.get('port', 'N/A')}\n"
            f"**PID:** {info.get('pid', 'N/A')}\n"
            f"**Started:** {info.get('started_at', 'N/A')}\n"
            f"**Status:** Running\n\n"
            f"🤖 Your bot is online!"
        )
        return

    # No deployment
    await message.reply(
        "ℹ️ **NO DEPLOYMENT**\n\n"
        "You don't have an active deployment.\n\n"
        "**Steps to deploy:**\n"
        "1. `/setsession <session_string>`\n"
        "2. `/deploy`\n"
        "3. Wait for approval"
    )


# ============================================================================
# DEPLOY LIST COMMAND (Developer)
# ============================================================================

@app.on_message(filters.command("deploylist") & filters.private)
async def deploylist_handler(client: Client, message: Message):
    """List all deployments (developer only)"""
    if not is_developer(message.from_user.id):
        await message.reply("❌ Developers only")
        return

    deployments = load_deployments()
    active = deployments.get('active', {})

    if not active:
        await message.reply("ℹ️ **NO ACTIVE DEPLOYMENTS**")
        return

    response = "📊 **ACTIVE DEPLOYMENTS**\n\n"

    for uid, info in active.items():
        response += f"**{info['user_name']}**\n"
        response += f"• ID: `{uid}`\n"
        response += f"• Port: {info['port']}\n"
        response += f"• PID: {info.get('pid', 'N/A')}\n"
        response += f"• Started: {info.get('started_at', 'N/A')}\n\n"

    response += f"**Total:** {len(active)} deployments"

    await message.reply(response)


# ============================================================================
# DEPLOY STOP COMMAND (Developer)
# ============================================================================

@app.on_message(filters.command("deploystop") & filters.private)
async def deploystop_handler(client: Client, message: Message):
    """Stop deployment (developer only)"""
    if not is_developer(message.from_user.id):
        await message.reply("❌ Developers only")
        return

    args = message.text.split()
    if len(args) < 2:
        await message.reply("**Usage:** `/deploystop <user_id>`")
        return

    user_id = args[1]

    deployments = load_deployments()

    if user_id not in deployments['active']:
        await message.reply(f"❌ No deployment found for user `{user_id}`")
        return

    info = deployments['active'][user_id]

    # Stop deployment
    success, error = await stop_deployment(user_id)

    if success:
        # Move to history
        deployments['history'].append({
            'user_id': user_id,
            'user_name': info['user_name'],
            'stopped_at': datetime.now().isoformat(),
            'stopped_by': message.from_user.id
        })

        del deployments['active'][user_id]
        save_deployments(deployments)

        await message.reply(
            f"✅ **DEPLOYMENT STOPPED**\n\n"
            f"**User:** {info['user_name']}\n"
            f"**Port:** {info['port']}\n\n"
            f"Deployment has been stopped."
        )

        # Notify user
        try:
            await client.send_message(
                int(user_id),
                "⚠️ **DEPLOYMENT STOPPED**\n\n"
                "Your deployment has been stopped by developer."
            )
        except:
            pass

        logger.info(f"Deployment stopped for {user_id} by {message.from_user.id}")

    else:
        await message.reply(
            f"❌ **STOP FAILED**\n\n"
            f"Error: {error}"
        )


# ============================================================================
# PENDING COMMAND (Developer)
# ============================================================================

@app.on_message(filters.command("pending") & filters.private)
async def pending_handler(client: Client, message: Message):
    """List pending requests (developer only)"""
    if not is_developer(message.from_user.id):
        await message.reply("❌ Developers only")
        return

    deployments = load_deployments()
    pending = deployments.get('pending', {})

    if not pending:
        await message.reply("ℹ️ **NO PENDING REQUESTS**")
        return

    response = "⏳ **PENDING REQUESTS**\n\n"

    for uid, info in pending.items():
        response += f"**{info['user_name']}**\n"
        response += f"• ID: `{uid}`\n"
        response += f"• Username: {info['username']}\n"
        response += f"• Requested: {info['requested_at']}\n\n"

    response += f"**Total:** {len(pending)} requests"

    await message.reply(response)


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Start the deployer bot"""
    print("=" * 60)
    print("VZ DEPLOYER BOT v0.0.0.69")
    print("Multi-user deployment manager")
    print("=" * 60)
    print()

    logger.info("Starting VZ Deployer Bot...")
    logger.info(f"Bot Token: {BOT_TOKEN[:20]}...")
    logger.info(f"Developers: {DEVELOPER_IDS}")

    # Create data directories
    os.makedirs("data", exist_ok=True)
    os.makedirs(DEPLOY_BASE_DIR, exist_ok=True)

    # Run bot
    app.run()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
        print("\n\n⚠️  Stopping bot...")
        print("👋 Goodbye!")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
