"""
VZ ASSISTANT v0.0.0.69
PM2 Manager - Multi-User Process Management

2025© Vzoel Fox's Lutpan
Founder & DEVELOPER : @VZLfxs
"""

import asyncio
import json
import os
from typing import Dict, List, Optional, Tuple

class PM2Manager:
    """Manage PM2 processes for multi-user sudoer instances."""

    def __init__(self):
        """Initialize PM2 manager."""
        self.ecosystem_file = "ecosystem.config.js"
        self.sessions_file = "sessions/sudoer_sessions.json"

    async def run_command(self, command: str) -> Tuple[bool, str, str]:
        """
        Run PM2 command asynchronously.

        Args:
            command: PM2 command to execute

        Returns:
            tuple: (success, stdout, stderr)
        """
        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            stdout_str = stdout.decode().strip()
            stderr_str = stderr.decode().strip()

            success = process.returncode == 0

            return success, stdout_str, stderr_str

        except Exception as e:
            return False, "", str(e)

    async def is_pm2_installed(self) -> bool:
        """Check if PM2 is installed."""
        success, stdout, _ = await self.run_command("pm2 --version")
        return success

    async def start_sudoer(
        self,
        user_id: int,
        session_string: str,
        username: str = None,
        first_name: str = None
    ) -> Tuple[bool, str]:
        """
        Start PM2 process for sudoer.

        Args:
            user_id: Telegram user ID
            session_string: Telethon session string
            username: User's username
            first_name: User's first name

        Returns:
            tuple: (success, message)
        """
        try:
            process_name = f"vz-sudoer-{user_id}"

            # Check if already running
            success, stdout, _ = await self.run_command(f"pm2 describe {process_name}")
            if success and "online" in stdout.lower():
                # Restart existing process
                success, stdout, stderr = await self.run_command(f"pm2 restart {process_name}")
                if success:
                    return True, f"Restarted existing process: {process_name}"
                else:
                    return False, f"Failed to restart: {stderr}"

            # Start new process
            # Create process with session string as environment variable
            env_vars = f"SESSION_STRING='{session_string}' USER_ID={user_id}"

            command = (
                f"{env_vars} pm2 start run_sudoer.py "
                f"--name {process_name} "
                f"--interpreter python3 "
                f"--args '{user_id}' "
                f"--max-memory-restart 500M "
                f"--error logs/{process_name}-error.log "
                f"--output logs/{process_name}-out.log "
                f"--log-date-format 'YYYY-MM-DD HH:mm:ss'"
            )

            success, stdout, stderr = await self.run_command(command)

            if success:
                print(f"✅ PM2 process started: {process_name}")
                # Save process to ecosystem
                await self.save_to_ecosystem(user_id, username, first_name)
                return True, f"Process started: {process_name}"
            else:
                return False, f"Failed to start: {stderr}"

        except Exception as e:
            return False, f"PM2 error: {str(e)}"

    async def stop_sudoer(self, user_id: int) -> Tuple[bool, str]:
        """Stop PM2 process for sudoer."""
        process_name = f"vz-sudoer-{user_id}"
        success, stdout, stderr = await self.run_command(f"pm2 stop {process_name}")

        if success:
            return True, f"Process stopped: {process_name}"
        else:
            return False, f"Failed to stop: {stderr}"

    async def delete_sudoer(self, user_id: int) -> Tuple[bool, str]:
        """Delete PM2 process for sudoer."""
        process_name = f"vz-sudoer-{user_id}"
        success, stdout, stderr = await self.run_command(f"pm2 delete {process_name}")

        if success:
            # Remove from ecosystem
            await self.remove_from_ecosystem(user_id)
            return True, f"Process deleted: {process_name}"
        else:
            return False, f"Failed to delete: {stderr}"

    async def get_process_status(self, user_id: int) -> Dict:
        """Get status of sudoer process."""
        process_name = f"vz-sudoer-{user_id}"
        success, stdout, stderr = await self.run_command(f"pm2 jlist")

        if not success:
            return {"exists": False, "error": stderr}

        try:
            processes = json.loads(stdout)
            for proc in processes:
                if proc.get('name') == process_name:
                    return {
                        "exists": True,
                        "name": proc.get('name'),
                        "status": proc.get('pm2_env', {}).get('status'),
                        "pid": proc.get('pid'),
                        "uptime": proc.get('pm2_env', {}).get('pm_uptime'),
                        "memory": proc.get('monit', {}).get('memory'),
                        "cpu": proc.get('monit', {}).get('cpu'),
                        "restarts": proc.get('pm2_env', {}).get('restart_time', 0)
                    }

            return {"exists": False}

        except Exception as e:
            return {"exists": False, "error": str(e)}

    async def list_all_sudoers(self) -> List[Dict]:
        """List all VZ Assistant sudoer processes."""
        success, stdout, stderr = await self.run_command("pm2 jlist")

        if not success:
            return []

        try:
            processes = json.loads(stdout)
            result = []

            for proc in processes:
                name = proc.get('name', '')
                if name.startswith('vz-sudoer-'):
                    user_id = name.replace('vz-sudoer-', '')
                    result.append({
                        "user_id": user_id,
                        "name": name,
                        "status": proc.get('pm2_env', {}).get('status'),
                        "pid": proc.get('pid'),
                        "uptime": proc.get('pm2_env', {}).get('pm_uptime'),
                        "memory": proc.get('monit', {}).get('memory'),
                        "cpu": proc.get('monit', {}).get('cpu'),
                        "restarts": proc.get('pm2_env', {}).get('restart_time', 0)
                    })

            return result

        except Exception as e:
            print(f"⚠️  Error listing processes: {e}")
            return []

    async def save_to_ecosystem(
        self,
        user_id: int,
        username: str = None,
        first_name: str = None
    ):
        """Save process configuration to ecosystem file."""
        try:
            # This is optional - PM2 already manages processes
            # But we can save metadata for reference
            process_name = f"vz-sudoer-{user_id}"

            # Update sessions JSON with PM2 info
            if os.path.exists(self.sessions_file):
                with open(self.sessions_file, 'r') as f:
                    data = json.load(f)

                for session in data.get('sessions', []):
                    if session['user_id'] == user_id:
                        session['pm2_process'] = process_name
                        session['pm2_active'] = True
                        break

                with open(self.sessions_file, 'w') as f:
                    json.dump(data, f, indent=2)

                print(f"✅ Updated ecosystem data for {process_name}")

        except Exception as e:
            print(f"⚠️  Could not update ecosystem: {e}")

    async def remove_from_ecosystem(self, user_id: int):
        """Remove process from ecosystem file."""
        try:
            if os.path.exists(self.sessions_file):
                with open(self.sessions_file, 'r') as f:
                    data = json.load(f)

                for session in data.get('sessions', []):
                    if session['user_id'] == user_id:
                        session['pm2_active'] = False
                        break

                with open(self.sessions_file, 'w') as f:
                    json.dump(data, f, indent=2)

        except Exception as e:
            print(f"⚠️  Could not update ecosystem: {e}")

    async def save_all_processes(self):
        """Save all PM2 processes (pm2 save)."""
        success, stdout, stderr = await self.run_command("pm2 save")
        return success

    async def restart_all_sudoers(self):
        """Restart all VZ Assistant sudoer processes."""
        success, stdout, stderr = await self.run_command("pm2 restart all")
        return success, stdout if success else stderr

# Global instance
pm2_manager = PM2Manager()
