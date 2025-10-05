# PM2 Multi-User Setup Guide
## VZ ASSISTANT v0.0.0.69

### Overview
VZ Assistant uses **PM2** for managing multiple sudoer instances. Each user runs as an isolated PM2 process with their own session.

---

## Prerequisites

### 1. Install Node.js & PM2
```bash
# Termux
pkg install nodejs
npm install -g pm2

# Ubuntu/Debian
apt install nodejs npm
npm install -g pm2
```

### 2. Verify Installation
```bash
pm2 --version
node --version
```

---

## Architecture

```
PM2 Process Manager
├── vz-deploybot (Deploy Bot)
├── vz-sudoer-123456789 (User 1)
├── vz-sudoer-987654321 (User 2)
└── vz-sudoer-555555555 (User 3)
```

**Each process:**
- ✅ Isolated session string
- ✅ Auto-restart on crash
- ✅ Dedicated logs
- ✅ Independent database
- ✅ Custom prefix support

---

## Deployment Flow

### Automatic (via Deploy Bot)
1. User requests access → Developer approves
2. User sends phone number → OTP sent
3. User sends OTP code → Session generated
4. **🚀 AUTO**: PM2 process created & started
5. ✅ VZ Assistant running for that user

### Manual Start
```bash
# Start specific sudoer
python run_sudoer.py <user_id>

# Or with PM2
pm2 start run_sudoer.py --name vz-sudoer-<user_id> --interpreter python3 -- <user_id>
```

---

## PM2 Commands

### Process Management
```bash
# List all processes
pm2 list

# View logs
pm2 logs vz-sudoer-123456789

# Stop process
pm2 stop vz-sudoer-123456789

# Restart process
pm2 restart vz-sudoer-123456789

# Delete process
pm2 delete vz-sudoer-123456789

# Restart all sudoers
pm2 restart all
```

### Monitoring
```bash
# Monitor all processes
pm2 monit

# Show process details
pm2 describe vz-sudoer-123456789

# View process info
pm2 info vz-sudoer-123456789
```

### Logs
```bash
# View logs for specific user
pm2 logs vz-sudoer-123456789

# View all logs
pm2 logs

# Clear logs
pm2 flush

# View error logs only
pm2 logs vz-sudoer-123456789 --err
```

---

## Configuration

### ecosystem.config.js
PM2 ecosystem file for multi-user management:

```javascript
module.exports = {
  apps: [
    {
      name: 'vz-deploybot',
      script: 'deploybot.py',
      interpreter: 'python3',
      autorestart: true,
      max_memory_restart: '500M'
    },
    {
      name: 'vz-sudoer-123456789',
      script: 'run_sudoer.py',
      interpreter: 'python3',
      args: '123456789',
      autorestart: true,
      max_memory_restart: '500M',
      env: {
        USER_ID: '123456789',
        SESSION_STRING: 'your_session_string_here'
      }
    }
  ]
};
```

### Start from ecosystem
```bash
pm2 start ecosystem.config.js
```

---

## Auto-Startup (Optional)

### Enable PM2 on system boot
```bash
# Generate startup script
pm2 startup

# Save current process list
pm2 save

# Disable startup
pm2 unstartup
```

---

## Troubleshooting

### Process won't start
```bash
# Check PM2 logs
pm2 logs vz-sudoer-<user_id> --lines 50

# Try manual start
python run_sudoer.py <user_id>

# Check session string
cat sessions/sudoer_sessions.json
```

### High memory usage
```bash
# Set memory limit
pm2 start run_sudoer.py --name vz-sudoer-<user_id> --max-memory-restart 300M

# Monitor memory
pm2 monit
```

### Process keeps restarting
```bash
# Check error logs
pm2 logs vz-sudoer-<user_id> --err

# View restart count
pm2 list
```

---

## File Structure

```
vbot/
├── deploybot.py              # Deploy bot with PM2 integration
├── run_sudoer.py             # Individual sudoer runner
├── ecosystem.config.js       # PM2 configuration
├── helpers/
│   └── pm2_manager.py        # PM2 process manager
├── sessions/
│   └── sudoer_sessions.json  # Session storage
└── logs/                     # PM2 logs directory
```

---

## Performance Tips

1. **Memory Limits**: Set appropriate memory limits for auto-restart
2. **Log Rotation**: Use `pm2 install pm2-logrotate` for log management
3. **Monitoring**: Use `pm2 monit` to track resource usage
4. **Clustering**: PM2 can run multiple instances if needed

---

## Security Notes

- ✅ Session strings stored in environment variables
- ✅ Each process runs with isolated credentials
- ✅ Logs separated per user
- ⚠️  Protect `sessions/sudoer_sessions.json`
- ⚠️  Don't commit ecosystem.config.js with sessions

---

## Developer Commands

### via Deploy Bot
```
/approve <user_id>  - Approve deploy access
/reject <user_id>   - Reject request
/pending            - View pending requests
/approved           - View approved users
```

### Direct PM2
```bash
# Start deploy bot
pm2 start deploybot.py --name vz-deploybot --interpreter python3

# Add new sudoer manually
pm2 start run_sudoer.py --name vz-sudoer-<id> --interpreter python3 -- <id>
```

---

## 🚀 Quick Start

```bash
# 1. Install PM2
npm install -g pm2

# 2. Start deploy bot
pm2 start deploybot.py --name vz-deploybot --interpreter python3

# 3. Users deploy via bot
# Bot will automatically create PM2 processes

# 4. Monitor
pm2 list
pm2 monit
```

---

2025© Vzoel Fox's Lutpan
Founder & DEVELOPER : @VZLfxs
