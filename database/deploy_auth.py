"""
VZ ASSISTANT v0.0.0.69
Deploy Bot Authorization Database

2025© Vzoel Fox's Lutpan
Founder & DEVELOPER : @VZLfxs
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Optional

class DeployAuthDB:
    """Manage deploy bot authorization."""

    def __init__(self, db_path: str = "database/deploy_auth.db"):
        """Initialize database."""
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.create_tables()

    def create_tables(self):
        """Create authorization tables."""
        cursor = self.conn.cursor()

        # Approved users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS approved_users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                approved_by INTEGER,
                approved_at TIMESTAMP,
                notes TEXT
            )
        """)

        # Pending requests table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pending_requests (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                requested_at TIMESTAMP,
                reason TEXT
            )
        """)

        # Rejected users table (optional - for tracking)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rejected_users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                rejected_by INTEGER,
                rejected_at TIMESTAMP,
                reason TEXT
            )
        """)

        self.conn.commit()

    def is_approved(self, user_id: int) -> bool:
        """Check if user is approved."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT user_id FROM approved_users WHERE user_id = ?",
            (user_id,)
        )
        return cursor.fetchone() is not None

    def has_pending_request(self, user_id: int) -> bool:
        """Check if user has pending request."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT user_id FROM pending_requests WHERE user_id = ?",
            (user_id,)
        )
        return cursor.fetchone() is not None

    def add_request(self, user_id: int, username: str, first_name: str, reason: str = None):
        """Add deploy access request."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO pending_requests
            (user_id, username, first_name, requested_at, reason)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, username, first_name, datetime.now(), reason))
        self.conn.commit()

    def approve_user(self, user_id: int, approved_by: int, notes: str = None):
        """Approve user for deploy access."""
        cursor = self.conn.cursor()

        # Get user info from pending requests
        cursor.execute(
            "SELECT username, first_name FROM pending_requests WHERE user_id = ?",
            (user_id,)
        )
        user_data = cursor.fetchone()

        if user_data:
            username, first_name = user_data
        else:
            # If not in pending, try to get from rejected or use defaults
            username = None
            first_name = None

        # Add to approved users
        cursor.execute("""
            INSERT OR REPLACE INTO approved_users
            (user_id, username, first_name, approved_by, approved_at, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, username, first_name, approved_by, datetime.now(), notes))

        # Remove from pending requests
        cursor.execute("DELETE FROM pending_requests WHERE user_id = ?", (user_id,))

        # Remove from rejected if exists
        cursor.execute("DELETE FROM rejected_users WHERE user_id = ?", (user_id,))

        self.conn.commit()

    def reject_user(self, user_id: int, rejected_by: int, reason: str = None):
        """Reject user deploy access."""
        cursor = self.conn.cursor()

        # Get user info from pending requests
        cursor.execute(
            "SELECT username, first_name FROM pending_requests WHERE user_id = ?",
            (user_id,)
        )
        user_data = cursor.fetchone()

        if user_data:
            username, first_name = user_data

            # Add to rejected users
            cursor.execute("""
                INSERT OR REPLACE INTO rejected_users
                (user_id, username, first_name, rejected_by, rejected_at, reason)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, username, first_name, rejected_by, datetime.now(), reason))

        # Remove from pending requests
        cursor.execute("DELETE FROM pending_requests WHERE user_id = ?", (user_id,))

        self.conn.commit()

    def revoke_access(self, user_id: int):
        """Revoke user deploy access."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM approved_users WHERE user_id = ?", (user_id,))
        self.conn.commit()

    def get_pending_requests(self) -> List[dict]:
        """Get all pending requests."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT user_id, username, first_name, requested_at, reason
            FROM pending_requests
            ORDER BY requested_at DESC
        """)

        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def get_approved_users(self) -> List[dict]:
        """Get all approved users."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT user_id, username, first_name, approved_by, approved_at, notes
            FROM approved_users
            ORDER BY approved_at DESC
        """)

        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def get_user_status(self, user_id: int) -> dict:
        """Get user authorization status."""
        cursor = self.conn.cursor()

        # Check if approved
        cursor.execute(
            "SELECT * FROM approved_users WHERE user_id = ?",
            (user_id,)
        )
        approved = cursor.fetchone()
        if approved:
            return {"status": "approved", "data": dict(approved)}

        # Check if pending
        cursor.execute(
            "SELECT * FROM pending_requests WHERE user_id = ?",
            (user_id,)
        )
        pending = cursor.fetchone()
        if pending:
            return {"status": "pending", "data": dict(pending)}

        # Check if rejected
        cursor.execute(
            "SELECT * FROM rejected_users WHERE user_id = ?",
            (user_id,)
        )
        rejected = cursor.fetchone()
        if rejected:
            return {"status": "rejected", "data": dict(rejected)}

        return {"status": "none", "data": None}

    def close(self):
        """Close database connection."""
        self.conn.close()
