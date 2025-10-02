# 🤖 Deploy Bot Setup Guide

**VZ ASSISTANT v0.0.0.69 - Deploy Bot Configuration**

2025© Vzoel Fox's Lutpan
Founder & DEVELOPER : @VZLfxs

---

## 📋 Overview

Deploy bot adalah Telegram bot yang membantu user untuk deploy VZ ASSISTANT secara otomatis tanpa perlu manual setup session string.

**Flow:**
```
User → @YourDeployBot → Send Phone → Enter OTP → ✅ Auto Deployed
```

---

## 🚀 Step 1: Create Bot via BotFather

### 1.1 Open BotFather

1. Buka Telegram
2. Search: **@BotFather**
3. Start conversation: `/start`

### 1.2 Create New Bot

```
/newbot
```

BotFather akan tanya:
1. **Bot name**: `VZ ASSISTANT Deploy Bot` (atau nama lain)
2. **Bot username**: `VZAssistantDeployBot` (harus unik, ends with 'bot')

### 1.3 Get Bot Token

Setelah sukses, BotFather akan kirim:
```
Done! Congratulations on your new bot.

Token: 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
```

**⚠️ SIMPAN TOKEN INI!**

---

## 🔧 Step 2: Configure Deploy Bot

### 2.1 Edit config.py

Open `config.py` dan cari baris:
```python
DEPLOY_BOT_TOKEN = None  # Set this when implementing deploy bot
```

Ubah menjadi:
```python
DEPLOY_BOT_TOKEN = "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"  # Your bot token
```

### 2.2 Save Configuration

Save file `config.py`

---

## ▶️ Step 3: Run Deploy Bot

### 3.1 Start Deploy Bot

```bash
# Method 1: Direct
python3 deploybot.py

# Method 2: Background (recommended)
nohup python3 deploybot.py > deploybot.log 2>&1 &

# Method 3: With screen/tmux
screen -S deploybot
python3 deploybot.py
# Press Ctrl+A+D to detach
```

### 3.2 Check if Running

```bash
# Check process
ps aux | grep deploybot

# Check logs (if using nohup)
tail -f deploybot.log
```

You should see:
```
╔══════════════════════════════════════════════════════════╗
║              VZ ASSISTANT v0.0.0.69                      ║
║              Deploy Bot                                  ║
║                                                          ║
║              2025© Vzoel Fox's Lutpan                    ║
║              Founder & DEVELOPER : @VZLfxs               ║
╚══════════════════════════════════════════════════════════╝

🤖 Starting Deploy Bot...

✅ Deploy Bot is running!
📱 Users can now deploy via @YourBotUsername

🔄 Bot is active... (Press Ctrl+C to stop)
```

---

## 🎯 Step 4: Test Deploy Bot

### 4.1 Find Your Bot

Open Telegram dan search bot username kamu (contoh: `@VZAssistantDeployBot`)

### 4.2 Start Deployment

1. Send: `/start`
2. Bot will reply with welcome message
3. Send your phone number: `+628123456789`
4. Bot sends OTP code to your phone
5. Enter the code: `12345`
6. ✅ Deployment complete!

---

## 🛠️ Optional: Bot Customization

### Set Bot Profile Picture

```
/setuserpic @YourBotUsername
```
Upload gambar bot

### Set Bot Description

```
/setdescription @YourBotUsername
```
Masukkan deskripsi:
```
🤖 VZ ASSISTANT Deploy Bot

Automatic deployment system for VZ ASSISTANT userbot.

📝 Commands:
/start - Begin deployment
/cancel - Cancel deployment
/status - Check deployment status

🌟 2025© Vzoel Fox's Lutpan
```

### Set Bot About

```
/setabouttext @YourBotUsername
```
Masukkan about text:
```
Official deploy bot for VZ ASSISTANT v0.0.0.69
```

### Set Bot Commands

```
/setcommands @YourBotUsername
```
Masukkan commands:
```
start - Begin deployment process
cancel - Cancel active deployment
status - Check deployment status
```

---

## 📊 Deploy Bot Features

