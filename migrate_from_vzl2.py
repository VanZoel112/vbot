#!/usr/bin/env python3
"""
VZ ASSISTANT - Migration Script from vzl2 to vbot
Migrates blacklist words and locked users from vzl2 to vbot format

2025© Vzoel Fox's Lutpan
Founder & DEVELOPER : @VZLfxs
"""

import json
import os
import sys

# Paths
VZL2_BLACKLIST_FILE = "/data/data/com.termux/files/home/vzl2/blacklist_data.json"
VBOT_GCAST_BLACKLIST = "/data/data/com.termux/files/home/vbot/data/gcast_blacklist.json"

def load_vzl2_data():
    """Load data from vzl2 blacklist file."""
    if not os.path.exists(VZL2_BLACKLIST_FILE):
        print(f"❌ vzl2 blacklist file not found: {VZL2_BLACKLIST_FILE}")
        return None

    with open(VZL2_BLACKLIST_FILE, 'r') as f:
        return json.load(f)

def migrate_gcast_blacklist(vzl2_data):
    """Migrate locked users to vbot gcast blacklist."""
    locked_users = vzl2_data.get('locked_users', {})

    # Convert to vbot format (list of chat IDs)
    vbot_blacklist = []

    for chat_id, user_list in locked_users.items():
        # Add the chat itself to blacklist if it has locked users
        if user_list:
            try:
                vbot_blacklist.append(int(chat_id))
            except:
                pass

    # Load existing vbot blacklist
    if os.path.exists(VBOT_GCAST_BLACKLIST):
        with open(VBOT_GCAST_BLACKLIST, 'r') as f:
            existing = json.load(f)
    else:
        existing = []

    # Merge (avoid duplicates)
    for chat_id in vbot_blacklist:
        if chat_id not in existing:
            existing.append(chat_id)

    # Save merged blacklist
    os.makedirs(os.path.dirname(VBOT_GCAST_BLACKLIST), exist_ok=True)
    with open(VBOT_GCAST_BLACKLIST, 'w') as f:
        json.dump(existing, f, indent=2)

    return len(vbot_blacklist), len(existing)

def show_summary(vzl2_data):
    """Show summary of what will be migrated."""
    print("\n" + "="*60)
    print("VZL2 → VBOT MIGRATION SUMMARY")
    print("="*60)

    blacklist_words = vzl2_data.get('blacklist_words', {})
    locked_users = vzl2_data.get('locked_users', {})
    blacklist_active = vzl2_data.get('blacklist_active', {})

    print(f"\n📋 BLACKLIST WORDS:")
    for chat_id, words in blacklist_words.items():
        print(f"   Chat {chat_id}: {len(words)} word(s) - {words}")

    print(f"\n🔒 LOCKED USERS:")
    total_locked = 0
    for chat_id, users in locked_users.items():
        count = len(users)
        total_locked += count
        print(f"   Chat {chat_id}: {count} user(s)")

    print(f"\n⚙️  BLACKLIST STATUS:")
    for chat_id, active in blacklist_active.items():
        print(f"   Chat {chat_id}: {'Active' if active else 'Inactive'}")

    print(f"\n📊 TOTALS:")
    print(f"   Chats with blacklist words: {len(blacklist_words)}")
    print(f"   Chats with locked users: {len(locked_users)}")
    print(f"   Total locked users: {total_locked}")

    print("\n" + "="*60)
    print("MIGRATION NOTES:")
    print("="*60)
    print("✓ Locked users → Gcast blacklist (prevents broadcasts to those chats)")
    print("⚠ Blacklist words NOT migrated (vbot uses different system)")
    print("⚠ You'll need to re-add blacklist words manually in vbot")
    print("="*60 + "\n")

def main():
    print("🔄 VZ ASSISTANT - vzl2 to vbot Migration Tool\n")

    # Check for --dry-run flag
    dry_run = '--dry-run' in sys.argv

    # Load vzl2 data
    print("📂 Loading vzl2 data...")
    vzl2_data = load_vzl2_data()

    if not vzl2_data:
        return 1

    # Show summary
    show_summary(vzl2_data)

    if dry_run:
        print("🔍 DRY RUN MODE - No changes made")
        print("Run without --dry-run to perform actual migration\n")
        return 0

    print("\n🚀 Starting migration...\n")

    # Migrate gcast blacklist
    print("📝 Migrating locked users to gcast blacklist...")
    new_count, total_count = migrate_gcast_blacklist(vzl2_data)
    print(f"   ✅ Added {new_count} chat(s), total blacklist: {total_count} chat(s)")

    print("\n" + "="*60)
    print("✅ MIGRATION COMPLETE!")
    print("="*60)
    print("\n📌 NEXT STEPS:")
    print("1. Review gcast blacklist: cat data/gcast_blacklist.json")
    print("2. Restart vbot: .restart")
    print("3. Test gcast to verify blacklist works")
    print("4. Manually re-add blacklist words if needed (vbot uses different system)")
    print("\n")

    return 0

if __name__ == "__main__":
    sys.exit(main())
