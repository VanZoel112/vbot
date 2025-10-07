#!/usr/bin/env python3
"""
VZ ASSISTANT v0.0.0.69
Deploy Bot - Automatic Sudoer Deployment

2025© Vzoel Fox's Lutpan
Founder & DEVELOPER : @VZLfxs
"""

import asyncio
import os
from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError

import config
from database.models import DatabaseManager
from database.deploy_auth import DeployAuthDB
from helpers.pm2_manager import pm2_manager

# ============================================================================
# DEPLOY BOT CONFIGURATION
# ============================================================================

BOT_TOKEN = config.DEPLOY_BOT_TOKEN
auth_db = DeployAuthDB()  # Authorization database

if not BOT_TOKEN:
    print("❌ DEPLOY_BOT_TOKEN not set in config.py")
    print("Please set DEPLOY_BOT_TOKEN to use the deploy bot")
    exit(1)

# Bot instance
bot = TelegramClient('deploy_bot', config.API_ID, config.API_HASH)

# User sessions in deployment process
deploy_sessions = {}

# Callback payload constants
REQUEST_ACCESS_ACTION = b'request_access'
START_DEPLOY_ACTION = b'start_deploy'
CHECK_STATUS_ACTION = b'check_status'


def build_user_portal_message(user, status_info):
    """Create the main menu text and buttons for a user."""

    status = status_info["status"]
    data = status_info.get("data") or {}
    first_name = getattr(user, "first_name", None) or getattr(user, "last_name", None) or getattr(user, "username", None) or "User"

    if status == "approved":
        text = f"""✅ **VZ ASSISTANT - Deploy Bot**

Selamat datang kembali, {first_name}!

**👤 Status Kamu:** ✅ Disetujui

**🚀 Cara Deploy:**
1️⃣ Tekan tombol **🚀 Mulai Deploy** di bawah
2️⃣ Kirim nomor telepon kamu (format +62...)
3️⃣ Masukkan kode OTP yang dikirim Telegram
4️⃣ Bot akan menjalankan PM2 otomatis

Kalau butuh bantuan, hubungi {config.FOUNDER_USERNAME}.

{config.BRANDING_FOOTER}
Founder & DEVELOPER : {config.FOUNDER_USERNAME}
"""

        buttons = [[Button.inline("🚀 Mulai Deploy", START_DEPLOY_ACTION)]]

    elif status == "pending":
        requested_at = data.get("requested_at", "Unknown")
        text = f"""⏳ **Permintaan Akses Sedang Diproses**

Hi {first_name}, kami sudah menerima permintaan akses deploy kamu.

Seorang developer sedang meninjau permintaanmu. Kamu akan mendapat notifikasi begitu disetujui supaya bisa menekan tombol deploy lagi.

**📊 Status Permintaan:**
├ User ID: `{data.get('user_id', 'Unknown')}`
├ Username: @{data.get('username') or 'None'}
└ Diminta pada: {requested_at}

{config.BRANDING_FOOTER}
Founder & DEVELOPER : {config.FOUNDER_USERNAME}
"""

        buttons = [[Button.inline("🔄 Cek Status Persetujuan", CHECK_STATUS_ACTION)]]

    elif status == "rejected":
        reason = data.get("reason", "Tidak ada alasan yang diberikan")
        text = f"""❌ **Permintaan Akses Ditolak**

Hi {first_name}, permintaan akses deploy kamu pernah ditolak.

**Alasan:** {reason}

Kalau kamu sudah memperbaiki kebutuhanmu, tekan tombol di bawah untuk mengajukan ulang. Developer akan meninjaunya kembali.

{config.BRANDING_FOOTER}
Founder & DEVELOPER : {config.FOUNDER_USERNAME}
"""

        buttons = [[Button.inline("🔁 Ajukan Ulang Akses Deploy", REQUEST_ACCESS_ACTION)]]

    else:
        text = f"""🤖 **VZ ASSISTANT - Deploy Bot**

Hi {first_name}!

**Status Kamu:** 🔒 Belum Punya Akses Deploy

Tekan tombol di bawah untuk mengajukan akses. Developer akan mendapat notifikasi dan kamu akan diberi tahu ketika sudah boleh menekan tombol deploy.

{config.BRANDING_FOOTER}
Founder & DEVELOPER : {config.FOUNDER_USERNAME}
"""

        buttons = [[Button.inline("🔔 Ajukan Akses Deploy", REQUEST_ACCESS_ACTION)]]

    return text, buttons


