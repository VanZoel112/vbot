"""
VZ ASSISTANT v0.0.0.69
Global Data Manager - Blacklist & Lock with Auto Git Push

2025© Vzoel Fox's Lutpan
Founder & DEVELOPER : @VZLfxs
"""

import json
import os
import asyncio
from typing import List, Dict
import subprocess
from datetime import datetime

class GlobalDataManager:
    """Manage global blacklist and lock data with auto git push."""

    def __init__(self, data_dir: str = "data"):
        """Initialize global data manager."""
        self.data_dir = data_dir
        self.bl_file = os.path.join(data_dir, "global_blacklist.json")
        self.lock_file = os.path.join(data_dir, "global_lock.json")

        # Ensure data directory exists
        os.makedirs(data_dir, exist_ok=True)

        # Initialize files if not exist
        if not os.path.exists(self.bl_file):
            self._save_json(self.bl_file, {})
        if not os.path.exists(self.lock_file):
            self._save_json(self.lock_file, {})

    def _load_json(self, filepath: str) -> Dict:
        """Load JSON file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _save_json(self, filepath: str, data: Dict):
        """Save JSON file."""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    async def _git_push(self, message: str):
        """Auto commit and push to git."""
        try:
            # Git add
            subprocess.run(['git', 'add', self.bl_file, self.lock_file],
                         check=True, cwd=os.path.dirname(self.data_dir))

            # Git commit
            commit_msg = f"{message}\n\n🤖 Auto-commit at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            subprocess.run(['git', 'commit', '-m', commit_msg],
                         check=True, cwd=os.path.dirname(self.data_dir))

            # Git push
            subprocess.run(['git', 'push', 'origin', 'main'],
                         check=True, cwd=os.path.dirname(self.data_dir))

            return True
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Git push failed: {e}")
            return False

    # ============================================================================
    # BLACKLIST MANAGEMENT
    # ============================================================================

    def get_blacklist(self, user_id: int) -> List[int]:
        """Get user's blacklist."""
        data = self._load_json(self.bl_file)
        return data.get(str(user_id), [])

    def add_to_blacklist(self, user_id: int, chat_id: int) -> bool:
        """Add chat to blacklist."""
        data = self._load_json(self.bl_file)
        user_key = str(user_id)

        if user_key not in data:
            data[user_key] = []

        if chat_id not in data[user_key]:
            data[user_key].append(chat_id)
            self._save_json(self.bl_file, data)

            # Auto git push
            asyncio.create_task(self._git_push(
                f"Add chat {chat_id} to blacklist for user {user_id}"
            ))
            return True
        return False

    def remove_from_blacklist(self, user_id: int, chat_id: int) -> bool:
        """Remove chat from blacklist."""
        data = self._load_json(self.bl_file)
        user_key = str(user_id)

        if user_key in data and chat_id in data[user_key]:
            data[user_key].remove(chat_id)
            self._save_json(self.bl_file, data)

            # Auto git push
            asyncio.create_task(self._git_push(
                f"Remove chat {chat_id} from blacklist for user {user_id}"
            ))
            return True
        return False

    def is_blacklisted(self, user_id: int, chat_id: int) -> bool:
        """Check if chat is blacklisted."""
        blacklist = self.get_blacklist(user_id)
        return chat_id in blacklist

    # ============================================================================
    # LOCK MANAGEMENT (Shadow Clear)
    # ============================================================================

    def get_locked_users(self, user_id: int) -> Dict[int, List[int]]:
        """Get user's locked users per chat."""
        data = self._load_json(self.lock_file)
        return data.get(str(user_id), {})

    def add_to_lock(self, user_id: int, chat_id: int, target_id: int) -> bool:
        """Add user to lock list for a chat."""
        data = self._load_json(self.lock_file)
        user_key = str(user_id)
        chat_key = str(chat_id)

        if user_key not in data:
            data[user_key] = {}
        if chat_key not in data[user_key]:
            data[user_key][chat_key] = []

        if target_id not in data[user_key][chat_key]:
            data[user_key][chat_key].append(target_id)
            self._save_json(self.lock_file, data)

            # Auto git push
            asyncio.create_task(self._git_push(
                f"Lock user {target_id} in chat {chat_id} for {user_id}"
            ))
            return True
        return False

    def remove_from_lock(self, user_id: int, chat_id: int, target_id: int) -> bool:
        """Remove user from lock list."""
        data = self._load_json(self.lock_file)
        user_key = str(user_id)
        chat_key = str(chat_id)

        if user_key in data and chat_key in data[user_key]:
            if target_id in data[user_key][chat_key]:
                data[user_key][chat_key].remove(target_id)
                self._save_json(self.lock_file, data)

                # Auto git push
                asyncio.create_task(self._git_push(
                    f"Unlock user {target_id} in chat {chat_id} for {user_id}"
                ))
                return True
        return False

    def is_locked(self, user_id: int, chat_id: int, target_id: int) -> bool:
        """Check if user is locked in chat."""
        data = self._load_json(self.lock_file)
        user_key = str(user_id)
        chat_key = str(chat_id)

        if user_key in data and chat_key in data[user_key]:
            return target_id in data[user_key][chat_key]
        return False

print("✅ Global Data Manager loaded")
