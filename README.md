# VZ ASSISTANT v0.0.0.69

**Telegram Userbot with Multi-Tier Architecture**

```
   Vz ASSISTANT



Founder         : Vzoel Fox's
Owner            : Multi-User Support
Versi              : 0.0.0.69
Telethon × Python 3+

~Vzoel Fox's Lutpan
```

---

## 🎯 Features

- ✅ **Dual-Tier System**: Developer & Sudoers hierarchy
- ✅ **Multi-User Database**: Individual database per user
- ✅ **Customizable Prefix**: Per-user command prefix
- ✅ **Premium Emoji Support**: 17 premium emojis mapped
- ✅ **Session Management**: String-based session storage
- ✅ **Plugin System**: Modular command plugins
- ✅ **Automatic Logging**: Command and error tracking

---

## 📋 Requirements

- Python 3.9+
- Telegram Account
- API ID & Hash (from my.telegram.org)

---

## 🚀 Quick Start

### 1. Clone & Setup

```bash
cd vbot
pip install -r requirements.txt
```

### 2. Generate Session String

```bash
python3 stringgenerator.py
```

Follow the prompts to:
- Enter your phone number
- Enter the OTP code
- Copy the generated session string

### 3. Configure Environment

```bash
cp .env.example .env
nano .env  # Edit and add your SESSION_STRING
```

### 4. Run

```bash
./start.sh
```

Or manually:
```bash
python3 main.py
```

---

## 📁 Project Structure

```
vbot/
├── main.py                    # Main entry point
├── client.py                  # Telethon client manager
├── config.py                  # Configuration (API ID, Hash, Developer IDs)
├── stringgenerator.py         # Session string generator
├── requirements.txt           # Python dependencies
├── start.sh                   # Quick start script
├── emojiprime.json           # Premium emoji mapping (17 emojis)
├── ROADMAP.md                # Full project roadmap
│
├── database/
│   ├── __init__.py
│   ├── models.py             # SQLAlchemy models
│   ├── developer/            # Developer database
│   ├── shared/               # Shared resources
│   └── sudoers/              # Per-user databases
│       ├── user_123456789/
│       │   ├── client.db
│       │   ├── lockglobal.json
│       │   └── blgc.json
│       └── user_987654321/
│
├── plugins/                   # Command plugins
│   ├── __init__.py
│   └── ping.py               # Example: Ping command
│
├── utils/                     # Utility functions
├── helpers/                   # Helper modules
└── sessions/                  # Session files (gitignored)
```

---

## ⚙️ Configuration

### config.py

Already configured with:
- **API ID**: 29919905
- **API Hash**: 717957f0e3ae20a7db004d08b66bfd30
- **Developer IDs**: 8024282347, 7553981355

### Emoji Premium Mapping

17 premium emojis ready in `emojiprime.json`:
- 🤩 MAIN_VZOEL
- 👨‍💻 DEVELOPER
- 🌟 OWNER
- ⚙️ GEAR
- ✅ CHECKLIST
- ⛈ PETIR
- 👍 HIJAU (1-150ms)
- ⚠️ KUNING (151-200ms)
- 👎 MERAH (200+ms)
- ✉️ TELEGRAM
- 📷 CAMERA
- 😈 PROSES_1
- 🔪 PROSES_2
- 😐 PROSES_3
- 👨‍🚀 ROBOT
- ♾ LOADING
- 🎚 NYALA

---

## 🎮 Available Commands

### Current Plugins:

#### Ping (ping.py)
- `.ping` - Show latency, uptime, owner, founder
- `.pink` - Show latency with color emoji (auto-triggers .limit)
- `.pong` - Show uptime (auto-triggers .alive)

**More plugins coming soon!** (See ROADMAP.md)

---

## 👨‍💻 For Developers

### Creating a Plugin

Create a new file in `plugins/` directory:

```python
"""
VZ ASSISTANT v0.0.0.69
Your Plugin Name

2025© Vzoel Fox's Lutpan
Founder & DEVELOPER : @VZLfxs
"""

from telethon import events
import config

@events.register(events.NewMessage(pattern=r'^\.yourcommand$', outgoing=True))
async def your_command_handler(event):
    """
    .yourcommand - Description
    """
    # Your code here
    await event.edit("Response text")

print("✅ Plugin loaded: yourplugin.py")
```

### Database Access

```python
from database.models import DatabaseManager
import config

# Get user database
db = DatabaseManager(config.get_sudoer_db_path(user_id))

# Add user
db.add_user(user_id=123456, username="example")

# Update prefix
db.update_prefix(user_id=123456, prefix="!")

# Add log
db.add_log(user_id=123456, command="test", success=True)
```

### Premium Emoji Usage

```python
import config

# Load emoji mapping
emoji_map = config.load_emoji_mapping()

# Get premium emoji ID
emoji_id = config.get_premium_emoji_id("👍")
```

---

## 🗺️ Development Roadmap

See [ROADMAP.md](ROADMAP.md) for complete development plan:

- **Phase 1**: Core Foundation ✅ COMPLETED
- **Phase 2**: Command Framework (In Progress)
- **Phase 3**: Sudoers Commands (Planned)
- **Phase 4**: Developer Commands (Planned)
- **Phase 5**: Animation & UI (Planned)
- **Phase 6**: Deploy Bot (Planned)
- **Phase 7**: Testing & Polish (Planned)

Total: **27 commands** planned (14 sudoers + 7 developer + 6 utilities)

---

## 🔧 Troubleshooting

### Issue: "No SESSION_STRING found"
**Solution**: Run `python3 stringgenerator.py` and add the generated string to `.env`

### Issue: "Python 3.9+ is required"
**Solution**: Upgrade Python:
```bash
# Termux
pkg install python

# Ubuntu/Debian
sudo apt install python3.11
```

### Issue: "Module not found"
**Solution**: Install dependencies:
```bash
pip install -r requirements.txt
```

---

## 📝 Notes

- ⚠️ **Branding**: Never modify branding text
- ⚠️ **Version**: Always locked at 0.0.0.69
- ⚠️ **Security**: Keep your SESSION_STRING private
- ⚠️ **Developer IDs**: Configured in config.py

---

## 📞 Support

**Founder & Developer:** @VZLfxs

---

**2025© Vzoel Fox's Lutpan**
**Vz ASSISTANT v0.0.0.69**
