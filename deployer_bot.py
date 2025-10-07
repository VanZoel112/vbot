#!/usr/bin/env python3
"""
VZ DEPLOYER BOT v0.0.0.69
Multi-user deployment manager - Simplified with ..ok approval

Flow:
1. User message bot
2. Bot forward to developer
3. Developer reply ..ok di PM bot → user approved
4. User /setsession and /deploy

2025© Vzoel Fox's Lutpan
"""

import os
import sys
import json
import logging
import asyncio
import subprocess
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import Message

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s'
)

logger = logging.getLogger('VZDeployerBot')

# Config
BOT_TOKEN = "7257252641:AAGKRXlf-GCJxsaqFUT1BgH8gRxUptIvQLQ"
API_ID = 29919905
API_HASH = "717957f0e3ae20a7db004d08b66bfd30"
DEVELOPER_IDS = [8024282347, 7553981355]

# Data files
DEPLOY_DATA_FILE = "data/deployments.json"
SESSION_DATA_FILE = "data/deploy_sessions.json"
APPROVED_USERS_FILE = "data/approved_users.json"
DEPLOY_BASE_DIR = "deployments"

# Helpers
def load_json(filepath, default=None):
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
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w') as f:
        json.dump(f, indent=2)

def load_deployments():
    return load_json(DEPLOY_DATA_FILE, {"active": {}, "history": []})

def save_deployments(data):
    save_json(DEPLOY_DATA_FILE, data)

def load_sessions():
    return load_json(SESSION_DATA_FILE, {})

def save_sessions(data):
    save_json(SESSION_DATA_FILE, data)

def load_approved_users():
    return load_json(APPROVED_USERS_FILE, {"approved": []})

def is_approved(user_id):
    approved = load_approved_users()
    return user_id in approved.get("approved", [])

def get_next_port():
    deployments = load_deployments()
    used_ports = [d.get('port', 0) for d in deployments['active'].values()]
    port = 8000
    while port in used_ports:
        port += 1
    return port

def create_user_env(user_id, session_string, port):
    user_dir = os.path.join(DEPLOY_BASE_DIR, str(user_id))
    os.makedirs(user_dir, exist_ok=True)
    
    env_content = f"""API_ID={API_ID}
API_HASH={API_HASH}
SESSION_STRING={session_string}
DEVELOPER_IDS={','.join(map(str, DEVELOPER_IDS))}
OWNER_ID={user_id}
"""
    
    with open(os.path.join(user_dir, '.env'), 'w') as f:
        f.write(env_content)
    
    return user_dir

