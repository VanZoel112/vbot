"""
VZ ASSISTANT v0.0.0.69
Approve Plugin - Quick Deploy Access Approval

2025© Vzoel Fox's Lutpan
Founder & DEVELOPER : @VZLfxs
"""

from telethon import events
import config
from database.deploy_auth import DeployAuthDB
from utils.animation import animate_loading

# Global variables (set by main.py)
vz_client = None
vz_emoji = None

# ============================================================================
# QUICK APPROVE COMMAND (Developer Only)
# ============================================================================

@events.register(events.NewMessage(pattern=r'^\.\.ok(?:\s+@?(\w+))?$', outgoing=True))
async def quick_approve_handler(event):
    """
    ..ok - Quick approve deploy access & send bot link

    Usage:
        ..ok (reply to user message)
        ..ok @username
        ..ok username

    Developer only command.
    Auto-approves user for deploy access and sends deploy bot link.
    """
    global vz_client, vz_emoji

    # Check if developer
    if not config.is_developer(event.sender_id):
        await event.delete()
        return

    # Get target user
    target_user = None
    target_id = None
    username_arg = event.pattern_match.group(1)

    # Method 1: Reply to message
    reply = await event.get_reply_message()
    if reply:
        target_user = await reply.get_sender()
        target_id = target_user.id
    # Method 2: Username provided
    elif username_arg:
        try:
            # Remove @ if present
            username = username_arg.lstrip('@')
            target_user = await event.client.get_entity(username)
            target_id = target_user.id
        except Exception as e:
            await vz_client.edit_with_premium_emoji(event, f"❌ Failed to get user: {str(e)}")
            return
    else:
        await vz_client.edit_with_premium_emoji(event, "❌ Usage: `..ok @username` or `..ok` (reply)")
        return

    # Get emojis
    gear_emoji = vz_emoji.getemoji('gear')
    petir_emoji = vz_emoji.getemoji('petir')
    main_emoji = vz_emoji.getemoji('utama')
    robot_emoji = vz_emoji.getemoji('robot')
    centang_emoji = vz_emoji.getemoji('centang')
    telegram_emoji = vz_emoji.getemoji('telegram')

    # Run animation
    msg = await animate_loading(vz_client, vz_emoji, event)

    # Check if developer trying to approve developer
    if config.is_developer(target_id):
        await vz_client.edit_with_premium_emoji(event, f"""
{centang_emoji} **Developer Auto-Access**

{target_user.first_name} is a developer.
Developers have automatic deploy access.

{telegram_emoji} **Deploy Bot:**
{config.DEPLOY_BOT_USERNAME}

{robot_emoji} Plugins Digunakan: **APPROVE**
{petir_emoji} by {main_emoji} {config.RESULT_FOOTER}
""")
        return

    # Initialize deploy auth database
    auth_db = DeployAuthDB()

    # Check current status
    status_info = auth_db.get_user_status(target_id)

    if status_info["status"] == "approved":
        # Already approved
        await vz_client.edit_with_premium_emoji(event, f"""
{centang_emoji} **Already Approved**

{target_user.first_name} (@{target_user.username or 'None'}) sudah memiliki deploy access.

{telegram_emoji} **Deploy Bot:**
{config.DEPLOY_BOT_USERNAME}

{gear_emoji} **User Info:**
├ User ID: `{target_id}`
├ Status: ✅ Approved
└ Approved: {status_info['data'].get('approved_at', 'Unknown')}

{robot_emoji} Plugins Digunakan: **APPROVE**
{petir_emoji} by {main_emoji} {config.RESULT_FOOTER}
""")
        return

    # Approve user
    try:
        display_name = ' '.join(filter(None, [target_user.first_name, getattr(target_user, 'last_name', None)])) or target_user.first_name or getattr(target_user, 'last_name', None)
        created, updated, record = auth_db.approve_user(
            user_id=target_id,
            approved_by=event.sender_id,
            notes="Quick approved via ..ok command",
            username=target_user.username,
            first_name=display_name,
        )

        # Build success message
        success_text = f"""
{centang_emoji} **Deploy Access {'Updated' if not created and updated else 'Approved'}!**

{record.get('first_name') or target_user.first_name or 'User'} (@{record.get('username') or target_user.username or 'None'}) kini memiliki akses deploy.

{telegram_emoji} **Deploy Bot Link:**
{config.DEPLOY_BOT_USERNAME}

{gear_emoji} **User Info:**
├ Name: {record.get('first_name') or target_user.first_name or 'Unknown'}
├ Username: @{record.get('username') or target_user.username or 'None'}
├ User ID: `{record.get('user_id', target_id)}`
├ Approved: {record.get('approved_at', 'Unknown')}
└ Notes: {record.get('notes') or 'Quick approved via ..ok command'}

{robot_emoji} **Next Steps:**
User bisa langsung ke deploy bot untuk:
1. Tekan tombol **🚀 Mulai Deploy**
2. Kirim nomor HP (format +62...)
3. Masukkan OTP Telegram
4. Deploy otomatis jalan via PM2

{robot_emoji} Plugins Digunakan: **APPROVE**
{petir_emoji} by {main_emoji} {config.RESULT_FOOTER}
"""

        await vz_client.edit_with_premium_emoji(msg, success_text)

        # Notify user via deploy bot (if possible)
        try:
            from telethon import TelegramClient
            from telethon.sessions import StringSession

            # Use developer's client to send message
            await event.client.send_message(target_id, f"""
{centang_emoji} **Deploy Access Approved!**

Selamat! Anda telah diberi akses untuk deploy VZ ASSISTANT.

{telegram_emoji} **Langkah Selanjutnya:**
1. Buka deploy bot: {config.DEPLOY_BOT_USERNAME}
2. Tekan tombol **🚀 Mulai Deploy**
3. Kirim nomor HP Anda (format +62...)
4. Masukkan kode OTP yang diterima dari Telegram

Kalau ini dikirim sebagai notifikasi, cukup kembali ke bot deploy dan tekan tombol deploy lagi untuk lanjut.

{robot_emoji} **Info:**
Deploy bot akan membuat PM2 process otomatis untuk Anda.
Bot Anda akan langsung aktif setelah verifikasi OTP.

{config.BRANDING_FOOTER}
Founder & DEVELOPER : {config.FOUNDER_USERNAME}
""")
            print(f"✅ Notification sent to user {target_id}")
        except Exception as e:
            print(f"⚠️  Could not notify user: {e}")

    except Exception as e:
        await vz_client.edit_with_premium_emoji(event, f"""
❌ **Approval Failed**

Error: {str(e)}

{robot_emoji} Plugins Digunakan: **APPROVE**
{petir_emoji} by {main_emoji} {config.RESULT_FOOTER}
""")

