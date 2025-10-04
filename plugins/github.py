"""
VZ ASSISTANT v0.0.0.69
GitHub Integration Plugin - Developer Only

Commands:
- .settoken <token> - Configure GitHub personal access token
- .push [message] - Commit and push changes
- .pull - Pull latest changes with auto-rebase
- .gitstatus - Show repository status

2025© Vzoel Fox's Lutpan
Founder & DEVELOPER : @VZLfxs
"""

from telethon import events
import config
from core.git_manager import GitManager

# Global variables (set by main.py)
vz_client = None
vz_emoji = None
git_manager = None

# Initialize git manager
try:
    git_manager = GitManager()
except Exception as e:
    print(f"❌ Git manager init error: {e}")

# ============================================================================
# SET TOKEN COMMAND (Developer Only)
# ============================================================================

@events.register(events.NewMessage(pattern=r'^\.settoken (.+)$', outgoing=True))
async def settoken_handler(event):
    """
    .settoken - Configure GitHub token (Developer only)

    Usage:
        .settoken <your_github_token>

    Saves token securely for push/pull operations
    """
    global vz_client, vz_emoji, git_manager

    # Developer only check
    user_id = event.sender_id
    if not config.is_developer(user_id):
        return

    if not git_manager:
        merah_emoji = vz_emoji.getemoji('merah')
        await vz_client.edit_with_premium_emoji(
            event,
            f"{merah_emoji} Git manager not initialized\n\nVZ ASSISTANT"
        )
        return

    token = event.pattern_match.group(1).strip()

    # Processing message
    loading_emoji = vz_emoji.getemoji('loading')
    proses_emoji = vz_emoji.getemoji('robot')
    telegram_emoji = vz_emoji.getemoji('telegram')

    processing_msg = f"""{loading_emoji} **CONFIGURING GITHUB TOKEN**

{proses_emoji} Validating token
{telegram_emoji} Please wait

VZ ASSISTANT"""

    await vz_client.edit_with_premium_emoji(event, processing_msg)

    # Delete original message for security
    try:
        await event.delete()
    except:
        pass

    # Set token
    success = git_manager.set_token(token)

    if success:
        centang_emoji = vz_emoji.getemoji('centang')
        aktif_emoji = vz_emoji.getemoji('aktif')
        proses_emoji = vz_emoji.getemoji('robot')
        biru_emoji = vz_emoji.getemoji('camera')

        response = f"""{centang_emoji} **GITHUB TOKEN CONFIGURED**

{aktif_emoji} Token saved securely
{telegram_emoji} Ready for push/pull operations

{proses_emoji} Use .push to push changes
{biru_emoji} Use .pull to pull updates

VZ ASSISTANT GitHub Integration
CONTACT: @VZLfxs"""
    else:
        merah_emoji = vz_emoji.getemoji('merah')
        kuning_emoji = vz_emoji.getemoji('kuning')

        response = f"""{merah_emoji} **TOKEN CONFIGURATION FAILED**

{kuning_emoji} Please try again

VZ ASSISTANT"""

    # Send as new message (original deleted)
    await event.respond(response)

# ============================================================================
# PUSH COMMAND (Developer Only)
# ============================================================================

@events.register(events.NewMessage(pattern=r'^\.push(?: (.+))?$', outgoing=True))
async def push_handler(event):
    """
    .push - Push to GitHub (Developer only)

    Usage:
        .push                  (auto commit message)
        .push <message>        (custom commit message)

    Auto-commits all changes and pushes to remote
    """
    global vz_client, vz_emoji, git_manager

    # Developer only check
    user_id = event.sender_id
    if not config.is_developer(user_id):
        return

    if not git_manager:
        merah_emoji = vz_emoji.getemoji('merah')
        await vz_client.edit_with_premium_emoji(
            event,
            f"{merah_emoji} Git manager not initialized\n\nVZ ASSISTANT"
        )
        return

    # Get custom message if provided
    custom_message = event.pattern_match.group(1)
    if custom_message:
        custom_message = custom_message.strip()

    # Processing message
    loading_emoji = vz_emoji.getemoji('loading')
    proses_emoji = vz_emoji.getemoji('robot')
    telegram_emoji = vz_emoji.getemoji('telegram')
    aktif_emoji = vz_emoji.getemoji('aktif')

    processing_msg = f"""{loading_emoji} **PUSHING TO GITHUB**

{proses_emoji} Checking repository status
{telegram_emoji} Committing changes
{aktif_emoji} Preparing push

VZ ASSISTANT"""

    await vz_client.edit_with_premium_emoji(event, processing_msg)

    # Push
    success, message = git_manager.push(custom_message)

    if success:
        status = git_manager.get_status()
        centang_emoji = vz_emoji.getemoji('centang')
        biru_emoji = vz_emoji.getemoji('camera')

        response = f"""{centang_emoji} **PUSH SUCCESSFUL**

{aktif_emoji} Branch: {status['branch']}
{telegram_emoji} Last commit: {status['last_commit']}
{proses_emoji} Changes synced to remote

{biru_emoji} Your code is now on GitHub

VZ ASSISTANT GitHub Integration
CONTACT: @VZLfxs"""
    else:
        merah_emoji = vz_emoji.getemoji('merah')
        kuning_emoji = vz_emoji.getemoji('kuning')

        response = f"""{merah_emoji} **PUSH FAILED**

{kuning_emoji} Error: {message}

{aktif_emoji} Possible solutions:
• Check your GitHub token (.settoken)
• Pull latest changes first (.pull)
• Check repository permissions

VZ ASSISTANT GitHub Integration
CONTACT: @VZLfxs"""

    await vz_client.edit_with_premium_emoji(event, response)

