"""
Vzoel Fox's Lutpan - GitHub Integration Manager
Direct repository management from Telegram

Features:
- Push changes with auto-commit
- Pull with auto-rebase
- GitHub token management
- Conflict detection and handling

Author: Vzoel Fox's
Contact: @VZLfxs
"""

import os
import subprocess
import logging
from typing import Dict, Optional, Tuple
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class GitManager:
    """
    Git operations manager for Vzoel Fox's Lutpan
    Handles GitHub integration directly from Telegram
    """

    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path).resolve()
        self.token_file = self.repo_path / ".git_token"
        self.config_file = self.repo_path / ".env"

    def _run_command(self, command: list, capture_output: bool = True) -> Tuple[bool, str, str]:
        """
        Run git command

        Returns:
            Tuple of (success, stdout, stderr)
        """
        try:
            result = subprocess.run(
                command,
                cwd=str(self.repo_path),
                capture_output=capture_output,
                text=True,
                timeout=60
            )
            success = result.returncode == 0
            return (success, result.stdout.strip(), result.stderr.strip())
        except subprocess.TimeoutExpired:
            return (False, "", "Command timed out")
        except Exception as e:
            return (False, "", str(e))

    def set_token(self, token: str) -> bool:
        """
        Store GitHub personal access token securely

        Args:
            token: GitHub classic token

        Returns:
            True if stored successfully
        """
        try:
            # Save token to file (should be in .gitignore)
            with open(self.token_file, 'w') as f:
                f.write(token)

            # Set restrictive permissions
            os.chmod(self.token_file, 0o600)

            logger.info("GitHub token saved")
            return True

        except Exception as e:
            logger.error(f"Token save error: {e}")
            return False

    def get_token(self) -> Optional[str]:
        """
        Retrieve stored GitHub token

        Returns:
            Token string or None
        """
        try:
            if self.token_file.exists():
                with open(self.token_file, 'r') as f:
                    return f.read().strip()
            return None
        except Exception as e:
            logger.error(f"Token read error: {e}")
            return None

    def has_token(self) -> bool:
        """Check if token is configured"""
        return self.token_file.exists() and bool(self.get_token())

    def get_status(self) -> Dict:
        """
        Get repository status

        Returns:
            Dict with status information
        """
        try:
            # Get current branch
            success, branch, _ = self._run_command(['git', 'branch', '--show-current'])
            current_branch = branch if success else "unknown"

            # Get status
            success, status_output, _ = self._run_command(['git', 'status', '--porcelain'])
            has_changes = bool(status_output) if success else False

            # Count files
            modified = 0
            untracked = 0
            if success and status_output:
                for line in status_output.split('\n'):
                    if line.startswith('??'):
                        untracked += 1
                    else:
                        modified += 1

            # Get remote status
            success, ahead_behind, _ = self._run_command([
                'git', 'rev-list', '--left-right', '--count',
                f'HEAD...origin/{current_branch}'
            ])

            commits_ahead = 0
            commits_behind = 0
            if success and ahead_behind:
                parts = ahead_behind.split()
                if len(parts) == 2:
                    commits_ahead = int(parts[0])
                    commits_behind = int(parts[1])

            # Get last commit info
            success, last_commit, _ = self._run_command([
                'git', 'log', '-1', '--pretty=format:%h - %s (%cr)'
            ])
            last_commit_info = last_commit if success else "No commits"

            return {
                'branch': current_branch,
                'has_changes': has_changes,
                'modified': modified,
                'untracked': untracked,
                'commits_ahead': commits_ahead,
                'commits_behind': commits_behind,
                'last_commit': last_commit_info,
                'has_token': self.has_token()
            }

        except Exception as e:
            logger.error(f"Status error: {e}")
            return {
                'error': str(e),
                'has_token': self.has_token()
            }

    def auto_commit(self, custom_message: Optional[str] = None) -> Tuple[bool, str]:
        """
        Auto-commit all changes with smart message

        Args:
            custom_message: Optional custom commit message

        Returns:
            Tuple of (success, message)
        """
        try:
            # Check if there are changes
            success, status, _ = self._run_command(['git', 'status', '--porcelain'])
            if not success:
                return (False, "Failed to check status")

            if not status:
                return (False, "No changes to commit")

            # Add all changes
            success, _, stderr = self._run_command(['git', 'add', '-A'])
            if not success:
                return (False, f"Failed to stage changes: {stderr}")

            # Generate commit message
            if custom_message:
                commit_message = custom_message
            else:
                # Smart commit message based on changes
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                commit_message = f"Update - {timestamp}"

            # Add branding footer
            commit_message += "\n\n🤖 Generated with Claude Code\nCo-Authored-By: Claude <noreply@anthropic.com>"

            # Commit
            success, _, stderr = self._run_command(['git', 'commit', '-m', commit_message])
            if not success:
                return (False, f"Commit failed: {stderr}")

            logger.info(f"Auto-committed: {commit_message.split(chr(10))[0]}")
            return (True, "Changes committed successfully")

        except Exception as e:
            logger.error(f"Commit error: {e}")
            return (False, str(e))

    def push(self, custom_message: Optional[str] = None) -> Tuple[bool, str]:
        """
        Push changes to GitHub

        Args:
            custom_message: Optional custom commit message

        Returns:
            Tuple of (success, message)
        """
        try:
            # Check token
            token = self.get_token()
            if not token:
                return (False, "GitHub token not configured. Use .settoken first")

            # Get current branch
            success, branch, _ = self._run_command(['git', 'branch', '--show-current'])
            if not success:
                return (False, "Failed to get current branch")

            # Auto-commit if there are changes
            success, commit_status, _ = self._run_command(['git', 'status', '--porcelain'])
            if commit_status:
                commit_success, commit_message = self.auto_commit(custom_message)
                if not commit_success:
                    return (False, commit_message)

            # Get remote URL
            success, remote_url, _ = self._run_command(['git', 'remote', 'get-url', 'origin'])
            if not success:
                return (False, "Failed to get remote URL")

            # Modify URL to include token
            if remote_url.startswith('https://'):
                # Extract repo path
                repo_path = remote_url.replace('https://github.com/', '')
                auth_url = f"https://{token}@github.com/{repo_path}"
            else:
                return (False, "Only HTTPS remotes are supported")

            # Push
            success, stdout, stderr = self._run_command(['git', 'push', auth_url, branch])

            if success:
                logger.info(f"Pushed to {branch}")
                return (True, f"Successfully pushed to {branch}")
            else:
                # Check if we need to pull first
                if 'rejected' in stderr.lower() or 'non-fast-forward' in stderr.lower():
                    return (False, "Push rejected. Run .pull first to sync changes")
                return (False, f"Push failed: {stderr}")

        except Exception as e:
            logger.error(f"Push error: {e}")
            return (False, str(e))

    def pull(self) -> Tuple[bool, str]:
        """
        Pull latest changes from GitHub

        Returns:
            Tuple of (success, message)
        """
        try:
            # Check token
            token = self.get_token()
            if not token:
                return (False, "GitHub token not configured. Use .settoken first")

            # Get current branch
            success, branch, _ = self._run_command(['git', 'branch', '--show-current'])
            if not success:
                return (False, "Failed to get current branch")

            # Check for uncommitted changes
            success, status, _ = self._run_command(['git', 'status', '--porcelain'])
            has_changes = bool(status)

            # Stash if needed
            if has_changes:
                success, _, stderr = self._run_command(['git', 'stash', 'push', '-m', 'Auto-stash before pull'])
                if not success:
                    return (False, f"Failed to stash changes: {stderr}")

            # Get remote URL and add token
            success, remote_url, _ = self._run_command(['git', 'remote', 'get-url', 'origin'])
            if not success:
                return (False, "Failed to get remote URL")

            if remote_url.startswith('https://'):
                repo_path = remote_url.replace('https://github.com/', '')
                auth_url = f"https://{token}@github.com/{repo_path}"
            else:
                return (False, "Only HTTPS remotes are supported")

            # Fetch
            success, _, stderr = self._run_command(['git', 'fetch', auth_url])
            if not success:
                return (False, f"Fetch failed: {stderr}")

            # Pull with rebase
            success, stdout, stderr = self._run_command(['git', 'pull', '--rebase', auth_url, branch])

            if success:
                # Pop stash if we stashed
                if has_changes:
                    stash_success, _, _ = self._run_command(['git', 'stash', 'pop'])
                    if not stash_success:
                        logger.warning("Failed to pop stash - you may need to resolve manually")

                logger.info(f"Pulled from {branch}")
                return (True, f"Successfully pulled from {branch}")
            else:
                # Check for conflicts
                if 'conflict' in stderr.lower():
                    return (False, "Merge conflicts detected. Please resolve manually")
                return (False, f"Pull failed: {stderr}")

        except Exception as e:
            logger.error(f"Pull error: {e}")
            return (False, str(e))

    def get_git_info(self) -> Dict:
        """Get general git repository information"""
        try:
            # Get remote URL
            success, remote_url, _ = self._run_command(['git', 'remote', 'get-url', 'origin'])
            remote = remote_url if success else "Unknown"

            # Remove token from display
            if '@github.com' in remote:
                remote = remote.split('@github.com')[-1]
                remote = 'https://github.com' + remote

            # Get total commits
            success, commit_count, _ = self._run_command(['git', 'rev-list', '--count', 'HEAD'])
            total_commits = commit_count if success else "Unknown"

            status = self.get_status()

            return {
                'remote': remote,
                'total_commits': total_commits,
                **status
            }

        except Exception as e:
            logger.error(f"Info error: {e}")
            return {'error': str(e)}