def resolve_status_for_menu(user_id, user, status_info):
    """Treat developers as always approved for UI flows."""

    if config.is_developer(user_id) and status_info["status"] != "approved":
        return {
            "status": "approved",
            "data": {
                "user_id": user_id,
                "username": getattr(user, "username", None),
                "first_name": getattr(user, "first_name", None),
            },
        }

    return status_info


async def notify_developers_of_request(user, reason):
    """Inform developers about a new access request."""

    for dev_id in config.DEVELOPER_IDS:
        try:
            await bot.send_message(dev_id, f"""🔔 **New Deploy Access Request**

**👤 User Info:**
├ Name: {user.first_name or 'Unknown'}
├ Username: @{user.username if user.username else 'None'}
├ User ID: `{user.id}`
{'├ Reason: ' + reason if reason else ''}

**🛠️ Actions:**
• `/approve {user.id}` - Approve request
• `/reject {user.id} [reason]` - Reject request
• `/check {user.id}` - View details

Gunakan `/pending` untuk melihat semua permintaan.
""")
        except Exception:
            pass

# ============================================================================
# DEPLOYMENT STATE MACHINE
# ============================================================================

class DeploymentSession:
    """Track deployment state for a user."""

    def __init__(self, user_id):
        """Initialize deployment session."""
        self.user_id = user_id
        self.state = 'idle'
        self.phone = None
        self.phone_code_hash = None
        self.client = None
        self.session_string = None

    async def start_deployment(self):
        """Start deployment process."""
        self.state = 'waiting_phone'

    async def set_phone(self, phone):
        """Set phone number and request code."""
        self.phone = phone
        self.state = 'waiting_code'

        # Create client for this session
        self.client = TelegramClient(
            StringSession(),
            config.API_ID,
            config.API_HASH
        )

        await self.client.connect()

        # Request code
        try:
            result = await self.client.send_code_request(phone)
            self.phone_code_hash = result.phone_code_hash
            return True, "Code sent to your phone"
        except Exception as e:
            return False, f"Failed to send code: {str(e)}"

    async def verify_code(self, code):
        """Verify code and complete login."""
        try:
            await self.client.sign_in(
                phone=self.phone,
                code=code,
                phone_code_hash=self.phone_code_hash
            )

            # Get session string
            self.session_string = self.client.session.save()

            # Get user info
            me = await self.client.get_me()

            # Save to database
            db = DatabaseManager(config.get_sudoer_db_path(me.id))
            db.add_user(
                user_id=me.id,
                username=me.username,
                first_name=me.first_name,
                is_sudoer=True,
                is_developer=False
            )
            db.close()

            # Auto-save session to JSON for multi-client management
            import json
            sessions_dir = "sessions"
            os.makedirs(sessions_dir, exist_ok=True)
            json_file = os.path.join(sessions_dir, "sudoer_sessions.json")

            try:
                # Load existing sessions
                if os.path.exists(json_file):
                    with open(json_file, 'r') as f:
                        existing_sessions = json.load(f)
                else:
                    existing_sessions = {"sessions": []}

                # Check if user already exists
                user_exists = False
                for existing in existing_sessions["sessions"]:
                    if existing["user_id"] == me.id:
                        # Update existing session
                        existing["session_string"] = self.session_string
                        existing["username"] = me.username
                        existing["first_name"] = me.first_name
                        user_exists = True
                        break

                if not user_exists:
                    # Add new session
                    existing_sessions["sessions"].append({
                        "user_id": me.id,
                        "username": me.username,
                        "first_name": me.first_name,
                        "phone": self.phone,
                        "session_string": self.session_string,
                        "is_sudoer": True,
                        "is_developer": False
                    })

                # Save to JSON
                with open(json_file, 'w') as f:
                    json.dump(existing_sessions, f, indent=2)

                print(f"✅ Sudoer session saved: {me.first_name} ({me.id})")
            except Exception as e:
                print(f"⚠️  Could not save session to JSON: {e}")

            # 🚀 AUTONOMOUS PM2 DEPLOYMENT
            # Start PM2 process automatically for this sudoer
            try:
                print(f"\n⚡ Starting autonomous PM2 deployment for {me.first_name}...")

                # Check if PM2 is installed
                if await pm2_manager.is_pm2_installed():
                    # Start PM2 process
                    success, message = await pm2_manager.start_sudoer(
                        user_id=me.id,
                        session_string=self.session_string,
                        username=me.username,
                        first_name=me.first_name
                    )

                    if success:
                        print(f"✅ PM2 deployment successful: vz-sudoer-{me.id}")
                        # Store PM2 info in result
                        me.process_name = f"vz-sudoer-{me.id}"
                        me.process_deployed = True

                        # Get process status
                        status = await pm2_manager.get_process_status(me.id)
                        if status.get('exists'):
                            me.process_status = status.get('status')
                            me.process_pid = status.get('pid')
                    else:
                        print(f"❌ PM2 deployment failed: {message}")
                        me.process_deployed = False
                        me.deployment_error = message
                else:
                    print("⚠️  PM2 not installed - manual start required")
                    me.process_deployed = False
                    me.deployment_error = "PM2 not installed (npm install -g pm2)"

            except Exception as e:
                print(f"❌ PM2 deployment error: {e}")
                me.process_deployed = False
                me.deployment_error = str(e)

            self.state = 'completed'

            return True, me

        except PhoneCodeInvalidError:
            return False, "Invalid code"
        except SessionPasswordNeededError:
            self.state = 'waiting_password'
            return False, "2FA password required"
        except Exception as e:
            return False, f"Login failed: {str(e)}"

    async def cleanup(self):
        """Cleanup session."""
        if self.client:
            await self.client.disconnect()
        self.state = 'idle'