# ============================================================================
# PULL COMMAND (Developer Only)
# ============================================================================

@events.register(events.NewMessage(pattern=r'^\.pull$', outgoing=True))
async def pull_handler(event):
    """
    .pull - Pull from GitHub (Developer only)

    Fetches and merges latest changes with auto-rebase
    Handles conflicts automatically when possible
    """
    global vz_client, vz_emoji, git_manager

    # Developer only check
    user_id = event.sender_id
    if not config.is_developer(user_id):
        return

    if not git_manager:
        merah_emoji = vz_emoji.getemoji('merah')
        await vz_client.edit_with_premium_emoji(
            event,
            f"{merah_emoji} Git manager not initialized\n\nVZ ASSISTANT"
        )
        return

    # Processing message
    loading_emoji = vz_emoji.getemoji('loading')
    proses_emoji = vz_emoji.getemoji('robot')
    telegram_emoji = vz_emoji.getemoji('telegram')
    aktif_emoji = vz_emoji.getemoji('aktif')

    processing_msg = f"""{loading_emoji} **PULLING FROM GITHUB**

{proses_emoji} Fetching remote changes
{telegram_emoji} Checking for conflicts
{aktif_emoji} Applying updates

VZ ASSISTANT"""

    await vz_client.edit_with_premium_emoji(event, processing_msg)

    # Pull
    success, message = git_manager.pull()

    if success:
        status = git_manager.get_status()
        centang_emoji = vz_emoji.getemoji('centang')
        biru_emoji = vz_emoji.getemoji('camera')

        response = f"""{centang_emoji} **PULL SUCCESSFUL**

{aktif_emoji} Branch: {status['branch']}
{telegram_emoji} Last commit: {status['last_commit']}
{proses_emoji} Local repository updated

{biru_emoji} Your code is now up to date

VZ ASSISTANT GitHub Integration
CONTACT: @VZLfxs"""
    else:
        merah_emoji = vz_emoji.getemoji('merah')
        kuning_emoji = vz_emoji.getemoji('kuning')

        response = f"""{merah_emoji} **PULL FAILED**

{kuning_emoji} Error: {message}

{aktif_emoji} Possible solutions:
• Check your GitHub token (.settoken)
• Resolve merge conflicts manually
• Check repository permissions

VZ ASSISTANT GitHub Integration
CONTACT: @VZLfxs"""

    await vz_client.edit_with_premium_emoji(event, response)

# ============================================================================
# GIT STATUS COMMAND (Developer Only)
# ============================================================================

@events.register(events.NewMessage(pattern=r'^\.gitstatus$', outgoing=True))
async def gitstatus_handler(event):
    """
    .gitstatus - Show repository status (Developer only)

    Displays branch, commits, changes, and sync status
    """
    global vz_client, vz_emoji, git_manager

    # Developer only check
    user_id = event.sender_id
    if not config.is_developer(user_id):
        return

    if not git_manager:
        merah_emoji = vz_emoji.getemoji('merah')
        await vz_client.edit_with_premium_emoji(
            event,
            f"{merah_emoji} Git manager not initialized\n\nVZ ASSISTANT"
        )
        return

    # Processing message
    loading_emoji = vz_emoji.getemoji('loading')
    proses_emoji = vz_emoji.getemoji('robot')

    processing_msg = f"""{loading_emoji} **CHECKING REPOSITORY STATUS**

{proses_emoji} Please wait

VZ ASSISTANT"""

    await vz_client.edit_with_premium_emoji(event, processing_msg)

    # Get status
    info = git_manager.get_git_info()

    if 'error' in info:
        merah_emoji = vz_emoji.getemoji('merah')
        kuning_emoji = vz_emoji.getemoji('kuning')

        response = f"""{merah_emoji} **STATUS CHECK FAILED**

{kuning_emoji} Error: {info['error']}

VZ ASSISTANT"""
    else:
        # Build status message
        utama_emoji = vz_emoji.getemoji('utama')
        proses_emoji = vz_emoji.getemoji('robot')
        telegram_emoji = vz_emoji.getemoji('telegram')
        aktif_emoji = vz_emoji.getemoji('aktif')
        biru_emoji = vz_emoji.getemoji('camera')
        kuning_emoji = vz_emoji.getemoji('kuning')
        centang_emoji = vz_emoji.getemoji('centang')
        adder1_emoji = vz_emoji.getemoji('petir')

        has_changes_icon = centang_emoji if info['has_changes'] else kuning_emoji
        changes_status = "Yes" if info['has_changes'] else "No"
        token_status = "Configured" if info['has_token'] else "Not configured"

        response = f"""{utama_emoji} **REPOSITORY STATUS**

{proses_emoji} BRANCH: {info['branch']}
{telegram_emoji} REMOTE: {info['remote']}
{aktif_emoji} TOTAL COMMITS: {info['total_commits']}

{biru_emoji} CHANGES:
• Modified files: {info['modified']}
• Untracked files: {info['untracked']}
• Has changes: {changes_status}

{kuning_emoji} SYNC STATUS:
• Commits ahead: {info['commits_ahead']}
• Commits behind: {info['commits_behind']}

{centang_emoji} LAST COMMIT:
{info['last_commit']}

{has_changes_icon} GITHUB TOKEN: {token_status}

{adder1_emoji} AVAILABLE COMMANDS:
• .push - Push changes
• .pull - Pull updates
• .settoken - Configure token

VZ ASSISTANT GitHub Integration
CONTACT: @VZLfxs"""

    await vz_client.edit_with_premium_emoji(event, response)

print("✅ Plugin loaded: github.py")
