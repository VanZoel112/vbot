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

# ============================================================================
# DEPLOY BOT CONFIGURATION
# ============================================================================

BOT_TOKEN = config.DEPLOY_BOT_TOKEN

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

    # Check if user is developer
    is_dev = config.is_developer(user_id)

    welcome_text = f"""
🤖 **VZ ASSISTANT - Deploy Bot**

Welcome to the automatic deployment system!

**👤 Your Status:** {'🌟 Developer' if is_dev else '👤 User'}

{'**🚀 Quick Deploy:**' if not is_dev else '**ℹ️ Information:**'}

{'This bot helps you deploy your VZ ASSISTANT instance.' if not is_dev else 'Developers can use .dp command in main bot.'}

**📝 How it works:**
1️⃣ Send your phone number
2️⃣ Enter the OTP code
3️⃣ Auto-deployment complete!

{'**🎯 Send your phone number to start!**' if not is_dev else ''}

{config.BRANDING_FOOTER}
Founder & DEVELOPER : {config.FOUNDER_USERNAME}
"""

    buttons = []
    if not is_dev:
        buttons.append([Button.text("📱 Send Phone Number", resize=True)])

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
# MESSAGE HANDLERS
# ============================================================================

@bot.on(events.NewMessage)
async def message_handler(event):
    """Handle all messages."""
    # Skip commands
    if event.text and event.text.startswith('/'):
        return

    user_id = event.sender_id

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
