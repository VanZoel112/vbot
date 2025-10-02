#!/usr/bin/env python3
"""
VZ ASSISTANT v0.0.0.69
Session String Generator

2025© Vzoel Fox's Lutpan
Founder & DEVELOPER : @VZLfxs
"""

from telethon import TelegramClient
from telethon.sessions import StringSession
import asyncio
import os

# Import config
import config

# ============================================================================
# ASCII ART BANNER
# ============================================================================

BANNER = """
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║              VZ ASSISTANT v0.0.0.69                      ║
║              Session String Generator                    ║
║                                                          ║
║              2025© Vzoel Fox's Lutpan                    ║
║              Founder & DEVELOPER : @VZLfxs               ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
"""

# ============================================================================
# SESSION STRING GENERATOR
# ============================================================================

async def generate_session_string():
    """Generate Telethon session string."""
    print(BANNER)
    print("📱 Telegram Session String Generator\n")

    # Ask for phone number
    phone = input("Enter your phone number (with country code, e.g., +628123456789): ")

    # Create client with StringSession
    client = TelegramClient(
        StringSession(),
        config.API_ID,
        config.API_HASH
    )

    await client.start(phone=phone)

    # Get session string
    session_string = client.session.save()

    # Get user info
    me = await client.get_me()

    print("\n✅ Login Successful!")
    print(f"👤 Name: {me.first_name}")
    print(f"📧 Username: @{me.username}" if me.username else "📧 Username: None")
    print(f"🆔 User ID: {me.id}")
    print(f"\n🔑 Your Session String:\n")
    print("=" * 80)
    print(session_string)
    print("=" * 80)

    # Save to file
    output_dir = "sessions"
    os.makedirs(output_dir, exist_ok=True)

    output_file = os.path.join(output_dir, f"session_{me.id}.txt")
    with open(output_file, 'w') as f:
        f.write(f"VZ ASSISTANT Session String\n")
        f.write(f"User: {me.first_name} (@{me.username})\n")
        f.write(f"User ID: {me.id}\n")
        f.write(f"Generated: {asyncio.get_event_loop().time()}\n")
        f.write(f"\nSession String:\n{session_string}\n")

    print(f"\n💾 Session string saved to: {output_file}")
    print("\n⚠️  IMPORTANT:")
    print("   • Keep this session string PRIVATE")
    print("   • Do NOT share with anyone")
    print("   • Anyone with this string can access your account")
    print("\n📝 Next Steps:")
    print("   1. Copy the session string above")
    print("   2. Save it in a secure location")
    print("   3. Use it to start VZ ASSISTANT")

    await client.disconnect()

# ============================================================================
# MULTIPLE SESSION GENERATOR
# ============================================================================

async def generate_multiple_sessions():
    """Generate multiple session strings."""
    print(BANNER)
    print("📱 Multiple Session Generator\n")

    sessions = []
    count = int(input("How many sessions do you want to generate? "))

    for i in range(count):
        print(f"\n{'='*60}")
        print(f"Session {i+1}/{count}")
        print(f"{'='*60}\n")

        phone = input(f"Enter phone number for session {i+1}: ")

        client = TelegramClient(
            StringSession(),
            config.API_ID,
            config.API_HASH
        )

        await client.start(phone=phone)

        session_string = client.session.save()
        me = await client.get_me()

        sessions.append({
            'phone': phone,
            'user_id': me.id,
            'username': me.username,
            'first_name': me.first_name,
            'session_string': session_string
        })

        print(f"✅ Session {i+1} generated for {me.first_name}")

        await client.disconnect()

    # Save all sessions
    output_file = os.path.join("sessions", "all_sessions.txt")
    with open(output_file, 'w') as f:
        f.write("VZ ASSISTANT - Multiple Sessions\n")
        f.write(f"Total Sessions: {len(sessions)}\n")
        f.write("="*80 + "\n\n")

        for i, session in enumerate(sessions, 1):
            f.write(f"Session {i}:\n")
            f.write(f"  Name: {session['first_name']}\n")
            f.write(f"  Username: @{session['username']}\n" if session['username'] else "  Username: None\n")
            f.write(f"  User ID: {session['user_id']}\n")
            f.write(f"  Phone: {session['phone']}\n")
            f.write(f"  Session String:\n  {session['session_string']}\n")
            f.write("\n" + "="*80 + "\n\n")

    print(f"\n💾 All sessions saved to: {output_file}")

# ============================================================================
# INTERACTIVE MENU
# ============================================================================

async def main():
    """Main interactive menu."""
    print(BANNER)
    print("Choose an option:\n")
    print("1. Generate Single Session String")
    print("2. Generate Multiple Session Strings")
    print("3. Exit")

    choice = input("\nEnter your choice (1-3): ")

    if choice == "1":
        await generate_session_string()
    elif choice == "2":
        await generate_multiple_sessions()
    elif choice == "3":
        print("👋 Goodbye!")
        return
    else:
        print("❌ Invalid choice!")

# ============================================================================
# RUN
# ============================================================================

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Process interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