async def start_deployment(user_id, user_dir):
    try:
        pm2_name = f"vbot_{user_id}"
        check = subprocess.run(["pm2", "id", pm2_name], capture_output=True)
        
        if check.returncode == 0:
            subprocess.run(["pm2", "restart", pm2_name])
        else:
            cmd = [
                "pm2", "start", "main.py",
                "--name", pm2_name,
                "--interpreter", "python3",
                "--", f"--env-file={os.path.join(user_dir, '.env')}"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                return False, result.stderr
        
        # Get PID
        pm2_list = subprocess.run(["pm2", "jlist"], capture_output=True, text=True)
        if pm2_list.returncode == 0:
            processes = json.loads(pm2_list.stdout)
            for proc in processes:
                if proc.get('name') == pm2_name:
                    return True, proc.get('pid')
        
        return True, None
    except Exception as e:
        return False, str(e)

async def stop_deployment(user_id):
    try:
        pm2_name = f"vbot_{user_id}"
        subprocess.run(["pm2", "stop", pm2_name], capture_output=True)
        subprocess.run(["pm2", "delete", pm2_name], capture_output=True)
        return True, None
    except Exception as e:
        return False, str(e)

# Pyrogram client
app = Client(
    "vz_deployer_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    workdir="sessions"
)

@app.on_message(filters.command("start") & filters.private)
async def start_handler(client, message):
    user_id = message.from_user.id
    is_dev = user_id in DEVELOPER_IDS
    
    text = f"""🤖 **VZ DEPLOYER BOT**

Hello {message.from_user.first_name}!
"""
    
    if is_dev:
        text += "\n**Role:** DEVELOPER\n\n**Commands:**\n"
        text += "• `/deploylist` - List deployments\n"
        text += "• `/deploystop <user_id>` - Stop deployment\n"
        text += "\n**Approval:**\nUse `..ok` di userbot PM untuk approve user"
    elif is_approved(user_id):
        text += "\n**Status:** ✅ Approved\n\n**Commands:**\n"
        text += "• `/setsession <string>` - Set session\n"
        text += "• `/deploy` - Deploy bot\n"
        text += "• `/mystatus` - Check status"
    else:
        text += "\n**Status:** ❌ Not Approved\n\n"
        text += "Chat bot ini, developer akan approve dengan `..ok`"
    
    await message.reply(text)

@app.on_message(filters.private & ~filters.command(["start", "setsession", "deploy", "mystatus", "deploylist", "deploystop"]))
async def forward_to_dev(client, message):
    """Forward non-command messages to developers for approval"""
    user_id = message.from_user.id
    
    # Skip if already approved or developer
    if user_id in DEVELOPER_IDS or is_approved(user_id):
        return
    
    # Forward to all developers
    for dev_id in DEVELOPER_IDS:
        try:
            await client.send_message(
                dev_id,
                f"📩 **NEW USER**\n\n"
                f"**User:** {message.from_user.first_name}\n"
                f"**Username:** @{message.from_user.username or 'no_username'}\n"
                f"**User ID:** `{user_id}`\n"
                f"**Message:** {message.text or '[Media]'}\n\n"
                f"Reply `..ok` untuk approve deployment"
            )
        except:
            pass
    
    await message.reply(
        "⚠️ **Menunggu Approval**\n\n"
        "Kamu belum dapat akses deploy tunggu diaprove developer dan jangan spam\n\n"
        "Pesan kamu telah dikirim ke developer."
    )

@app.on_message(filters.command("setsession") & filters.private)
async def setsession_handler(client, message):
    user_id = message.from_user.id
    
    if not is_approved(user_id):
        await message.reply("❌ Belum di-approve. Chat bot dan tunggu `..ok` dari developer.")
        return
    
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply("**Usage:** `/setsession <session_string>`")
        return
    
    session_string = args[1].strip()
    
    if len(session_string) < 100:
        await message.reply("❌ Session string terlalu pendek")
        return
    
    sessions = load_sessions()
    sessions[str(user_id)] = {
        'session': session_string,
        'updated_at': datetime.now().isoformat()
    }
    save_sessions(sessions)
    
    await message.reply(
        "✅ **Session Saved**\n\n"
        "Session tersimpan. Sekarang bisa `/deploy`\n\n"
        "⚠️ Hapus pesan session kamu!"
    )
    
    try:
        await message.delete()
    except:
        pass

@app.on_message(filters.command("deploy") & filters.private)
async def deploy_handler(client, message):
    user_id = message.from_user.id
    
    if not is_approved(user_id):
        await message.reply("❌ Belum di-approve")
        return
    
    sessions = load_sessions()
    if str(user_id) not in sessions:
        await message.reply("❌ Set session dulu: `/setsession <string>`")
        return
    
    deployments = load_deployments()
    if str(user_id) in deployments['active']:
        info = deployments['active'][str(user_id)]
        await message.reply(
            f"⚠️ **Already Deployed**\n\n"
            f"Port: {info.get('port')}\n"
            f"Status: Running"
        )
        return
    
    status_msg = await message.reply("⏳ Deploying...")
    
    try:
        session_string = sessions[str(user_id)]['session']
        port = get_next_port()
        user_dir = create_user_env(user_id, session_string, port)
        
        success, result = await start_deployment(user_id, user_dir)
        
        if success:
            deployments['active'][str(user_id)] = {
                'user_name': message.from_user.first_name,
                'port': port,
                'pid': result,
                'started_at': datetime.now().isoformat()
            }
            save_deployments(deployments)
            
            await status_msg.edit(
                f"✅ **DEPLOYED**\n\n"
                f"Port: {port}\n"
                f"PID: {result}\n"
                f"Status: Running"
            )
        else:
            await status_msg.edit(f"❌ **FAILED**\n\n{str(result)[:200]}")
    
    except Exception as e:
        await status_msg.edit(f"❌ Error: {str(e)[:200]}")

@app.on_message(filters.command("mystatus") & filters.private)
async def mystatus_handler(client, message):
    user_id = message.from_user.id
    
    if not is_approved(user_id):
        await message.reply("❌ Belum di-approve")
        return
    
    deployments = load_deployments()
    
    if str(user_id) in deployments['active']:
        info = deployments['active'][str(user_id)]
        await message.reply(
            f"✅ **DEPLOYMENT ACTIVE**\n\n"
            f"Port: {info.get('port')}\n"
            f"PID: {info.get('pid')}\n"
            f"Started: {info.get('started_at')}"
        )
    else:
        await message.reply("ℹ️ No deployment\n\nUse `/deploy` to deploy")

@app.on_message(filters.command("deploylist") & filters.private)
async def deploylist_handler(client, message):
    if message.from_user.id not in DEVELOPER_IDS:
        await message.reply("❌ Developer only")
        return
    
    deployments = load_deployments()
    active = deployments.get('active', {})
    
    if not active:
        await message.reply("ℹ️ No active deployments")
        return
    
    text = "📊 **ACTIVE DEPLOYMENTS**\n\n"
    for uid, info in active.items():
        text += f"**{info['user_name']}**\n"
        text += f"• ID: `{uid}`\n"
        text += f"• Port: {info['port']}\n\n"
    
    text += f"Total: {len(active)}"
    await message.reply(text)

@app.on_message(filters.command("deploystop") & filters.private)
async def deploystop_handler(client, message):
    if message.from_user.id not in DEVELOPER_IDS:
        await message.reply("❌ Developer only")
        return
    
    args = message.text.split()
    if len(args) < 2:
        await message.reply("**Usage:** `/deploystop <user_id>`")
        return
    
    user_id = args[1]
    deployments = load_deployments()
    
    if user_id not in deployments['active']:
        await message.reply(f"❌ No deployment for `{user_id}`")
        return
    
    success, error = await stop_deployment(user_id)
    
    if success:
        info = deployments['active'][user_id]
        del deployments['active'][user_id]
        save_deployments(deployments)
        
        await message.reply(f"✅ Stopped deployment for {info['user_name']}")
    else:
        await message.reply(f"❌ Failed: {error}")

def main():
    logger.info("Starting VZ Deployer Bot...")
    os.makedirs("data", exist_ok=True)
    os.makedirs(DEPLOY_BASE_DIR, exist_ok=True)
    app.run()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopping...")
    except Exception as e:
        logger.error(f"Fatal: {e}", exc_info=True)
        sys.exit(1)