### Automatic Features:
- ✅ Phone number validation
- ✅ OTP code verification
- ✅ Session string generation
- ✅ Database creation
- ✅ User registration as sudoer
- ✅ Auto-start userbot

### Security Features:
- ✅ State machine (prevents spam)
- ✅ 2FA support (if enabled)
- ✅ Session cleanup on error
- ✅ Developer bypass

### Commands Available:
- `/start` - Begin deployment
- `/cancel` - Cancel deployment
- `/status` - Check deployment status

---

## 🔐 Security Notes

### Bot Token Security

**⚠️ NEVER share your bot token!**

Bot token adalah seperti password untuk bot kamu.

**If leaked:**
1. Revoke token di @BotFather: `/revoke`
2. Generate new token: `/newbot` (new bot) or `/token` (existing bot)
3. Update `config.py` dengan token baru

### Session String Security

Deploy bot akan generate session string untuk user.
Session string disimpan di database per user.

**⚠️ Jangan log atau expose session strings!**

---

## 🐛 Troubleshooting

### Problem: Bot tidak response

**Solution:**
```bash
# Check if bot is running
ps aux | grep deploybot

# Check logs
tail -f deploybot.log

# Restart bot
pkill -f deploybot.py
python3 deploybot.py
```

### Problem: "Invalid phone number"

**Solution:**
- Phone harus dengan country code: `+628123456789`
- Jangan gunakan spasi atau karakter lain

### Problem: "Phone code invalid"

**Solution:**
- Pastikan kode OTP benar (5 digit)
- Kode OTP expired setelah beberapa menit
- Request code baru dengan `/cancel` lalu `/start` lagi

### Problem: "2FA password required"

**Solution:**
- User punya 2FA enabled
- Masukkan 2FA password setelah diminta
- TODO: Implement 2FA handler (currently shows info)

### Problem: Bot token invalid

**Solution:**
```bash
# Check token in config.py
grep DEPLOY_BOT_TOKEN config.py

# Test token
curl https://api.telegram.org/bot<TOKEN>/getMe

# If invalid, get new token from @BotFather
```

---

## 📝 Usage Example

### For New Users:

```
User: /start
Bot: 🤖 VZ ASSISTANT - Deploy Bot
     Welcome! Send your phone number to start.

User: +628123456789
Bot: 📱 Sending code to +628123456789...
     ✅ Code sent! Enter the code:

User: 12345
Bot: 🔄 Verifying code...
     ✅ Deployment Successful!

     👤 Account Information:
     ├ Name: John Doe
     ├ Username: @johndoe
     ├ User ID: 123456789
     └ Role: Sudoer

     Your VZ ASSISTANT is now running!
```

---

## 🚦 Production Deployment

### Using PM2 (Recommended)

```bash
# Install PM2
npm install -g pm2

# Start deploy bot
pm2 start deploybot.py --name vz-deploy --interpreter python3

# Auto-restart on system reboot
pm2 startup
pm2 save

# Monitor
pm2 status
pm2 logs vz-deploy
```

### Using systemd

Create `/etc/systemd/system/vz-deploybot.service`:
```ini
[Unit]
Description=VZ ASSISTANT Deploy Bot
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/vbot
ExecStart=/usr/bin/python3 deploybot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable vz-deploybot
sudo systemctl start vz-deploybot
sudo systemctl status vz-deploybot
```

---

## 📞 Support

If you have issues:
1. Check logs: `deploybot.log`
2. Verify bot token in config.py
3. Test bot with `/start` command
4. Contact: @VZLfxs

---

## ✅ Checklist

Before going live:

- [ ] Bot created via @BotFather
- [ ] Bot token saved in config.py
- [ ] Deploy bot running (test with /start)
- [ ] Bot profile picture set (optional)
- [ ] Bot description set (optional)
- [ ] Bot commands set (optional)
- [ ] Tested deployment flow
- [ ] Production deployment setup (PM2/systemd)

---

**2025© Vzoel Fox's Lutpan**
**VZ ASSISTANT v0.0.0.69**
