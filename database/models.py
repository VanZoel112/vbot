"""
VZ ASSISTANT v0.0.0.69
Database Models - SQLAlchemy ORM

2025© Vzoel Fox's Lutpan
Founder & DEVELOPER : @VZLfxs
"""

from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

Base = declarative_base()

# ============================================================================
# DATABASE MODELS
# ============================================================================

class User(Base):
    """User model for storing user information."""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True, nullable=False)
    username = Column(String(255))
    first_name = Column(String(255))
    last_name = Column(String(255))
    is_developer = Column(Boolean, default=False)
    is_sudoer = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Settings(Base):
    """Settings model for storing user preferences."""
    __tablename__ = 'settings'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    prefix = Column(String(10), default='.')
    pm_permit_enabled = Column(Boolean, default=False)
    pm_permit_message = Column(Text)
    auto_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PMPermit(Base):
    """PM Permit model for approved users."""
    __tablename__ = 'pm_permit'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)  # Owner user ID
    approved_user_id = Column(Integer, nullable=False)  # Approved user ID
    approved_username = Column(String(255))
    approved_at = Column(DateTime, default=datetime.utcnow)

class PaymentInfo(Base):
    """Payment information model."""
    __tablename__ = 'payment_info'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    payment_type = Column(String(50))  # dana, gopay, ovo, qris, etc.
    payment_number = Column(String(255))
    payment_name = Column(String(255))
    qr_code_path = Column(String(500))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Logs(Base):
    """Command execution logs."""
    __tablename__ = 'logs'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    command = Column(String(255))
    arguments = Column(Text)
    chat_id = Column(Integer)
    success = Column(Boolean, default=True)
    error_message = Column(Text)
    executed_at = Column(DateTime, default=datetime.utcnow)

class BlacklistGroup(Base):
    """Blacklisted groups for gcast."""
    __tablename__ = 'blacklist_groups'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    group_id = Column(Integer, nullable=False)
    group_name = Column(String(255))
    added_at = Column(DateTime, default=datetime.utcnow)

class LockUser(Base):
    """Locked users (shadow clear)."""
    __tablename__ = 'lock_users'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)  # Owner user ID
    locked_user_id = Column(Integer, nullable=False)  # Locked user ID
    locked_username = Column(String(255))
    group_id = Column(Integer)
    locked_at = Column(DateTime, default=datetime.utcnow)

# ============================================================================
# DATABASE MANAGER
# ============================================================================

