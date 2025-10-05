# VZ ASSISTANT BOT - Quick Start Guide

## Overview
Assistant bot menggunakan **Pyrogram + Trio** untuk menangani inline keyboards yang tidak bisa dilakukan userbot.

### Architecture
- **Userbot**: Telethon + uvloop (fast execution)
- **Assistant Bot**: Pyrogram + Trio (robust inline keyboards)
- **Separation**: Event loops terpisah untuk stabilitas optimal

## Installation

### 1. Install Dependencies
```bash
pip3 install -r requirements_assistant.txt
```

### 2. Configure Environment
Update `.env` dengan token assistant bot:
```env
ASSISTANT_BOT_TOKEN=8314911312:AAEZTrlru95_QNycAt4TlYH_k-7q2f_PQ9c
OWNER_ID=7553981355
ASSISTANT_BOT_USERNAME=VzAssistantBot
```

### 3. Run Assistant Bot
```bash
# Method 1: Direct run
python3 assistant_bot_pyrogram.py

# Method 2: PM2 (recommended for AWS)
pm2 start assistant_bot_pyrogram.py --name vz-assistant --interpreter python3

# Method 3: Screen (alternative)
screen -dmS assistant python3 assistant_bot_pyrogram.py
```

## Features

### Available Commands
- `/start` - Welcome message
- `/help` - Interactive help menu dengan inline categories
- `/alive` - Bot status dengan inline buttons
- `/ping` - Check latency

### Inline Keyboard Categories
- 📋 Basic Commands
- 👨‍💼 Admin
- 📡 Broadcast
- 👥 Group
- ℹ️ Info
- ⚙️ Settings
- 🔧 Plugins

### Authorization
- Owner: `7553981355`
- Developers: `[8024282347, 7553981355]`

## Testing

### Test Inline Keyboards
1. Start bot: `python3 assistant_bot_pyrogram.py`
2. Open Telegram dan chat dengan bot
3. Kirim `/help` *(atau jalankan `.help` di userbot untuk membuka inline browser)*
4. Click category buttons untuk navigate
5. Test `/alive` untuk debug

### Debug Commands
Bot ini dibuat khusus untuk debug:
- `.help` - inline help menu (dipicu dari userbot & bot)
- `.alive` - debug alive message
- `.joinvc` - debug voice chat

## PM2 Management

### Start
```bash
pm2 start assistant_bot_pyrogram.py --name vz-assistant --interpreter python3
```

### Monitor
```bash
pm2 logs vz-assistant
pm2 monit
```

### Restart
```bash
pm2 restart vz-assistant
```

### Stop
```bash
pm2 stop vz-assistant
pm2 delete vz-assistant
```

## Troubleshooting

### Bot tidak respond
- Check token di `.env`
- Verify owner ID benar
- Check logs: `pm2 logs vz-assistant`

### Inline buttons tidak muncul
- Bot harus bot account (bukan user account)
- Verify authorization (owner/developer ID)

### Event loop conflict
- Jangan run di folder yang sama dengan userbot jika ada conflict
- Trio dan uvloop terpisah secara design

## Integration with Userbot

### Bridge Communication (Future)
File bridge: `data/bot_bridge.json`
- Userbot writes commands
- Assistant bot executes dengan inline
- Result sync kembali ke userbot

## Notes
- Bot ini **TIDAK** menggantikan userbot
- Bot ini **MELENGKAPI** userbot dengan inline keyboard capability
- Event loop terpisah: Trio (assistant) vs uvloop (userbot)
- Logging robust untuk debugging

---
🤖 by VzBot | @VZLfxs