# ============================================================================
# BOT COMMANDS
# ============================================================================

@bot.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    """Handle /start command."""
    user_id = event.sender_id
    user = await event.get_sender()

    # Check if user is developer
    is_dev = config.is_developer(user_id)

    if is_dev:
        # Developer message
        welcome_text = f"""
🌟 **VZ ASSISTANT - Deploy Bot**

Welcome, Developer!

**👤 Your Status:** 🌟 Developer (Full Access)

**🛠️ Developer Commands:**
• `/approve <user_id>` - Approve deploy access
• `/reject <user_id> [reason]` - Reject request
• `/revoke <user_id>` - Revoke access
• `/pending` - View pending requests
• `/approved` - View approved users
• `/check <user_id>` - Check user status

**ℹ️ For deployment:**
Use `.dp` command in main bot

{config.BRANDING_FOOTER}
Founder & DEVELOPER : {config.FOUNDER_USERNAME}
"""
        await event.respond(welcome_text)
        return

    # Check authorization status
    status_info = auth_db.get_user_status(user_id)

    welcome_text, buttons = build_user_portal_message(user, status_info)
    await event.respond(welcome_text, buttons=buttons)

@bot.on(events.NewMessage(pattern='/cancel'))
async def cancel_handler(event):
    """Cancel deployment process."""
    user_id = event.sender_id

    if user_id in deploy_sessions:
        await deploy_sessions[user_id].cleanup()
        del deploy_sessions[user_id]

    await event.respond("❌ Deployment cancelled.")

