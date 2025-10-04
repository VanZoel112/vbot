"""
VZ ASSISTANT v0.0.0.69
Configuration File

2025© Vzoel Fox's Lutpan
Founder & DEVELOPER : @VZLfxs
"""

import os
import json
from typing import List, Dict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============================================================================
# TELEGRAM API CREDENTIALS
# ============================================================================
API_ID = 29919905
API_HASH = "717957f0e3ae20a7db004d08b66bfd30"

# ============================================================================
# DEVELOPER IDS (Full Access)
# ============================================================================
DEVELOPER_IDS = [
    8024282347,  # Main Developer
    7553981355   # Secondary Developer
]

# ============================================================================
# BOT CONFIGURATION
# ============================================================================
BOT_VERSION = "0.0.0.69"
BOT_NAME = "Vz ASSISTANT"
FOUNDER_USERNAME = "@VZLfxs"
FOUNDER_LINK = "t.me/VZLfxs"
BRANDING_FOOTER = "2025© Vzoel Fox's Lutpan"

# ============================================================================
# VZL2-STYLE RESPONSE FOOTERS
# ============================================================================
RESULT_FOOTER = "𝚁𝚎𝚜𝚞𝚕𝚝 𝚋𝚢 𝚅𝚣𝚘𝚎𝚕 𝙵𝚘𝚡'𝚜 𝙰𝚜𝚜𝚒𝚜𝚝𝚊𝚗𝚝"
COPYRIGHT_FOOTER = "©𝟸0𝟸𝟻 𝚋𝚢 𝚅𝚣𝚘𝚎𝚕 𝙵𝚘𝚡'𝚜 𝙻𝚞𝚝𝚙𝚊𝚗"
FOUNDER_TEXT = "𝐹𝑜𝑢𝑛𝑑𝑒𝑟 : 𝑉𝑧𝑜𝑒𝑙 𝐹𝑜𝑥'𝑠"

# ============================================================================
# PREFIX CONFIGURATION
# ============================================================================
DEFAULT_PREFIX = "."
ALLOWED_PREFIXES = [".", "+", "#", "@", ":", "?", ""]  # "" means no prefix

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_DIR = os.path.join(BASE_DIR, "database")

# Developer database
DEVELOPER_DB_PATH = os.path.join(DATABASE_DIR, "developer", "main.db")
DEVELOPER_LOGS_DB_PATH = os.path.join(DATABASE_DIR, "developer", "logs.db")

# Shared database
SHARED_DIR = os.path.join(DATABASE_DIR, "shared")
EMOJI_PRIME_JSON = os.path.join(BASE_DIR, "emojiprime.json")

# Sudoers database directory
SUDOERS_DB_DIR = os.path.join(DATABASE_DIR, "sudoers")

# ============================================================================
# SESSION CONFIGURATION
# ============================================================================
SESSION_DIR = os.path.join(BASE_DIR, "sessions")
os.makedirs(SESSION_DIR, exist_ok=True)

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================
# Load from environment
LOG_GROUP_ID = os.getenv("LOG_GROUP_ID")
if LOG_GROUP_ID:
    try:
        LOG_GROUP_ID = int(LOG_GROUP_ID)
    except ValueError:
        LOG_GROUP_ID = None

LOG_LEVEL = "INFO"

# ============================================================================
# PM PERMIT CONFIGURATION
# ============================================================================
DEFAULT_PM_PERMIT_MESSAGE = f"""
**{BOT_NAME}**

Halo! Ini adalah akun pribadi yang dilindungi oleh PM Permit.

Silakan tunggu hingga owner menyetujui pesan Anda.
Jangan spam atau Anda akan diblokir otomatis.

{BRANDING_FOOTER}
Founder & DEVELOPER : {FOUNDER_USERNAME}
"""

# ============================================================================
# ALIVE TEMPLATE
# ============================================================================
ALIVE_TEMPLATE = """
   **Vz ASSISTANT**



**Founder**         : Vzoel Fox's/{FOUNDER_LINK}
**Owner**            : @{{owner_username}}
**Versi**              : {BOT_VERSION}
**Telethon × Python 3+**
**Total Plugin**  : {{plugin_count}}
**Waktu Nyala** : {{uptime}}

~Vzoel Fox's Lutpan
"""

