"""
VZ ASSISTANT v0.0.0.69
Logging System - Local File Logger

2025© Vzoel Fox's Lutpan
Founder & DEVELOPER : @VZLfxs
"""

import logging
import os
from datetime import datetime
import traceback
import sys

# ============================================================================
# LOGGER CONFIGURATION
# ============================================================================

class VZLogger:
    """Enhanced logger for VZ ASSISTANT."""

    def __init__(self, name: str = "VZ_ASSISTANT"):
        """Initialize logger."""
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        # Create logs directory
        self.log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
        os.makedirs(self.log_dir, exist_ok=True)

        # Setup handlers
        self._setup_handlers()

    def _setup_handlers(self):
        """Setup file and console handlers."""
        # Remove existing handlers
        self.logger.handlers.clear()

        # File handler - All logs
        log_file = os.path.join(self.log_dir, f"vbot_{datetime.now().strftime('%Y%m%d')}.log")
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)

        # Error file handler - Only errors
        error_file = os.path.join(self.log_dir, f"error_{datetime.now().strftime('%Y%m%d')}.log")
        error_handler = logging.FileHandler(error_file, encoding='utf-8')
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)
        self.logger.addHandler(error_handler)

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(levelname)-8s | %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

        # Command log file
        self.cmd_log = os.path.join(self.log_dir, f"commands_{datetime.now().strftime('%Y%m%d')}.log")

    def debug(self, message: str):
        """Log debug message."""
        self.logger.debug(message)

    def info(self, message: str):
        """Log info message."""
        self.logger.info(message)

    def warning(self, message: str):
        """Log warning message."""
        self.logger.warning(message)

    def error(self, message: str, exc_info=None):
        """Log error message."""
        if exc_info:
            self.logger.error(message, exc_info=True)
        else:
            self.logger.error(message)

    def critical(self, message: str, exc_info=None):
        """Log critical message."""
        if exc_info:
            self.logger.critical(message, exc_info=True)
        else:
            self.logger.critical(message)

    def log_command(self, user_id: int, username: str, chat_id: int,
                    chat_name: str, command: str, success: bool = True, error: str = None):
        """Log command execution."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        status = "SUCCESS" if success else "FAILED"

        log_line = f"{timestamp} | {status:8s} | User: {username} ({user_id}) | Chat: {chat_name} ({chat_id}) | Command: {command}"

        if error:
            log_line += f" | Error: {error}"

        # Write to command log
        try:
            with open(self.cmd_log, 'a', encoding='utf-8') as f:
                f.write(log_line + '\n')
        except Exception as e:
            self.error(f"Failed to write command log: {e}")

        # Also log to main logger
        if success:
            self.info(f"Command executed: {command} by {username}")
        else:
            self.error(f"Command failed: {command} by {username} - {error}")

    def log_event(self, event_type: str, message: str, details: dict = None):
        """Log event with details."""
        log_msg = f"EVENT[{event_type}]: {message}"
        if details:
            log_msg += f" | Details: {details}"
        self.info(log_msg)

    def log_exception(self, context: str = ""):
        """Log exception with full traceback."""
        exc_type, exc_value, exc_traceback = sys.exc_info()
        if exc_type:
            tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            tb_text = ''.join(tb_lines)
            self.error(f"Exception in {context}:\n{tb_text}")

    def get_log_path(self) -> str:
        """Get current log file path."""
        return os.path.join(self.log_dir, f"vbot_{datetime.now().strftime('%Y%m%d')}.log")

    def get_error_log_path(self) -> str:
        """Get current error log file path."""
        return os.path.join(self.log_dir, f"error_{datetime.now().strftime('%Y%m%d')}.log")

    def get_command_log_path(self) -> str:
        """Get current command log file path."""
        return self.cmd_log


# ============================================================================
# GLOBAL LOGGER INSTANCE
# ============================================================================

# Create global logger instance
logger = VZLogger("VZ_ASSISTANT")

# Convenience functions
def debug(msg):
    logger.debug(msg)

def info(msg):
    logger.info(msg)

def warning(msg):
    logger.warning(msg)

def error(msg, exc_info=None):
    logger.error(msg, exc_info)

def critical(msg, exc_info=None):
    logger.critical(msg, exc_info)

def log_command(user_id, username, chat_id, chat_name, command, success=True, error=None):
    logger.log_command(user_id, username, chat_id, chat_name, command, success, error)

def log_event(event_type, message, details=None):
    logger.log_event(event_type, message, details)

def log_exception(context=""):
    logger.log_exception(context)

print(f"✅ VZ Logger Loaded - Logs: {logger.log_dir}")