@bot.on(events.NewMessage(pattern='/status'))
async def status_handler(event):
    """Check deployment status."""
    user_id = event.sender_id

    if user_id in deploy_sessions:
        session = deploy_sessions[user_id]
        status_text = f"""
📊 **Deployment Status**

**State:** {session.state}
**Phone:** {session.phone if session.phone else 'Not set'}

Use /cancel to cancel deployment
"""
    else:
        status_text = "ℹ️ No active deployment. Use /start to begin."

    await event.respond(status_text)

# ============================================================================
# REQUEST ACCESS COMMAND
# ============================================================================

@bot.on(events.NewMessage(pattern=r'/request(?:\s+(.+))?'))
async def request_handler(event):
    """Handle access request."""
    user_id = event.sender_id
    user = await event.get_sender()
    reason = event.pattern_match.group(1)

    # Check if developer
    if config.is_developer(user_id):
        await event.respond("🌟 Developers have automatic access!")
        return

    # Check current status
    status_info = auth_db.get_user_status(user_id)

    if status_info["status"] == "approved":
        await event.respond("✅ You are already approved!")
        return

    if status_info["status"] == "pending":
        await event.respond("⏳ You already have a pending request!")
        return

    # Add request
    auth_db.add_request(
        user_id=user_id,
        username=user.username,
        first_name=user.first_name,
        reason=reason
    )

    await event.respond(f"""
✅ **Access Request Submitted**

Hi {user.first_name},

Your request has been submitted to the developers.

**📊 Request Info:**
├ User ID: `{user_id}`
├ Username: @{user.username if user.username else 'None'}
{'├ Reason: ' + reason if reason else ''}
└ Status: ⏳ Pending

**⏰ Next Steps:**
A developer will review your request soon.
You will be notified when approved.
Setelah ada notifikasi approval, buka bot ini lagi dan tekan tombol **🚀 Mulai Deploy** untuk melanjutkan.

{config.BRANDING_FOOTER}
""")

    # Notify all developers
    await notify_developers_of_request(user, reason)


@bot.on(events.CallbackQuery(data=REQUEST_ACCESS_ACTION))
async def request_access_callback(event):
    """Handle inline button to request deploy access."""

    user_id = event.sender_id

    if config.is_developer(user_id):
        await event.answer("Developer punya akses otomatis. Kamu bisa langsung deploy.", alert=True)
        return

    user = await event.get_sender()
    status_info = auth_db.get_user_status(user_id)
    menu_status = resolve_status_for_menu(user_id, user, status_info)

    if status_info["status"] == "approved":
        text, buttons = build_user_portal_message(user, menu_status)
        await event.edit(text, buttons=buttons)
        await event.answer("Akses deploy kamu sudah disetujui! Tekan 🚀 Mulai Deploy untuk mulai.", alert=True)
        return

    if status_info["status"] == "pending":
        text, buttons = build_user_portal_message(user, menu_status)
        await event.edit(text, buttons=buttons)
        await event.answer("Permintaan akses kamu masih diproses. Tunggu notifikasi ya!", alert=True)
        return

    reason = "Requested via deploy bot button"
    auth_db.add_request(user_id, user.username, user.first_name, reason=reason)
    await notify_developers_of_request(user, reason)

    updated_status = auth_db.get_user_status(user_id)
    menu_status = resolve_status_for_menu(user_id, user, updated_status)
    text, buttons = build_user_portal_message(user, menu_status)
    await event.edit(text, buttons=buttons)
    await event.answer("Permintaan akses terkirim! Tunggu persetujuan developer.", alert=True)


@bot.on(events.CallbackQuery(data=CHECK_STATUS_ACTION))
async def check_status_callback(event):
    """Handle inline button to re-check access status."""

    user_id = event.sender_id
    user = await event.get_sender()
    status_info = auth_db.get_user_status(user_id)
    menu_status = resolve_status_for_menu(user_id, user, status_info)

    text, buttons = build_user_portal_message(user, menu_status)
    await event.edit(text, buttons=buttons)

    status = menu_status["status"]
    if status == "approved":
        message = "Akses deploy kamu sudah disetujui! Tekan 🚀 Mulai Deploy."
    elif status == "pending":
        message = "Permintaan kamu masih menunggu persetujuan developer."
    elif status == "rejected":
        message = "Permintaan kamu ditolak. Ajukan ulang jika perlu."
    else:
        message = "Kamu belum mengajukan akses deploy."

    await event.answer(message, alert=True)