# ============================================================================
# ANIMATION SETTINGS
# ============================================================================
# Updated to match vzl2 pattern with descriptive phases
ANIMATION_DELAY = 2.5  # seconds for descriptive animation phases (vzl2 style)
TAG_ANIMATION_DELAY = 2.5  # seconds for tag command
PROCESS_STEPS = 12  # Number of process animation steps (vzl2 uses 12)
TAG_USERS_PER_EDIT = 10  # Number of users to tag per edit
FAST_ANIMATION_DELAY = 0.2  # seconds for fast/error animations

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_sudoer_db_path(user_id: int) -> str:
    """Get database path for a specific sudoer."""
    user_dir = os.path.join(SUDOERS_DB_DIR, f"user_{user_id}")
    os.makedirs(user_dir, exist_ok=True)
    return os.path.join(user_dir, "client.db")

def get_sudoer_json_path(user_id: int, json_name: str) -> str:
    """Get JSON file path for a specific sudoer."""
    user_dir = os.path.join(SUDOERS_DB_DIR, f"user_{user_id}")
    os.makedirs(user_dir, exist_ok=True)
    return os.path.join(user_dir, json_name)

def is_developer(user_id: int) -> bool:
    """Check if user is a developer."""
    return user_id in DEVELOPER_IDS

def load_emoji_mapping() -> Dict:
    """Load emoji premium mapping from JSON."""
    try:
        with open(EMOJI_PRIME_JSON, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# ============================================================================
# GCAST BLACKLIST MANAGEMENT
# ============================================================================

def add_to_gcast_blacklist(chat_id: int) -> bool:
    """Add chat ID to gcast blacklist."""
    global GCAST_BLACKLIST
    if chat_id not in GCAST_BLACKLIST:
        GCAST_BLACKLIST.append(chat_id)
        save_gcast_blacklist()
        return True
    return False

def remove_from_gcast_blacklist(chat_id: int) -> bool:
    """Remove chat ID from gcast blacklist."""
    global GCAST_BLACKLIST
    if chat_id in GCAST_BLACKLIST:
        GCAST_BLACKLIST.remove(chat_id)
        save_gcast_blacklist()
        return True
    return False

def is_gcast_blacklisted(chat_id: int) -> bool:
    """Check if chat ID is in gcast blacklist."""
    return chat_id in GCAST_BLACKLIST

def save_gcast_blacklist():
    """Save GCAST_BLACKLIST to config file."""
    try:
        config_file = os.path.join(BASE_DIR, "config.py")
        with open(config_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Find and replace GCAST_BLACKLIST line
        import re
        pattern = r'GCAST_BLACKLIST: List\[int\] = \[.*?\]'
        replacement = f'GCAST_BLACKLIST: List[int] = {GCAST_BLACKLIST}'
        content = re.sub(pattern, replacement, content)

        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(content)
    except Exception as e:
        print(f"Error saving gcast blacklist: {e}")

def load_gcast_blacklist():
    """Load GCAST_BLACKLIST from config (already loaded on import)."""
    pass  # GCAST_BLACKLIST is loaded when module imports

def get_premium_emoji_id(emoji: str) -> str:
    """Get premium emoji ID from standard emoji."""
    mapping = load_emoji_mapping()
    return mapping.get("emoji_mapping", {}).get(emoji, None)

# ============================================================================
# ENSURE DIRECTORIES EXIST
# ============================================================================
os.makedirs(DATABASE_DIR, exist_ok=True)
os.makedirs(os.path.join(DATABASE_DIR, "developer"), exist_ok=True)
os.makedirs(SHARED_DIR, exist_ok=True)
os.makedirs(SUDOERS_DB_DIR, exist_ok=True)

# ============================================================================
# DEPLOYMENT BOT
# ============================================================================
# Load from environment
DEPLOY_BOT_TOKEN = os.getenv("DEPLOY_BOT_TOKEN", None)

# ============================================================================
# BROADCAST SETTINGS
# ============================================================================
GCAST_DELAY = 0.5  # Delay between broadcasts in seconds
MAX_BROADCAST_RETRIES = 3

# Gcast Blacklist (chat IDs to skip during broadcast)
GCAST_BLACKLIST: List[int] = []

# ============================================================================
# VC SETTINGS (pytgcalls)
# ============================================================================
VC_AUTO_JOIN = True
VC_BITRATE = 48000

# ============================================================================
# PAYMENT SETTINGS
# ============================================================================
MAX_PAYMENT_INFO = 3  # Maximum number of payment info entries
PAYMENT_QR_ENABLED = True

print(f"✅ {BOT_NAME} v{BOT_VERSION} - Configuration Loaded")
print(f"📁 Database Directory: {DATABASE_DIR}")
print(f"👨‍💻 Developers: {len(DEVELOPER_IDS)} registered")
