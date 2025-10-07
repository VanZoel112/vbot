# VZ Deployer Bot

Multi-user deployment manager with approval system for VZ Assistant.

## Features

- 🤖 User request deployment via `/deploy`
- ✅ Developer approve/reject with inline buttons
- 🔐 Auto-generate `.env` for each user
- 📊 PM2 management for each deployment
- 🔒 Secure session storage

## Setup

### 1. Install Dependencies

```bash
pip install pyrogram tgcrypto
npm install -g pm2  # If not installed
```

### 2. Start Deployer Bot

```bash
chmod +x start_deployer.sh
./start_deployer.sh
```

Or manually:

```bash
python3 deployer_bot.py
```

## User Commands

### For Sudoers (Users who can request deployment):

- `/start` - Show welcome message
- `/setsession <session_string>` - Set your session string
- `/deploy` - Request deployment
- `/mystatus` - Check deployment status

### For Developers:

- `/deploylist` - List all active deployments
- `/deploystop <user_id>` - Stop deployment for user
- `/pending` - View pending deployment requests

## Usage Flow

### For Users:

1. **Set Session String**
   ```
   /setsession 1BVtsOK4Bu...
   ```
   - Use a **different account** from your owner account
   - Get session from string generator
   - Message will auto-delete for security

2. **Request Deployment**
   ```
   /deploy
   ```
   - Sends request to developers
   - Wait for approval notification

3. **Check Status**
   ```
   /mystatus
   ```
   - Shows deployment status (pending/active/none)

### For Developers:

1. **Approve Request**
   - Receive notification with inline buttons
   - Click "✅ Approve" to deploy
   - Bot auto-creates env and starts PM2

2. **Manage Deployments**
   ```
   /deploylist          # View all active
   /deploystop 123456   # Stop specific user
   /pending             # View pending requests
   ```

## Configuration

Edit `deployer_bot.py`:

```python
BOT_TOKEN = "your_bot_token"
DEVELOPER_IDS = [123456, 789012]  # Can approve
SUDOER_IDS = [345678]             # Can request
```

## Data Storage

- `data/deployments.json` - Active/pending/history
- `data/deploy_sessions.json` - User session strings (encrypted recommended)
- `deployments/<user_id>/` - User deployment directories

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