@bot.on(events.CallbackQuery(data=START_DEPLOY_ACTION))
async def start_deploy_callback(event):
    """Handle inline button to kick off the deployment flow."""

    user_id = event.sender_id
    user = await event.get_sender()
    status_info = auth_db.get_user_status(user_id)
    is_dev = config.is_developer(user_id)

    if not is_dev and status_info["status"] != "approved":
        menu_status = resolve_status_for_menu(user_id, user, status_info)
        text, buttons = build_user_portal_message(user, menu_status)
        await event.edit(text, buttons=buttons)

        if status_info["status"] == "pending":
            await event.answer("Masih menunggu persetujuan developer. Tunggu notifikasi ya!", alert=True)
        else:
            await event.answer("Ajukan akses deploy dulu sebelum memulai.", alert=True)
        return

    session = deploy_sessions.get(user_id)
    if not session:
        session = DeploymentSession(user_id)
        deploy_sessions[user_id] = session

    await session.start_deployment()

    instructions = f"""🚀 **Mulai Deploy Sekarang**

Kirim nomor telepon kamu di chat ini dengan format `+62xxxx`.
Setelah menerima kode OTP dari Telegram, balas dengan 5 digit kode tersebut.

Gunakan /cancel kalau ingin membatalkan proses deploy.

{config.BRANDING_FOOTER}
Founder & DEVELOPER : {config.FOUNDER_USERNAME}
"""

    await bot.send_message(user_id, instructions)

    menu_status = resolve_status_for_menu(user_id, user, status_info)
    text, buttons = build_user_portal_message(user, menu_status)
    await event.edit(text, buttons=buttons)

    await event.answer("Kirim nomor telepon kamu sekarang untuk melanjutkan deploy.", alert=True)

# ============================================================================
# DEVELOPER COMMANDS
# ============================================================================

@bot.on(events.NewMessage(pattern=r'/approve\s+(\d+)(?:\s+(.+))?'))
async def approve_handler(event):
    """Approve user deploy access."""
    if not config.is_developer(event.sender_id):
        await event.respond("❌ Developer only command!")
        return

    target_id = int(event.pattern_match.group(1))
    raw_notes = event.pattern_match.group(2)
    notes = raw_notes.strip() if raw_notes else None

    # Try to fetch latest metadata for the target user
    username = None
    display_name = None
    try:
        target = await bot.get_entity(target_id)
        username = target.username
        name_parts = [target.first_name, target.last_name]
        display_name = ' '.join(part for part in name_parts if part) or target.first_name or target.last_name
    except Exception:
        target = None

    created, updated, record = auth_db.approve_user(
        target_id,
        event.sender_id,
        notes,
        username=username,
        first_name=display_name,
    )

    if created:
        status_title = "✅ **User Approved**"
        footer_line = "User can now deploy via this bot."
    elif updated:
        status_title = "✅ **User Approval Updated**"
        footer_line = "User approval details have been updated."
    else:
        status_title = "ℹ️ **User Already Approved**"
        footer_line = "No changes were made; user already has deploy access."

    detail_lines = [
        f"**User ID:** `{record['user_id']}`",
        f"├ Name: {record.get('first_name') or 'Unknown'}",
        f"├ Username: @{record.get('username') or 'None'}",
        f"├ Approved: {record.get('approved_at', 'Unknown')}",
    ]
    if record.get('notes'):
        detail_lines.append(f"├ Notes: {record['notes']}")
    detail_lines.append(f"└ Approved by: `{record.get('approved_by', 'Unknown')}`")

    detail_text = "\n".join(detail_lines)

    await event.respond(
        f"""{status_title}

{detail_text}

{footer_line}
"""
    )

    if created:
        # Notify user only when approval is newly granted
        try:
            await bot.send_message(target_id, f"""
🎉 **Deploy Access Approved!**

Selamat! Akses deploy kamu sudah disetujui oleh developer.

**✅ Langkah Berikutnya:**
1. Buka bot deploy: {config.DEPLOY_BOT_USERNAME}
2. Tekan tombol **🚀 Mulai Deploy**
3. Kirim nomor telepon kamu (format +62...)
4. Masukkan kode OTP dari Telegram

Kalau kamu melihat pesan ini sebagai notifikasi, cukup kembali ke bot deploy dan tekan tombol deploy lagi untuk melanjutkan.

{config.BRANDING_FOOTER}
Founder & DEVELOPER : {config.FOUNDER_USERNAME}
""")
        except Exception:
            pass