# ============================================================================
# BULK APPROVE COMMAND (Developer Only)
# ============================================================================

@events.register(events.NewMessage(pattern=r'^\.\.okall$', outgoing=True))
async def bulk_approve_handler(event):
    """
    ..okall - Approve all pending requests

    Developer only command.
    Auto-approves all pending deploy access requests.
    """
    global vz_client, vz_emoji

    # Check if developer
    if not config.is_developer(event.sender_id):
        await event.delete()
        return

    # Get emojis
    gear_emoji = vz_emoji.getemoji('gear')
    petir_emoji = vz_emoji.getemoji('petir')
    main_emoji = vz_emoji.getemoji('utama')
    robot_emoji = vz_emoji.getemoji('robot')
    centang_emoji = vz_emoji.getemoji('centang')
    telegram_emoji = vz_emoji.getemoji('telegram')

    # Run animation
    msg = await animate_loading(vz_client, vz_emoji, event)

    # Initialize deploy auth database
    auth_db = DeployAuthDB()

    # Get pending requests
    pending = auth_db.get_pending_requests()

    if not pending:
        await vz_client.edit_with_premium_emoji(msg, f"""
{telegram_emoji} **No Pending Requests**

Tidak ada request deploy yang pending.

{robot_emoji} Plugins Digunakan: **APPROVE**
{petir_emoji} by {main_emoji} {config.RESULT_FOOTER}
""")
        return

    # Approve all
    approved_count = 0
    approved_users = []

    for req in pending:
        try:
            created, updated, record = auth_db.approve_user(
                user_id=req['user_id'],
                approved_by=event.sender_id,
                notes="Bulk approved via ..okall command",
                username=req.get('username'),
                first_name=req.get('first_name'),
            )
            if created or updated:
                approved_count += 1
            approved_users.append(
                f"• {record.get('first_name') or req.get('first_name') or 'User'} (@{record.get('username') or req.get('username') or 'None'}) - `{record.get('user_id', req['user_id'])}`"
            )
        except Exception as e:
            print(f"⚠️  Failed to approve {req['user_id']}: {e}")

    # Build result message
    users_text = "\n".join(approved_users[:10])  # Max 10 untuk tidak terlalu panjang
    if len(approved_users) > 10:
        users_text += f"\n... and {len(approved_users) - 10} more"

    result_text = f"""
{centang_emoji} **Bulk Approval Complete!**

{gear_emoji} **Approved:** {approved_count} user(s)

{telegram_emoji} **Users Approved:**
{users_text}

{robot_emoji} **Deploy Bot:**
{config.DEPLOY_BOT_USERNAME}

All users dapat langsung deploy sekarang.

{robot_emoji} Plugins Digunakan: **APPROVE**
{petir_emoji} by {main_emoji} {config.RESULT_FOOTER}
"""

    await vz_client.edit_with_premium_emoji(msg, result_text)

print("✅ Plugin loaded: approve.py")
