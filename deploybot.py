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

    if status_info["status"] == "approved":
        # User is approved - show deploy info
        welcome_text = f"""
✅ **VZ ASSISTANT - Deploy Bot**

Welcome back, {user.first_name}!

**👤 Your Status:** ✅ Approved

**🚀 Ready to Deploy:**
You are authorized to deploy VZ ASSISTANT.

**📝 How it works:**
1️⃣ Send your phone number
2️⃣ Enter the OTP code
3️⃣ Auto-deployment complete!

**🎯 Send your phone number to start!**

{config.BRANDING_FOOTER}
Founder & DEVELOPER : {config.FOUNDER_USERNAME}
"""
        buttons = [[Button.text("📱 Send Phone Number", resize=True)]]
        await event.respond(welcome_text, buttons=buttons)

    elif status_info["status"] == "pending":
        # User has pending request
        await event.respond(f"""
⏳ **Access Request Pending**

Hi {user.first_name},

Your access request is **pending approval**.
A developer will review your request soon.

**📊 Request Status:** ⏳ Waiting for approval
**⏰ Requested:** {status_info["data"]["requested_at"]}

Please wait for developer approval.

{config.BRANDING_FOOTER}
""")

    elif status_info["status"] == "rejected":
        # User was rejected
        rejected_data = status_info["data"]
        await event.respond(f"""
❌ **Access Denied**

Hi {user.first_name},

Your access request was **rejected**.

**Reason:** {rejected_data.get("reason", "Not specified")}

If you believe this is a mistake, please contact:
{config.FOUNDER_USERNAME}

{config.BRANDING_FOOTER}
""")

    else:
        # User not authorized - show request access
        welcome_text = f"""
🤖 **VZ ASSISTANT - Deploy Bot**

Hi {user.first_name}!

**👤 Your Status:** 🔒 Not Authorized

**📝 Access Required:**
To use this deploy bot, you need approval from a developer.

**🎯 Request Access:**
Use `/request [reason]` to request deploy access.

**Example:**
`/request I want to test VZ ASSISTANT`

**Contact Developer:**
{config.FOUNDER_USERNAME}

{config.BRANDING_FOOTER}
"""
        await event.respond(welcome_text)

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

{config.BRANDING_FOOTER}
""")

    # Notify all developers
    for dev_id in config.DEVELOPER_IDS:
        try:
            await bot.send_message(dev_id, f"""
🔔 **New Deploy Access Request**

**👤 User Info:**
├ Name: {user.first_name}
├ Username: @{user.username if user.username else 'None'}
├ User ID: `{user_id}`
{'├ Reason: ' + reason if reason else ''}

**🛠️ Actions:**
• `/approve {user_id}` - Approve request
• `/reject {user_id} [reason]` - Reject request
• `/check {user_id}` - View details

Use `/pending` to see all requests.
""")
        except:
            pass

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
    notes = event.pattern_match.group(2)

    # Approve user
    auth_db.approve_user(target_id, event.sender_id, notes)

    await event.respond(f"""
✅ **User Approved**

**User ID:** `{target_id}`
{'**Notes:** ' + notes if notes else ''}

User can now deploy via this bot.
""")

    # Notify user
    try:
        await bot.send_message(target_id, f"""
🎉 **Deploy Access Approved!**

Congratulations! Your deploy access has been approved.

**✅ You can now:**
1. Use `/start` to begin deployment
2. Send your phone number
3. Enter OTP code
4. Deploy your VZ ASSISTANT

{config.BRANDING_FOOTER}
Founder & DEVELOPER : {config.FOUNDER_USERNAME}
""")
    except:
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

    # Get or create session
    if user_id not in deploy_sessions:
        deploy_sessions[user_id] = DeploymentSession(user_id)
        await deploy_sessions[user_id].start_deployment()

    session = deploy_sessions[user_id]

    # Handle based on state
    if session.state == 'waiting_phone':
        # Extract phone number
        phone = event.text.strip()

        # Validate phone format
        if not phone.startswith('+'):
            phone = '+' + phone

        await event.respond(f"📱 Sending code to {phone}...")

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
        code = event.text.strip()

        await event.respond("🔄 Verifying code...")

        success, result = await session.verify_code(code)

        if success:
            me = result

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

**🎉 You're all set!**

Your VZ ASSISTANT is now running.
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
║              Deploy Bot                                  ║
║                                                          ║
║              {config.BRANDING_FOOTER}                    ║
║              Founder & DEVELOPER : {config.FOUNDER_USERNAME}               ║
╚══════════════════════════════════════════════════════════╝

🤖 Starting Deploy Bot...
""")

    await bot.start(bot_token=BOT_TOKEN)

    print("\n✅ Deploy Bot is running!")
    print("📱 Users can now deploy via @YourBotUsername")
    print("\n🔄 Bot is active... (Press Ctrl+C to stop)\n")

    await bot.run_until_disconnected()

# ============================================================================
# RUN
# ============================================================================

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Deploy Bot stopped")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