@bot.on(events.NewMessage(pattern=r'/reject\s+(\d+)(?:\s+(.+))?'))
async def reject_handler(event):
    """Reject user deploy access."""
    if not config.is_developer(event.sender_id):
        await event.respond("❌ Developer only command!")
        return

    target_id = int(event.pattern_match.group(1))
    reason = event.pattern_match.group(2) or "Not specified"

    # Reject user
    auth_db.reject_user(target_id, event.sender_id, reason)

    await event.respond(f"""
❌ **User Rejected**

**User ID:** `{target_id}`
**Reason:** {reason}

User has been notified.
""")

    # Notify user
    try:
        await bot.send_message(target_id, f"""
❌ **Deploy Access Denied**

Your deploy access request was rejected.

**Reason:** {reason}

If you have questions, please contact:
{config.FOUNDER_USERNAME}

{config.BRANDING_FOOTER}
""")
    except:
        pass

@bot.on(events.NewMessage(pattern=r'/revoke\s+(\d+)'))
async def revoke_handler(event):
    """Revoke user deploy access."""
    if not config.is_developer(event.sender_id):
        await event.respond("❌ Developer only command!")
        return

    target_id = int(event.pattern_match.group(1))

    # Revoke access
    auth_db.revoke_access(target_id)

    await event.respond(f"""
🔒 **Access Revoked**

**User ID:** `{target_id}`

Deploy access has been revoked.
""")

    # Notify user
    try:
        await bot.send_message(target_id, f"""
🔒 **Deploy Access Revoked**

Your deploy access has been revoked by a developer.

If you have questions, please contact:
{config.FOUNDER_USERNAME}

{config.BRANDING_FOOTER}
""")
    except:
        pass

@bot.on(events.NewMessage(pattern='/pending'))
async def pending_handler(event):
    """View pending requests."""
    if not config.is_developer(event.sender_id):
        await event.respond("❌ Developer only command!")
        return

    requests = auth_db.get_pending_requests()

    if not requests:
        await event.respond("ℹ️ No pending requests.")
        return

    text = "⏳ **Pending Deploy Requests:**\n\n"

    for req in requests:
        text += f"""**👤 {req['first_name']}**
├ Username: @{req['username'] or 'None'}
├ User ID: `{req['user_id']}`
├ Requested: {req['requested_at']}
{'├ Reason: ' + req['reason'] if req['reason'] else ''}
└ Actions: `/approve {req['user_id']}` or `/reject {req['user_id']}`

"""

    await event.respond(text[:4000])  # Telegram message limit

@bot.on(events.NewMessage(pattern='/approved'))
async def approved_handler(event):
    """View approved users."""
    if not config.is_developer(event.sender_id):
        await event.respond("❌ Developer only command!")
        return

    users = auth_db.get_approved_users()

    if not users:
        await event.respond("ℹ️ No approved users.")
        return

    text = "✅ **Approved Users:**\n\n"

    for user in users:
        text += f"""**👤 {user['first_name']}**
├ Username: @{user['username'] or 'None'}
├ User ID: `{user['user_id']}`
├ Approved: {user['approved_at']}
{'├ Notes: ' + user['notes'] if user['notes'] else ''}
└ Revoke: `/revoke {user['user_id']}`

"""

    await event.respond(text[:4000])  # Telegram message limit

