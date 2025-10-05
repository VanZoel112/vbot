"""
VZ ASSISTANT v0.0.0.69
VC Bridge - Communication between bot assistant and userbot for VC

2025© Vzoel Fox's Lutpan
Founder & DEVELOPER : @VZLfxs
"""

import os
import json
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime


class VCBridge:
    """Bridge for VC commands between bot assistant and userbot."""

    def __init__(self, bridge_file: str = "data/vc_bridge.json"):
        self.bridge_file = bridge_file
        self._ensure_bridge_file()

    def _ensure_bridge_file(self):
        """Ensure bridge file exists."""
        os.makedirs(os.path.dirname(self.bridge_file), exist_ok=True)
        if not os.path.exists(self.bridge_file):
            self._write_bridge({})

    def _read_bridge(self) -> Dict:
        """Read bridge data."""
        try:
            with open(self.bridge_file, 'r') as f:
                return json.load(f)
        except:
            return {}

    def _write_bridge(self, data: Dict):
        """Write bridge data."""
        with open(self.bridge_file, 'w') as f:
            json.dump(data, f, indent=2)

    async def send_command(self, chat_id: int, command: str, params: Dict = None) -> str:
        """
        Send VC command to userbot.

        Args:
            chat_id: Target chat ID
            command: Command type (join, leave, play, etc)
            params: Additional parameters

        Returns:
            str: Command ID
        """
        command_id = f"{chat_id}_{int(datetime.now().timestamp() * 1000)}"

        data = self._read_bridge()
        data[command_id] = {
            "chat_id": chat_id,
            "command": command,
            "params": params or {},
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "result": None,
            "error": None
        }
        self._write_bridge(data)

        return command_id

    async def get_command_status(self, command_id: str) -> Optional[Dict]:
        """Get command status."""
        data = self._read_bridge()
        return data.get(command_id)

    async def wait_for_result(self, command_id: str, timeout: int = 30) -> Dict:
        """
        Wait for command result.

        Args:
            command_id: Command ID to wait for
            timeout: Timeout in seconds

        Returns:
            Dict: Command result
        """
        for _ in range(timeout * 2):  # Check every 0.5s
            status = await self.get_command_status(command_id)
            if status and status["status"] in ["completed", "error"]:
                return status
            await asyncio.sleep(0.5)

        return {
            "status": "timeout",
            "error": "Command timeout after 30s"
        }

    async def update_command(self, command_id: str, status: str, result: Any = None, error: str = None):
        """Update command status (called by userbot)."""
        data = self._read_bridge()
        if command_id in data:
            data[command_id]["status"] = status
            data[command_id]["result"] = result
            data[command_id]["error"] = error
            data[command_id]["updated_at"] = datetime.now().isoformat()
            self._write_bridge(data)

    async def cleanup_old_commands(self, max_age_hours: int = 1):
        """Clean up old commands."""
        data = self._read_bridge()
        now = datetime.now()

        cleaned_data = {}
        for cmd_id, cmd_data in data.items():
            created = datetime.fromisoformat(cmd_data["created_at"])
            age = (now - created).total_seconds() / 3600

            if age < max_age_hours:
                cleaned_data[cmd_id] = cmd_data

        self._write_bridge(cleaned_data)

    async def get_active_vc_sessions(self) -> Dict:
        """Get active VC sessions from userbot."""
        data = self._read_bridge()
        sessions = data.get("active_sessions", {})
        return sessions

    async def update_vc_session(self, chat_id: int, session_data: Dict):
        """Update VC session info (called by userbot)."""
        data = self._read_bridge()
        if "active_sessions" not in data:
            data["active_sessions"] = {}

        data["active_sessions"][str(chat_id)] = session_data
        self._write_bridge(data)

    async def remove_vc_session(self, chat_id: int):
        """Remove VC session (called by userbot)."""
        data = self._read_bridge()
        if "active_sessions" in data and str(chat_id) in data["active_sessions"]:
            del data["active_sessions"][str(chat_id)]
            self._write_bridge(data)