class DatabaseManager:
    """Database manager for single user."""

    def __init__(self, db_path: str):
        """Initialize database manager."""
        self.db_path = db_path

        # Create directory if not exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        # Create engine
        self.engine = create_engine(f'sqlite:///{db_path}')

        # Create tables
        Base.metadata.create_all(self.engine)

        # Create session
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def add_user(self, user_id: int, username: str = None, first_name: str = None,
                 last_name: str = None, is_developer: bool = False, is_sudoer: bool = False):
        """Add or update user."""
        user = self.session.query(User).filter_by(user_id=user_id).first()

        if user:
            # Update existing user
            user.username = username
            user.first_name = first_name
            user.last_name = last_name
            user.is_developer = is_developer
            user.is_sudoer = is_sudoer
            user.updated_at = datetime.utcnow()
        else:
            # Create new user
            user = User(
                user_id=user_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
                is_developer=is_developer,
                is_sudoer=is_sudoer
            )
            self.session.add(user)

        self.session.commit()
        return user

    def get_user(self, user_id: int):
        """Get user by ID."""
        return self.session.query(User).filter_by(user_id=user_id).first()

    def get_prefix(self, user_id: int) -> str:
        """Get user's command prefix."""
        settings = self.session.query(Settings).filter_by(user_id=user_id).first()

        if settings:
            return settings.prefix

        # Create default settings
        settings = Settings(user_id=user_id, prefix='.')
        self.session.add(settings)
        self.session.commit()

        return '.'

    def update_prefix(self, user_id: int, prefix: str):
        """Update user's command prefix."""
        settings = self.session.query(Settings).filter_by(user_id=user_id).first()

        if settings:
            settings.prefix = prefix
            settings.updated_at = datetime.utcnow()
        else:
            settings = Settings(user_id=user_id, prefix=prefix)
            self.session.add(settings)

        self.session.commit()

    def get_settings(self, user_id: int):
        """Get user settings."""
        settings = self.session.query(Settings).filter_by(user_id=user_id).first()

        if not settings:
            settings = Settings(user_id=user_id)
            self.session.add(settings)
            self.session.commit()

        return settings

    def update_pm_permit(self, user_id: int, enabled: bool = None, message: str = None):
        """Update PM permit settings."""
        settings = self.get_settings(user_id)

        if enabled is not None:
            settings.pm_permit_enabled = enabled

        if message is not None:
            settings.pm_permit_message = message

        settings.updated_at = datetime.utcnow()
        self.session.commit()

    def approve_pm_user(self, user_id: int, approved_user_id: int, approved_username: str = None):
        """Approve user for PM."""
        # Check if already approved
        existing = self.session.query(PMPermit).filter_by(
            user_id=user_id,
            approved_user_id=approved_user_id
        ).first()

        if existing:
            return existing

        permit = PMPermit(
            user_id=user_id,
            approved_user_id=approved_user_id,
            approved_username=approved_username
        )
        self.session.add(permit)
        self.session.commit()

        return permit

    def disapprove_pm_user(self, user_id: int, approved_user_id: int):
        """Remove user from PM approval."""
        self.session.query(PMPermit).filter_by(
            user_id=user_id,
            approved_user_id=approved_user_id
        ).delete()
        self.session.commit()

    def is_pm_approved(self, user_id: int, check_user_id: int) -> bool:
        """Check if user is approved for PM."""
        return self.session.query(PMPermit).filter_by(
            user_id=user_id,
            approved_user_id=check_user_id
        ).first() is not None

    def add_payment_info(self, user_id: int, payment_type: str, payment_number: str,
                        payment_name: str, qr_code_path: str = None):
        """Add payment information."""
        payment = PaymentInfo(
            user_id=user_id,
            payment_type=payment_type,
            payment_number=payment_number,
            payment_name=payment_name,
            qr_code_path=qr_code_path
        )
        self.session.add(payment)
        self.session.commit()

        return payment

    def get_payment_info(self, user_id: int):
        """Get all payment information."""
        return self.session.query(PaymentInfo).filter_by(
            user_id=user_id,
            is_active=True
        ).all()

    def add_log(self, user_id: int, command: str, arguments: str = None,
                chat_id: int = None, success: bool = True, error_message: str = None):
        """Add command execution log."""
        log = Logs(
            user_id=user_id,
            command=command,
            arguments=arguments,
            chat_id=chat_id,
            success=success,
            error_message=error_message
        )
        self.session.add(log)
        self.session.commit()

        return log

    def get_logs(self, user_id: int, limit: int = 100):
        """Get command logs."""
        return self.session.query(Logs).filter_by(
            user_id=user_id
        ).order_by(Logs.executed_at.desc()).limit(limit).all()

    def add_blacklist_group(self, user_id: int, group_id: int, group_name: str = None):
        """Add group to blacklist."""
        # Check if already blacklisted
        existing = self.session.query(BlacklistGroup).filter_by(
            user_id=user_id,
            group_id=group_id
        ).first()

        if existing:
            return existing

        blacklist = BlacklistGroup(
            user_id=user_id,
            group_id=group_id,
            group_name=group_name
        )
        self.session.add(blacklist)
        self.session.commit()

        return blacklist

    def remove_blacklist_group(self, user_id: int, group_id: int):
        """Remove group from blacklist."""
        self.session.query(BlacklistGroup).filter_by(
            user_id=user_id,
            group_id=group_id
        ).delete()
        self.session.commit()

    def get_blacklist_groups(self, user_id: int):
        """Get all blacklisted groups."""
        return self.session.query(BlacklistGroup).filter_by(user_id=user_id).all()

    def is_group_blacklisted(self, user_id: int, group_id: int) -> bool:
        """Check if group is blacklisted."""
        return self.session.query(BlacklistGroup).filter_by(
            user_id=user_id,
            group_id=group_id
        ).first() is not None

    def add_lock_user(self, user_id: int, locked_user_id: int,
                     locked_username: str = None, group_id: int = None):
        """Add user to lock list (shadow clear)."""
        # Check if already locked
        existing = self.session.query(LockUser).filter_by(
            user_id=user_id,
            locked_user_id=locked_user_id,
            group_id=group_id
        ).first()

        if existing:
            return existing

        lock = LockUser(
            user_id=user_id,
            locked_user_id=locked_user_id,
            locked_username=locked_username,
            group_id=group_id
        )
        self.session.add(lock)
        self.session.commit()

        return lock

    def remove_lock_user(self, user_id: int, locked_user_id: int, group_id: int = None):
        """Remove user from lock list."""
        query = self.session.query(LockUser).filter_by(
            user_id=user_id,
            locked_user_id=locked_user_id
        )

        if group_id:
            query = query.filter_by(group_id=group_id)

        query.delete()
        self.session.commit()

    def is_user_locked(self, user_id: int, check_user_id: int, group_id: int = None) -> bool:
        """Check if user is locked."""
        query = self.session.query(LockUser).filter_by(
            user_id=user_id,
            locked_user_id=check_user_id
        )

        if group_id:
            query = query.filter_by(group_id=group_id)

        return query.first() is not None

    def close(self):
        """Close database connection."""
        self.session.close()

# ============================================================================
# MULTI-USER DATABASE MANAGER
# ============================================================================

class MultiUserDatabaseManager:
    """Manage databases for multiple users."""

    def __init__(self, base_dir: str):
        """Initialize multi-user database manager."""
        self.base_dir = base_dir
        self.managers = {}

        os.makedirs(base_dir, exist_ok=True)

    def get_manager(self, user_id: int) -> DatabaseManager:
        """Get database manager for user."""
        if user_id not in self.managers:
            # Create user directory
            user_dir = os.path.join(self.base_dir, f"user_{user_id}")
            os.makedirs(user_dir, exist_ok=True)

            # Create database
            db_path = os.path.join(user_dir, "client.db")
            self.managers[user_id] = DatabaseManager(db_path)

        return self.managers[user_id]

    def close_all(self):
        """Close all database connections."""
        for manager in self.managers.values():
            manager.close()

        self.managers.clear()

print("✅ Database Models Loaded")