@bot.on(events.NewMessage(pattern=r'/check\s+(\d+)'))
async def check_handler(event):
    """Check user authorization status."""
    if not config.is_developer(event.sender_id):
        await event.respond("❌ Developer only command!")
        return

    target_id = int(event.pattern_match.group(1))
    status_info = auth_db.get_user_status(target_id)

    if status_info["status"] == "none":
        await event.respond(f"ℹ️ User `{target_id}` has no record.")
        return

    data = status_info["data"]
    status_emoji = {
        "approved": "✅",
        "pending": "⏳",
        "rejected": "❌"
    }.get(status_info["status"], "❓")

    text = f"""{status_emoji} **User Status: {status_info["status"].upper()}**

**👤 User Info:**
├ User ID: `{target_id}`
├ Username: @{data.get('username') or 'None'}
├ Name: {data.get('first_name', 'Unknown')}
"""

    if status_info["status"] == "approved":
        text += f"""
**✅ Approved:**
├ Approved at: {data['approved_at']}
{'├ Notes: ' + data['notes'] if data.get('notes') else ''}
└ Action: `/revoke {target_id}`
"""
    elif status_info["status"] == "pending":
        text += f"""
**⏳ Pending:**
├ Requested: {data['requested_at']}
{'├ Reason: ' + data['reason'] if data.get('reason') else ''}
└ Actions: `/approve {target_id}` or `/reject {target_id}`
"""
    elif status_info["status"] == "rejected":
        text += f"""
**❌ Rejected:**
├ Rejected at: {data['rejected_at']}
{'├ Reason: ' + data['reason'] if data.get('reason') else ''}
└ Action: `/approve {target_id}` (to re-approve)
"""

    await event.respond(text)

# ============================================================================
# MESSAGE HANDLERS
# ============================================================================

