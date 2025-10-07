# VZ Deployer Bot

Multi-user deployment manager with `..ok` approval system for VZ Assistant.

## Features

- 🤖 User request via chat → forward to developer
- ✅ Developer approve dengan command `..ok` di userbot
- 🔐 Git clone per user (no session tabrakan)
- 📁 Separate directory per user: `deployments/<user_id>/`
- 📊 PM2 management per user: `vbot_<user_id>`
- 🔒 Secure session storage
- 🚫 Anti-spam protection
- ⚡ Auto-start with main.py (integrated)

## Setup

### 1. Install Dependencies

```bash
pip install pyrogram tgcrypto
npm install -g pm2  # If not installed
```

### 2. Start Bot

Deployer bot auto-starts dengan main.py:

```bash
python3 main.py
# atau
./start.sh
```

**Tidak perlu start terpisah!** Deployer bot jalan bareng main.py tanpa tabrakan.

## Commands

### For Users (After approved):

- `/start` - Show welcome message
- `/setsession <session_string>` - Set your session string
- `/deploy` - Deploy your vbot
- `/mystatus` - Check deployment status

### For Developers (Userbot):

- `..ok` - Approve user (reply di PM bot deployer)
- `..no` - Disapprove user (remove from approved list)
- `.approvedlist` - List all approved users
- `.deploystatus` - Check deployer bot status

### For Developers (Bot):

- `/deploylist` - List all active deployments
- `/deploystop <user_id>` - Stop deployment for user

## Usage Flow

### For Users:

1. **Request Access**
   - Chat deployer bot (any message)
   - Bot will forward to developer
   - Wait for approval

2. **After Approved - Set Session**
   ```
   /setsession 1BVtsOK4Bu...
   ```
   - Use a **different account** from your owner account
   - Get session from string generator
   - Message will auto-delete for security

3. **Deploy**
   ```
   /deploy
   ```
   - Bot auto-creates env and starts PM2
   - Get deployment info (port, PID)

4. **Check Status**
   ```
   /mystatus
   ```
   - Shows deployment status (port, PID, uptime)

### For Developers:

1. **Approve User**
   - Receive forwarded message di userbot PM
   - Reply `..ok` pada pesan bot deployer
   - User instantly approved

2. **Manage Approvals**
   ```
   ..no              # Disapprove user (reply)
   .approvedlist     # List approved users
   .deploystatus     # Check bot status
   ```

3. **Manage Deployments**
   ```
   /deploylist          # View all active (di bot)
   /deploystop 123456   # Stop specific user (di bot)
   ```

## Configuration

Edit `deployer_bot.py`:

```python
BOT_TOKEN = "your_bot_token"
DEVELOPER_IDS = [123456, 789012]  # Can approve
SUDOER_IDS = [345678]             # Can request
```

## Data Storage

- `data/deployments.json` - Active/history deployments
- `data/deploy_sessions.json` - User session strings
- `data/approved_users.json` - Approved user IDs (via ..ok)
- `deployments/<user_id>/` - Git clone per user (isolated)

## Directory Structure

```
vbot/
├── main.py                    # Main bot (includes deployer)
├── helpers/
│   └── deployer_manager.py    # Deployer bot module
├── plugins/
│   └── deploy_approve.py      # ..ok approval plugin
├── data/
│   ├── deployments.json       # Active deployments
│   ├── deploy_sessions.json   # User sessions
│   └── approved_users.json    # Approved users
└── deployments/
    ├── 123456/                # User 123456's vbot clone
    │   ├── main.py
    │   ├── .env               # User's env
    │   └── ... (full vbot)
    └── 789012/                # User 789012's vbot clone
        ├── main.py
        ├── .env
        └── ... (full vbot)
```

## PM2 Management

Each deployment runs as `vbot_<user_id>`:

```bash
pm2 list                    # List all
pm2 logs vbot_123456       # View logs
pm2 restart vbot_123456    # Restart
pm2 stop vbot_123456       # Stop
```

## Security Notes

⚠️ **IMPORTANT:**

- Session strings = full account access
- Store `deploy_sessions.json` securely
- Use different accounts for each deployment
- Never share session strings
- Recommend encrypting session storage

## Troubleshooting

### Bot not responding:
```bash
pm2 restart vz_deployer_bot
pm2 logs vz_deployer_bot
```

### Deployment failed:
- Check user session is valid
- Verify PM2 is installed
- Check port availability
- Review logs: `pm2 logs vbot_<user_id>`

### Session not found:
User needs to set session first:
```
/setsession <string>
```

## Support

Developer: @VZLfxs
Bot: VZ Assistant v0.0.0.69

---

2025© Vzoel Fox's Lutpan
