# 🚀 VZ ASSISTANT - PROJECT ROADMAP

**Versi:** 0.0.0.69
**Founder & Developer:** @VZLfxs
**Branding:** Vzoel Fox's Lutpan
**Tech Stack:** Telethon × Python 3+

---

## 📋 TABLE OF CONTENTS

1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Development Phases](#development-phases)
4. [Features Breakdown](#features-breakdown)
5. [Technical Requirements](#technical-requirements)
6. [Branding Guidelines](#branding-guidelines)

---

## 🎯 PROJECT OVERVIEW

**VZ ASSISTANT** adalah Telegram Userbot dengan sistem hierarki multi-level yang memisahkan **Developer** dan **Sudoers** dengan database dan permission terpisah.

### Key Features:
- ✅ Dual-tier system (Developer & Sudoers)
- ✅ Individual database per sudoers
- ✅ Customizable prefix per user
- ✅ Deploy bot system for auto-onboarding
- ✅ Advanced broadcast with blacklist
- ✅ Voice chat support
- ✅ Payment integration
- ✅ PM Permit system
- ✅ Animated responses with premium emoji mapping

---

## 🏗️ SYSTEM ARCHITECTURE

### User Hierarchy

```
┌─────────────────────────────────────┐
│         DEVELOPER LEVEL             │
├─────────────────────────────────────┤
│ • Full access to all commands       │
│ • Can use 's' prefix for sudo cmds  │
│ • Access to all sudoers databases   │
│ • Deploy/manage sudoers sessions    │
│ • Force logout sudoers (.out)       │
│ • View all logs                     │
└─────────────────────────────────────┘
              ↓ manages
┌─────────────────────────────────────┐
│          SUDOERS LEVEL              │
├─────────────────────────────────────┤
│ • Individual database & client      │
│ • Customizable prefix               │
│ • Standard userbot commands         │
│ • Cannot access developer commands  │
│ • Cannot view developer database    │
└─────────────────────────────────────┘
```

### Database Structure

```
databases/
├── developer/
│   ├── main.db (developer data)
│   └── logs.db (all sudoers logs)
│
├── shared/
│   └── emojiprime.json (emoji premium mapping)
│
└── sudoers/
    ├── user_123456789/
    │   ├── client.db
    │   ├── lockglobal.json
    │   └── blgc.json
    │
    └── user_987654321/
        ├── client.db
        ├── lockglobal.json
        └── blgc.json
```

### Config & Environment

**config.py:**
- Developer ID(s) - Multiple IDs allowed
- Bot deploy token
- API ID & Hash (to be provided)
- Premium emoji mapping (to be provided)
- Default branding templates

**.env:**
- SESSION_STRING
- API_ID
- API_HASH
- BOT_TOKEN (for deploy bot)
- LOG_GROUP_ID

---

## 📅 DEVELOPMENT PHASES

### **PHASE 1: Core Foundation** ⏳ Week 1-2

#### 1.1 Base Setup
- [ ] Project structure & dependencies
- [ ] Telethon client initialization
- [ ] Config & environment loader
- [ ] Database models (SQLAlchemy)
- [ ] Developer/Sudoers authentication system

#### 1.2 Database System
- [ ] SQLite setup per user
- [ ] JSON storage (lockglobal.json, blgc.json)
- [ ] Database helper functions
- [ ] Migration system

#### 1.3 Prefix System
- [ ] Dynamic prefix handler
- [ ] Prefix customization (.prefix command)
- [ ] Support for: `. + # @ : ?` or alphanumeric or none
- [ ] Prefix storage in user database

---

### **PHASE 2: Command Framework** ⏳ Week 3-4

#### 2.1 Command Handler
- [ ] Decorator-based command system
- [ ] IF/Process/Result animation framework
- [ ] 8-step edit animation system
- [ ] Priority queue for process completion

#### 2.2 Response System
- [ ] Markdown parser
- [ ] Premium emoji mapper (awaiting mapping data)
- [ ] Edit animation (1.5s intervals for vzoel, 2.5s for tag)
- [ ] Template renderer

#### 2.3 Permission System
- [ ] Developer command filter
- [ ] Sudoers command filter
- [ ] 's' prefix sudo trigger for developers
- [ ] Command blacklist/whitelist

---

### **PHASE 3: Sudoers Commands** ⏳ Week 5-7

#### 3.1 Shadow Clear (.lock/.unlock)
- [ ] Auto-delete messages from target users
- [ ] Requires admin rights verification
- [ ] lockglobal.json storage
- [ ] Username/reply-based targeting
- [ ] Real-time database updates

#### 3.2 BLGCAST (.bl/.dbl/.gcast)
- [ ] Blacklist group/channel storage (blgc.json)
- [ ] Add/remove from blacklist
- [ ] Broadcast with blacklist filtering
- [ ] Reply-based or text-based gcast
- [ ] Progress indicator during broadcast

#### 3.3 Cek ID (.id/.getfileid)
- [ ] User info fetcher (ID, name, username)
- [ ] Group count calculator
- [ ] File ID extractor for media
- [ ] Reply-based targeting

#### 3.4 PING System (.ping/.pink/.pong)
- [ ] `.ping` - Latency + Uptime + Owner + Founder
- [ ] `.pink` - Latency with color emoji mapping:
  - 1-150ms: Blue emoji
  - 151-200ms: Yellow emoji
  - 200+ms: Red emoji
  - Auto-trigger `.limit` after
- [ ] `.pong` - Uptime display
  - Auto-trigger `.alive` after

#### 3.5 Limit (.limit)
- [ ] Auto-connect to @spambot
- [ ] Auto-press start button
- [ ] Return @spambot response
- [ ] Parse limit status

#### 3.6 ALIVE (.alive)
- [ ] Template rendering with:
  - Founder: Vzoel Fox's/t.me/VZLfxs
  - Owner: @usernameownerid
  - Version: 0.0.0.69
  - Telethon × Python 3+
  - Total plugins count
  - Uptime display
- [ ] Inline buttons:
  - HELP button → .help
  - DEV button → @VZLfxs
- [ ] Footer branding

#### 3.7 VC (.joinvc/.leavevc)
- [ ] pytgcalls integration
- [ ] tgcrypto support
- [ ] Join/create voice chat
- [ ] Leave voice chat
- [ ] User-based (no admin required)
- [ ] Reference pytgcalls docs

#### 3.8 PAYMENT (.get/.setget/.getqr)
- [ ] `.get` - Display payment info
- [ ] `.setget` - Set payment info (max 3 entries):
  ```
  EWALLET/BANK      :
  NOMOR REKENING :
  ATAS NAMA             :
  ```
- [ ] `.getqr` - Set QR payment:
  - Auto-use .getfileid for image
  - Store file_id for QR code

#### 3.9 TAGALL (.tag/.stag)
- [ ] `.tag <text>` or `.tag reply` - Mention all users
- [ ] No admin rights required
- [ ] Edit message every 2.5s
- [ ] Call 10 random users per edit
- [ ] Auto-stop when all called
- [ ] Final summary: user count + time elapsed
- [ ] `.stag` - Manual stop

#### 3.10 PERMIT (.pmon/.pmoff/.setpm)
- [ ] PM permit system
- [ ] `.pmon` - Enable PM permit
- [ ] `.pmoff` - Disable PM permit
- [ ] `.setpm` - Customize permit message
- [ ] Default: Vzoel Fox's branding
- [ ] Developer bypass (never triggered/blocked)
- [ ] Sudoers get triggered by developer's PM permit

#### 3.11 HELP (.help)
- [x] Userbot `.help` membuka inline browser via assistant bot (fallback otomatis bila offline)
- [ ] Inline button interface
- [ ] List all plugins + functions
- [ ] Hide developer-only plugins for sudoers
- [ ] Show developer plugins for developers
- [ ] Category-based navigation

#### 3.12 ADMIN (.admin/.unadmin)
- [ ] `.admin @user <title>` or `.admin reply <title>`
  - Promote user to admin
  - Requires add admin permission
  - Default title: "admin"
- [ ] `.unadmin @user` or `.unadmin reply`
  - Demote admin
  - Developer immune to unadmin

#### 3.13 PREFIX (.prefix)
- [ ] `.prefix <new_prefix>` - Change user prefix
- [ ] Validate allowed prefixes
- [ ] Store in user database
- [ ] Apply immediately

#### 3.14 SHOWJSON (.showjson)
- [ ] `.showjson` - Display metrics & mapping data
- [ ] Show emoji premium ID mapping
- [ ] Display file ID from media
- [ ] Show usage metrics/statistics
- [ ] JSON formatted output
- [ ] Auto-triggered by commands (gcast, tagall, etc.)
- [ ] Emoji conversion engine:
  - Convert standard emoji to premium emoji
  - Use mapping from premium emoji ID database
  - Apply conversion before sending messages
  - Fallback to standard emoji if mapping not found
- [ ] Store mapping in emojiprime.json
- [ ] Real-time emoji replacement for:
  - `.gcast` broadcasts
  - `.tag` mentions
  - All response messages
  - Animated process/result outputs

---

### **PHASE 4: Developer Commands** ⏳ Week 8-9

#### 4.1 Sudo Access
- [ ] 's' prefix system for all sudoers commands
- [ ] Example: `sgcast` triggers gcast for target sudoer
- [ ] Target selection mechanism

#### 4.2 DEPLOY (.dp/.cr)
- [ ] `.dp` - Deploy access via bot
  - User provides phone number
  - Bot sends code
  - Auto-deploy as sudoers
  - Create user database
  - Initialize session
- [ ] `.cr` - Force stop sudoers session
  - Terminate active session
  - Cleanup resources

#### 4.3 LOG System
- [ ] Central log group
- [ ] All sudoers logs forwarded
- [ ] Log format with timestamps
- [ ] User identification
- [ ] Command tracking

#### 4.4 OUT (.out)
- [ ] `.out @user` or `.out reply`
- [ ] Force logout sudoers client
- [ ] Terminate Telegram session
- [ ] Database cleanup option

#### 4.5 VZOEL (.vzoel)
- [ ] 12 edit animation
- [ ] 1.5s interval per edit
- [ ] Final: Developer profile display
- [ ] Premium emoji integration

#### 4.6 Database Access
- [ ] `.sdb @username` - View sudoers database
- [ ] `.sgd reply` - Get data from reply context
- [ ] Read-only for developer
- [ ] Full isolation from sudoers

---

### **PHASE 5: Animation & UI** ⏳ Week 10

#### 5.1 Response Animation
- [ ] IF stage: "OK" initial response
- [ ] Process stage: 8-step edit animation
  - Create plugin-specific process mapping
  - Priority processing (no interruption)
- [ ] Result stage: Final output with animation
  - Gradual text reveal
  - Premium emoji at start of each line

#### 5.2 Emoji Mapping
- [ ] Load premium emoji mapping from emojiprime.json
- [ ] Map emojis per command category
- [ ] Consistent emoji usage
- [ ] Fallback for non-premium users
- [ ] Integration with .showjson for emoji conversion:
  - Auto-convert standard emoji to premium before sending
  - Apply to all commands: gcast, tagall, responses
  - Real-time replacement engine
  - Cache mapping for performance
- [ ] Emoji conversion priority:
  1. Check emojiprime.json for mapping
  2. Convert standard → premium emoji ID
  3. Fallback to standard if not found
  4. Log conversion metrics

#### 5.3 Branding Integration
- [ ] Template system for all responses
- [ ] Header: **Vz ASSISTANT**
- [ ] Footer: **2025© Vzoel Fox's Lutpan {plugin_name}**
- [ ] Credit: **Founder & DEVELOPER: @VZLfxs**
- [ ] Version stamp: **0.0.0.69**

---

### **PHASE 6: Deploy Bot** ⏳ Week 11-12

#### 6.1 Bot Development
- [ ] Separate bot project (python-telegram-bot)
- [ ] `/start` - Welcome message
- [ ] Phone number request
- [ ] Code verification
- [ ] Session creation
- [ ] Auto-add to sudoers list

#### 6.2 Integration
- [ ] Communication with main userbot
- [ ] Database sync
- [ ] Session storage
- [ ] Auto-notification to developer

---

### **PHASE 7: Testing & Polish** ⏳ Week 13-14

#### 7.1 Testing
- [ ] Unit tests for core functions
- [ ] Integration tests for commands
- [ ] Database integrity tests
- [ ] Permission system tests
- [ ] Animation/UI tests

#### 7.2 Documentation
- [ ] User guide for sudoers
- [ ] Developer documentation
- [ ] Deployment guide
- [ ] Configuration guide
- [ ] Troubleshooting guide

#### 7.3 Optimization
- [ ] Performance profiling
- [ ] Database query optimization
- [ ] Memory leak checks
- [ ] Error handling improvements

---

## 🔧 FEATURES BREAKDOWN

### Sudoers Commands Summary

| Command | Description | Requires Admin | Database |
|---------|-------------|----------------|----------|
| `.lock/.unlock` | Shadow clear auto-delete | ✅ Yes | lockglobal.json |
| `.bl/.dbl` | Blacklist groups for gcast | ❌ No | blgc.json |
| `.gcast` | Broadcast to all groups | ❌ No | blgc.json |
| `.id/.getfileid` | Get user/file info | ❌ No | - |
| `.ping/.pink/.pong` | Latency & uptime | ❌ No | - |
| `.limit` | Check spam status | ❌ No | - |
| `.alive` | Show bot info | ❌ No | - |
| `.joinvc/.leavevc` | Voice chat controls | ❌ No | - |
| `.get/.setget/.getqr` | Payment info | ❌ No | user.db |
| `.tag/.stag` | Tag all members | ❌ No | - |
| `.pmon/.pmoff/.setpm` | PM permit system | ❌ No | user.db |
| `.help` | Show commands | ❌ No | - |
| `.admin/.unadmin` | Manage admins | ✅ Yes | - |
| `.prefix` | Change prefix | ❌ No | user.db |
| `.showjson` | Show metrics & emoji mapping | ❌ No | emojiprime.json |

### Developer Commands Summary

| Command | Description | Target |
|---------|-------------|--------|
| `s<command>` | Sudo any sudoers command | Sudoers |
| `.dp` | Deploy new sudoers | New user |
| `.cr` | Force stop session | Sudoers |
| `.out` | Force logout | Sudoers |
| `.vzoel` | Show developer profile | Self |
| `.sdb` | View sudoers database | Sudoers |
| `.sgd` | Get data from reply | Sudoers |

---

## 🛠️ TECHNICAL REQUIREMENTS

### Dependencies

```python
# Core
telethon>=1.28.0
python-telegram-bot>=20.0  # For deploy bot
sqlalchemy>=2.0.0
aiosqlite>=0.19.0

# Voice Chat
pytgcalls>=3.0.0
tgcrypto>=1.2.5

# Utilities
python-dotenv>=1.0.0
aiofiles>=23.0.0
emoji>=2.8.0
```

### Python Version
- **Required:** Python 3.9+
- **Recommended:** Python 3.11

### System Requirements
- **OS:** Linux (Ubuntu/Debian) or Termux
- **RAM:** Minimum 512MB
- **Storage:** 1GB free space
- **Network:** Stable internet connection

### Telegram Requirements
- **API ID & Hash:** From my.telegram.org (to be provided)
- **Phone Number:** For session creation
- **Premium Account:** For premium emoji (optional)

---

## 🎨 BRANDING GUIDELINES

### Mandatory Branding Elements

**Every response/plugin MUST include:**

1. **Header:**
   ```
   Vz ASSISTANT
   ```

2. **Footer:**
   ```
   2025© Vzoel Fox's Lutpan {plugin_name}
   Founder & DEVELOPER : @VZLfxs
   ```

3. **Version Lock:**
   - Always display: `0.0.0.69`
   - Never change even after updates

4. **Founder Credit:**
   - Founder link: `t.me/VZLfxs`
   - Developer mention: `@VZLfxs`

### Template Examples

#### ALIVE Template:
```
   Vz ASSISTANT



Founder         : Vzoel Fox's/t.me/VZLfxs
Owner            : @usernameownerid
Versi              : 0.0.0.69
Telethon × Python 3+
Total Plugin  : {plugin_count}
Waktu Nyala : {uptime}

~Vzoel Fox's Lutpan

[HELP/.help] [DEV/@VZLfxs]
```

#### PAYMENT Template:
```
Vz ASSISTANT - Payment Info

{payment_info}

2025© Vzoel Fox's Lutpan PAYMENT
Founder & DEVELOPER : @VZLfxs
```

### Premium Emoji Mapping
- **To be provided:** Full emoji mapping
- **Usage:** Every response line starts with mapped emoji
- **Fallback:** Standard emoji for non-premium

### Markdown Standards
- Bold: `**text**`
- Italic: `__text__`
- Code: `` `code` ``
- Links: `[text](url)`

---

## 📝 NOTES & PENDING DATA

### Awaiting Information:
1. ✅ **Developer ID(s)** - (Manual config)
2. ⏳ **API ID & Hash** - To be provided
3. ✅ **Premium Emoji Mapping** - COMPLETED (emojiprime.json created with 17 emojis)
4. ⏳ **Process Animation Mapping** - Per plugin

### Emoji Prime Mapping - READY ✅

**File:** `emojiprime.json` (17 premium emojis mapped)

**Available Emojis:**
- **Identity:** 🤩 (MAIN_VZOEL), 👨‍💻 (DEVELOPER), 🌟 (OWNER)
- **System:** ⚙️ (GEAR), ✅ (CHECKLIST), ⛈ (PETIR), 🎚 (NYALA)
- **Status:** 👍 (HIJAU), ⚠️ (KUNING), 👎 (MERAH)
- **Communication:** ✉️ (TELEGRAM), 📷 (CAMERA)
- **Process:** 😈 (PROSES_1), 🔪 (PROSES_2), 😐 (PROSES_3)
- **Special:** 👨‍🚀 (ROBOT), ♾ (LOADING)

**Usage Examples:**
- `.pink` latency colors: 👍 (1-150ms), ⚠️ (151-200ms), 👎ย (200+ms)
- Process animation: 😈 → 🔪 → 😐 → ♾
- User roles: 🤩 (Vzoel), 👨‍💻 (Dev), 🌟 (Owner)

**Structure:** See `emojiprime.json` for full mapping with Telegram entities

### Important Reminders:
- ⚠️ **NEVER** change branding (even minor edits)
- ⚠️ **NEVER** change version number (locked at 0.0.0.69)
- ⚠️ **ALWAYS** use premium emoji mapping when provided
- ⚠️ **ALWAYS** include founder credit

---

## 🚦 DEVELOPMENT STATUS

### Current Phase: **PLANNING** ✅
- [x] Requirements gathered
- [x] Roadmap created
- [ ] Architecture finalized
- [ ] Development started

### Next Steps:
1. Finalize project structure
2. Setup development environment
3. Initialize Telethon client
4. Build core authentication system
5. Implement database models

---

## 📞 CONTACT & SUPPORT

**Founder & Developer:** @VZLfxs
**Telegram:** t.me/VZLfxs

---

**2025© Vzoel Fox's Lutpan**
**Vz ASSISTANT v0.0.0.69**