@bot.on(events.NewMessage)
async def message_handler(event):
    """Handle all messages."""
    # Skip commands
    if event.text and event.text.startswith('/'):
        return

    user_id = event.sender_id

    # Authorization check - only developers and approved users can deploy
    is_dev = config.is_developer(user_id)
    is_approved = auth_db.is_approved(user_id)

    if not is_dev and not is_approved:
        await event.respond("❌ **Access Denied**\n\nYou must be approved to deploy. Use /start for more info.")
        return

    session = deploy_sessions.get(user_id)

    if not session or session.state == 'idle':
        await event.respond(
            "ℹ️ Belum ada proses deploy yang berjalan. Buka /start lalu tekan tombol 🚀 Mulai Deploy terlebih dahulu."
        )
        return

    # Handle based on state
    if not event.raw_text and getattr(event, "message", None) and getattr(event.message, "contact", None):
        # Extract phone from contact sharing
        contact_phone = event.message.contact.phone_number
        if contact_phone and not contact_phone.startswith('+'):
            contact_phone = '+' + contact_phone
        event_text = contact_phone
    else:
        event_text = (event.raw_text or "").strip()

    if session.state == 'waiting_phone':
        # Extract phone number
        phone = event_text

        if not phone:
            await event.respond("❌ Format nomor tidak valid. Ketik nomor kamu, contoh: +628123456789.")
            return

        # Validate phone format
        if not phone.startswith('+'):
            phone = '+' + phone

        await event.respond(f"📱 Mengirim kode ke {phone}...")

        success, message = await session.set_phone(phone)

        if success:
            await event.respond(f"""
✅ {message}

**📝 Enter the code:**
Send the 5-digit code you received

Use /cancel to cancel deployment
""")
        else:
            await event.respond(f"❌ {message}")
            del deploy_sessions[user_id]

    elif session.state == 'waiting_code':
        code = event_text

        await event.respond("🔄 Verifying code...")

        success, result = await session.verify_code(code)

        if success:
            me = result

            # Build success message with PM2 process info
            success_text = f"""
✅ **Deployment Successful!**

**👤 Account Information:**
├ Name: {me.first_name}
├ Username: @{me.username if me.username else 'None'}
├ User ID: `{me.id}`
└ Role: Sudoer

**📊 Session Details:**
├ Session String: Generated ✅
├ Database: Created ✅
└ Status: Active ✅
"""

            # Add PM2 process info if deployed
            if hasattr(me, 'process_deployed') and me.process_deployed:
                success_text += f"""
**⚡ PM2 Process:**
├ Process Name: `{me.process_name}`
├ Status: {me.process_status if hasattr(me, 'process_status') else 'Running'} ✅
├ PID: `{me.process_pid if hasattr(me, 'process_pid') else 'N/A'}`
├ Mode: Autonomous Deploy
└ Auto-restart: Enabled ✅

**💡 Management:**
• View: `pm2 list`
• Logs: `pm2 logs {me.process_name}`
• Stop: `pm2 stop {me.process_name}`
• Restart: `pm2 restart {me.process_name}`
"""
            elif hasattr(me, 'deployment_error'):
                success_text += f"""
**⚠️ PM2 Process:**
├ Deployment: Failed
├ Reason: {me.deployment_error}
└ Session saved, manual start required

**🔧 Manual Start:**
`python run_sudoer.py {me.id}`
or
`pm2 start run_sudoer.py --name vz-sudoer-{me.id} --interpreter python3 -- {me.id}`
"""

            success_text += f"""
**🎉 You're all set!**

Your VZ ASSISTANT is {'running as PM2 process' if hasattr(me, 'process_deployed') and me.process_deployed else 'ready to start'}.
Check your Saved Messages for updates.

{config.BRANDING_FOOTER}
Founder & DEVELOPER : {config.FOUNDER_USERNAME}
"""

            await event.respond(success_text)

            # Cleanup
            await session.cleanup()
            del deploy_sessions[user_id]

        else:
            await event.respond(f"❌ {result}\n\nUse /cancel to start over")

# ============================================================================
# MAIN FUNCTION
# ============================================================================

async def main():
    """Main bot function."""
    print(f"""
╔══════════════════════════════════════════════════════════╗
║              VZ ASSISTANT v{config.BOT_VERSION}                      ║
║              Deploy Bot (PM2 Multi-User)                 ║
║                                                          ║
║              {config.BRANDING_FOOTER}                    ║
║              Founder & DEVELOPER : {config.FOUNDER_USERNAME}               ║
╚══════════════════════════════════════════════════════════╝

🤖 Starting Deploy Bot...
""")

    # Check PM2 availability
    print("⚡ Checking PM2 installation...")
    if await pm2_manager.is_pm2_installed():
        print("✅ PM2 is installed and ready")

        # List existing sudoer processes
        processes = await pm2_manager.list_all_sudoers()
        if processes:
            print(f"📊 Found {len(processes)} existing sudoer process(es)")
            for proc in processes[:3]:  # Show first 3
                print(f"   • {proc['name']} - {proc['status']}")
    else:
        print("⚠️  PM2 not installed - auto-deployment disabled")
        print("   Install: npm install -g pm2")

    await bot.start(bot_token=BOT_TOKEN)

    print("\n✅ Deploy Bot is running!")
    print(f"📱 Users can now deploy via {config.DEPLOY_BOT_USERNAME}")
    print("⚡ PM2 auto-deployment: ENABLED")
    print("\n🔄 Bot is active... (Press Ctrl+C to stop)\n")

    await bot.run_until_disconnected()

# ============================================================================
# RUN
# ============================================================================

if __name__ == "__main__":
    try:
        # Use uvloop for better async performance
        import uvloop
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        print("🚀 Using uvloop for optimized async performance")
    except ImportError:
        print("⚠️  uvloop not installed, using default asyncio")

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Deploy Bot stopped")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
