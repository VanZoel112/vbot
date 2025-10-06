"""
VZ ASSISTANT v0.0.0.69
Developer Tools Plugin - Git Pull/Push with Token Management

Commands (DEVELOPER ONLY):
- .pull - Pull latest changes from GitHub
- .push [message] - Push changes to GitHub
- .settoken <token> - Set GitHub personal access token

2025© Vzoel Fox's Lutpan
Founder & DEVELOPER : @VZLfxs
"""

from telethon import events
import subprocess
import os
import config
from utils.animation import animate_loading

# Global variables (set by main.py)
vz_client = None
vz_emoji = None

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_github_token(user_id: int) -> str:
    """Get GitHub token from database."""
    from database.models import DatabaseManager
    db_path = config.DEVELOPER_DB_PATH if config.is_developer(user_id) else config.get_sudoer_db_path(user_id)

    db = DatabaseManager(db_path)

    try:
        # Create table if not exists
        db.execute("""
            CREATE TABLE IF NOT EXISTS github_settings (
                user_id INTEGER PRIMARY KEY,
                token TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        result = db.execute("SELECT token FROM github_settings WHERE user_id = ?", (user_id,)).fetchone()
        db.close()

        return result[0] if result else None
    except:
        db.close()
        return None

def save_github_token(user_id: int, token: str):
    """Save GitHub token to database."""
    from database.models import DatabaseManager
    db_path = config.DEVELOPER_DB_PATH if config.is_developer(user_id) else config.get_sudoer_db_path(user_id)

    db = DatabaseManager(db_path)

    try:
        db.execute("""
            CREATE TABLE IF NOT EXISTS github_settings (
                user_id INTEGER PRIMARY KEY,
                token TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        db.execute("""
            INSERT OR REPLACE INTO github_settings (user_id, token)
            VALUES (?, ?)
        """, (user_id, token))

        db.session.commit()
        db.close()
        return True
    except Exception as e:
        db.close()
        return False

def configure_git_with_token(token: str) -> bool:
    """Configure git to use token for authentication."""
    try:
        # Get current remote URL
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            return False

        remote_url = result.stdout.strip()

        # Convert to token-based URL if it's https
        if remote_url.startswith("https://github.com/"):
            # Extract repo path
            repo_path = remote_url.replace("https://github.com/", "")

            # Set new URL with token
            new_url = f"https://{token}@github.com/{repo_path}"

            subprocess.run(
                ["git", "remote", "set-url", "origin", new_url],
                check=True
            )

            return True

        return False
    except:
        return False

# ============================================================================
# SETTOKEN COMMAND
# ============================================================================

@events.register(events.NewMessage(pattern=r'^\.settoken\s+(.+)$', outgoing=True))
async def settoken_handler(event):
    """
    .settoken - Set GitHub personal access token

    Usage:
        .settoken <your_github_token>

    Get token from: https://github.com/settings/tokens
    Required scopes: repo (full control)

    DEVELOPER ONLY
    """
    global vz_client, vz_emoji

    try:
        user_id = event.sender_id

        print(f"[DEVTOOLS] .settoken command triggered by {user_id}")

        # Check if client and emoji are initialized
        if not vz_client or not vz_emoji:
            print(f"[DEVTOOLS] ERROR: vz_client or vz_emoji not initialized!")
            await event.edit("❌ **Bot not fully initialized!**")
            return

        # Check if developer
        if not config.is_developer(user_id):
            print(f"[DEVTOOLS] Access denied - not developer")
            error_emoji = vz_emoji.getemoji('merah')
            await vz_client.edit_with_premium_emoji(event, f"{error_emoji} **Access Denied!** Developer only command.")
            return

        token = event.pattern_match.group(1).strip()

        # Delete message immediately for security
        await event.delete()

        # Send status message
        loading_emoji = vz_emoji.getemoji('loading')
        msg = await vz_client.client.send_message(event.chat_id, f"{loading_emoji} **Setting GitHub token...**")
    except Exception as e:
        print(f"[DEVTOOLS] FATAL ERROR in settoken_handler: {e}")
        import traceback
        traceback.print_exc()
        try:
            await event.edit(f"❌ **Fatal Error:** {str(e)}")
        except:
            pass
        return

    # Save token
    success = save_github_token(user_id, token)

    if success:
        # Configure git with token
        git_configured = configure_git_with_token(token)

        success_emoji = vz_emoji.getemoji('centang')
        petir_emoji = vz_emoji.getemoji('petir')
        gear_emoji = vz_emoji.getemoji('gear')
        main_emoji = vz_emoji.getemoji('utama')
        dev_emoji = vz_emoji.getemoji('developer')

        status_text = "✅ Configured" if git_configured else "⚠️ Manual config needed"

        await vz_client.edit_with_premium_emoji(msg, f"""
{success_emoji} **GitHub Token Saved**

{gear_emoji} **Git Config:** {status_text}
{petir_emoji} **Token:** `***...{token[-4:]}`

**💡 Usage:**
• `.pull` - Pull latest changes
• `.push [message]` - Push changes

{petir_emoji} {dev_emoji} Plugins Digunakan: **DEVTOOLS**
{petir_emoji} by {main_emoji} {config.RESULT_FOOTER}
""")
    else:
        error_emoji = vz_emoji.getemoji('merah')
        await vz_client.edit_with_premium_emoji(msg, f"{error_emoji} **Failed to save token**")

# ============================================================================
# PULL COMMAND
# ============================================================================

@events.register(events.NewMessage(pattern=r'^\.pull$', outgoing=True))
async def pull_handler(event):
    """
    .pull - Pull latest changes from GitHub

    Pulls latest changes from main branch.
    Requires GitHub token to be set.

    DEVELOPER ONLY
    """
    global vz_client, vz_emoji

    try:
        user_id = event.sender_id

        # Debug log
        print(f"[DEVTOOLS] .pull command triggered by {user_id}")

        # Check if client and emoji are initialized
        if not vz_client or not vz_emoji:
            print(f"[DEVTOOLS] ERROR: vz_client or vz_emoji not initialized!")
            await event.edit("❌ **Bot not fully initialized!**")
            return

        # Check if developer
        if not config.is_developer(user_id):
            print(f"[DEVTOOLS] Access denied - not developer")
            error_emoji = vz_emoji.getemoji('merah')
            await vz_client.edit_with_premium_emoji(event, f"{error_emoji} **Access Denied!** Developer only command.")
            return

        print(f"[DEVTOOLS] Developer check passed")

        # Run animation
        try:
            msg = await animate_loading(vz_client, vz_emoji, event)
            print(f"[DEVTOOLS] Animation loaded successfully")
        except Exception as e:
            print(f"[DEVTOOLS] Animation error: {e}")
            msg = await event.edit("⏳ **Processing...**")
    except Exception as e:
        print(f"[DEVTOOLS] FATAL ERROR in pull_handler: {e}")
        import traceback
        traceback.print_exc()
        try:
            await event.edit(f"❌ **Fatal Error:** {str(e)}")
        except:
            pass
        return

    # Get token
    token = get_github_token(user_id)

    if not token:
        error_emoji = vz_emoji.getemoji('merah')
        gear_emoji = vz_emoji.getemoji('gear')
        petir_emoji = vz_emoji.getemoji('petir')
        main_emoji = vz_emoji.getemoji('utama')

        await vz_client.edit_with_premium_emoji(msg, f"""
{error_emoji} **GitHub Token Required**

{gear_emoji} **Setup Required:**
1. Get token: https://github.com/settings/tokens
2. Required scope: `repo` (full control)
3. Copy token and send:

{petir_emoji} **Command:**
`.settoken <paste_your_token_here>`

{main_emoji} Token will be saved securely
""")
        return

    # Configure git with token
    loading_emoji = vz_emoji.getemoji('loading')
    await vz_client.edit_with_premium_emoji(msg, f"{loading_emoji} **Configuring git...**")

    configure_git_with_token(token)

    # Pull changes
    await vz_client.edit_with_premium_emoji(msg, f"{loading_emoji} **Pulling changes from GitHub...**")

    try:
        result = subprocess.run(
            ["git", "pull", "origin", "main"],
            capture_output=True,
            text=True,
            timeout=30
        )

        output = result.stdout + result.stderr

        # Check if authentication failed
        if "Authentication failed" in output or "could not read Username" in output or result.returncode == 128:
            error_emoji = vz_emoji.getemoji('merah')
            gear_emoji = vz_emoji.getemoji('gear')
            petir_emoji = vz_emoji.getemoji('petir')

            await vz_client.edit_with_premium_emoji(msg, f"""
{error_emoji} **Authentication Failed**

{gear_emoji} **Token expired or invalid**

{petir_emoji} **Get new token:**
https://github.com/settings/tokens

Then copy and send:
`.settoken <paste_new_token_here>`
""")
            return

        # Success
        if result.returncode == 0:
            success_emoji = vz_emoji.getemoji('centang')
            petir_emoji = vz_emoji.getemoji('petir')
            gear_emoji = vz_emoji.getemoji('gear')
            main_emoji = vz_emoji.getemoji('utama')
            dev_emoji = vz_emoji.getemoji('developer')

            # Truncate output if too long
            if len(output) > 500:
                output = output[:500] + "\n... (truncated)"

            await vz_client.edit_with_premium_emoji(msg, f"""
{success_emoji} **Pull Complete**

**Output:**
```
{output}
```

{gear_emoji} **Next Steps:**
• `.restart` to apply changes

{petir_emoji} {dev_emoji} Plugins Digunakan: **DEVTOOLS**
{petir_emoji} by {main_emoji} {config.RESULT_FOOTER}
""")
        else:
            error_emoji = vz_emoji.getemoji('merah')
            await vz_client.edit_with_premium_emoji(msg, f"""
{error_emoji} **Pull Failed**

**Error:**
```
{output[:500]}
```
""")

    except subprocess.TimeoutExpired:
        error_emoji = vz_emoji.getemoji('merah')
        await vz_client.edit_with_premium_emoji(msg, f"{error_emoji} **Timeout!** Pull took too long")
    except Exception as e:
        error_emoji = vz_emoji.getemoji('merah')
        await vz_client.edit_with_premium_emoji(msg, f"{error_emoji} **Error:** {str(e)}")

# ============================================================================
# PUSH COMMAND
# ============================================================================

@events.register(events.NewMessage(pattern=r'^\.push(?:\s+(.+))?$', outgoing=True))
async def push_handler(event):
    """
    .push - Push changes to GitHub

    Usage:
        .push [commit message]

    Pushes all changes to GitHub main branch.
    Requires GitHub token to be set.

    DEVELOPER ONLY
    """
    global vz_client, vz_emoji

    user_id = event.sender_id

    # Check if developer
    if not config.is_developer(user_id):
        error_emoji = vz_emoji.getemoji('merah')
        await vz_client.edit_with_premium_emoji(event, f"{error_emoji} **Access Denied!** Developer only command.")
        return

    commit_message = event.pattern_match.group(1)

    if not commit_message:
        commit_message = "Update: Quick changes"

    # Run animation
    msg = await animate_loading(vz_client, vz_emoji, event)

    # Get token
    token = get_github_token(user_id)

    if not token:
        error_emoji = vz_emoji.getemoji('merah')
        gear_emoji = vz_emoji.getemoji('gear')
        petir_emoji = vz_emoji.getemoji('petir')
        main_emoji = vz_emoji.getemoji('utama')

        await vz_client.edit_with_premium_emoji(msg, f"""
{error_emoji} **GitHub Token Required**

{gear_emoji} **Setup Required:**
1. Get token: https://github.com/settings/tokens
2. Required scope: `repo` (full control)
3. Copy token and send:

{petir_emoji} **Command:**
`.settoken <paste_your_token_here>`

{main_emoji} Token will be saved securely
""")
        return

    # Configure git with token
    loading_emoji = vz_emoji.getemoji('loading')
    await vz_client.edit_with_premium_emoji(msg, f"{loading_emoji} **Configuring git...**")

    configure_git_with_token(token)

    # Add all changes
    await vz_client.edit_with_premium_emoji(msg, f"{loading_emoji} **Adding changes...**")

    try:
        subprocess.run(["git", "add", "."], check=True, timeout=10)

        # Commit
        await vz_client.edit_with_premium_emoji(msg, f"{loading_emoji} **Committing...**")

        subprocess.run(
            ["git", "commit", "-m", f"{commit_message}\n\n🤖 Generated with Claude Code"],
            check=True,
            timeout=10
        )

        # Push
        await vz_client.edit_with_premium_emoji(msg, f"{loading_emoji} **Pushing to GitHub...**")

        result = subprocess.run(
            ["git", "push", "origin", "main"],
            capture_output=True,
            text=True,
            timeout=30
        )

        output = result.stdout + result.stderr

        # Check if authentication failed
        if "Authentication failed" in output or "could not read Username" in output or result.returncode == 128:
            error_emoji = vz_emoji.getemoji('merah')
            gear_emoji = vz_emoji.getemoji('gear')
            petir_emoji = vz_emoji.getemoji('petir')

            await vz_client.edit_with_premium_emoji(msg, f"""
{error_emoji} **Authentication Failed**

{gear_emoji} **Token expired or invalid**

{petir_emoji} **Get new token:**
https://github.com/settings/tokens

Then copy and send:
`.settoken <paste_new_token_here>`
""")
            return

        # Success
        if result.returncode == 0:
            success_emoji = vz_emoji.getemoji('centang')
            petir_emoji = vz_emoji.getemoji('petir')
            camera_emoji = vz_emoji.getemoji('camera')
            main_emoji = vz_emoji.getemoji('utama')
            dev_emoji = vz_emoji.getemoji('developer')

            await vz_client.edit_with_premium_emoji(msg, f"""
{success_emoji} **Push Complete**

{camera_emoji} **Commit:** {commit_message}
{petir_emoji} **Branch:** main

**Output:**
```
{output[:500]}
```

{petir_emoji} {dev_emoji} Plugins Digunakan: **DEVTOOLS**
{petir_emoji} by {main_emoji} {config.RESULT_FOOTER}
""")
        else:
            error_emoji = vz_emoji.getemoji('merah')
            await vz_client.edit_with_premium_emoji(msg, f"""
{error_emoji} **Push Failed**

**Error:**
```
{output[:500]}
```
""")

    except subprocess.CalledProcessError as e:
        # No changes to commit
        if "nothing to commit" in str(e.stderr):
            error_emoji = vz_emoji.getemoji('merah')
            await vz_client.edit_with_premium_emoji(msg, f"{error_emoji} **No changes to commit**")
        else:
            error_emoji = vz_emoji.getemoji('merah')
            await vz_client.edit_with_premium_emoji(msg, f"{error_emoji} **Error:** {str(e)}")
    except subprocess.TimeoutExpired:
        error_emoji = vz_emoji.getemoji('merah')
        await vz_client.edit_with_premium_emoji(msg, f"{error_emoji} **Timeout!** Push took too long")
    except Exception as e:
        error_emoji = vz_emoji.getemoji('merah')
        await vz_client.edit_with_premium_emoji(msg, f"{error_emoji} **Error:** {str(e)}")

print("✅ Plugin loaded: devtools.py")
