"""
VZ ASSISTANT v0.0.0.69
Payment Plugin - Payment Information Management

2025© Vzoel Fox's Lutpan
Founder & DEVELOPER : @VZLfxs
"""

from telethon import events, Button
import config
from database.models import DatabaseManager

# Global variables (set by main.py)
vz_client = None
vz_emoji = None

# ============================================================================
# GET PAYMENT INFO COMMAND
# ============================================================================

@events.register(events.NewMessage(pattern=r'^\.get$', outgoing=True))
async def get_handler(event):
    global vz_client, vz_emoji

    """
    .get - Display payment information

    Shows all saved payment methods (max 3)
    and QR code if available.
    """
    user_id = event.sender_id

    # Get payment info from database
    db = DatabaseManager(config.get_sudoer_db_path(user_id))
    payments = db.get_payment_info(user_id)
    db.close()

    if not payments:
        await event.edit(f"""
ℹ️ **No Payment Information**

Use `.setget` (reply to message) to add payment info

**Format:**
EWALLET/BANK      :
NOMOR REKENING :
ATAS NAMA             :

{config.BRANDING_FOOTER} PAYMENT
""")
        return

    # Build payment info text
    payment_text = f"""
💳 **PAYMENT INFORMATION**

"""

    for i, payment in enumerate(payments, 1):
        if payment.qr_file_id:
            payment_text += f"**QR CODE:** Available ✅\n\n"
        else:
            payment_text += f"""**Method {i}:**
{payment.payment_type}      :
NOMOR REKENING : {payment.account_number}
ATAS NAMA             : {payment.account_name}

"""

    payment_text += f"""
{config.BRANDING_FOOTER} PAYMENT
Founder & DEVELOPER : {config.FOUNDER_USERNAME}
"""

    # Send QR code if available
    qr_payment = [p for p in payments if p.qr_file_id]
    if qr_payment and qr_payment[0].qr_file_id:
        try:
            await event.client.send_file(
                event.chat_id,
                qr_payment[0].qr_file_id,
                caption=payment_text
            )
            await event.delete()
        except:
            await event.edit(payment_text)
    else:
        await event.edit(payment_text)

# ============================================================================
# SET PAYMENT INFO COMMAND
# ============================================================================

@events.register(events.NewMessage(pattern=r'^\.setget$', outgoing=True))
async def setget_handler(event):
    global vz_client, vz_emoji

    """
    .setget - Add payment information

    Usage:
        .setget (reply to formatted message)

    Format:
    EWALLET/BANK      :
    NOMOR REKENING :
    ATAS NAMA             :

    Max 3 payment methods.
    """
    user_id = event.sender_id

    # Check if replying
    reply = await event.get_reply_message()
    if not reply or not reply.text:
        await event.edit(f"""
❌ **Reply to a message** with payment info

**Format:**
```
EWALLET/BANK      : DANA
NOMOR REKENING : 08123456789
ATAS NAMA             : John Doe
```

{config.BRANDING_FOOTER} PAYMENT
""")
        return

    # Parse payment info
    lines = reply.text.strip().split('\n')

    payment_type = None
    account_number = None
    account_name = None

    for line in lines:
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip().upper()
            value = value.strip()

            if 'EWALLET' in key or 'BANK' in key:
                payment_type = value
            elif 'NOMOR' in key or 'REKENING' in key:
                account_number = value
            elif 'NAMA' in key:
                account_name = value

    if not all([payment_type, account_number, account_name]):
        await event.edit("❌ Invalid format! Make sure all fields are filled.")
        return

    # Save to database
    db = DatabaseManager(config.get_sudoer_db_path(user_id))

    success = db.add_payment_info(
        user_id=user_id,
        payment_type=payment_type,
        account_number=account_number,
        account_name=account_name
    )

    if not success:
        db.close()
        await event.edit(f"""
❌ **Maximum Limit Reached**

You can only save up to {config.MAX_PAYMENT_INFO} payment methods.

{config.BRANDING_FOOTER} PAYMENT
""")
        return

    payments_count = len(db.get_payment_info(user_id))
    db.close()

    result_text = f"""
✅ **Payment Info Added**

**📋 Details:**
├ Type: {payment_type}
├ Account: {account_number}
└ Name: {account_name}

**📊 Total Methods:** {payments_count}/{config.MAX_PAYMENT_INFO}

Use `.get` to view all payment info

{config.BRANDING_FOOTER} PAYMENT
Founder & DEVELOPER : {config.FOUNDER_USERNAME}
"""

    await event.edit(result_text)

# ============================================================================
# SET QR CODE COMMAND
# ============================================================================

@events.register(events.NewMessage(pattern=r'^\.getqr$', outgoing=True))
async def getqr_handler(event):
    global vz_client, vz_emoji

    """
    .getqr - Set QR code for payment

    Usage:
        .getqr (reply to QR code image)

    Auto-extracts file_id and saves it.
    """
    user_id = event.sender_id

    # Check if replying to photo
    reply = await event.get_reply_message()
    if not reply or not reply.photo:
        await event.edit("""
❌ **Reply to a QR code image**

The image should contain your payment QR code.

💡 Supported: Photos only

{config.BRANDING_FOOTER} PAYMENT
""")
        return

    await event.edit("📷 Extracting QR code...")

    # Get file ID
    file_id = str(reply.photo.id)

    # Save to database
    db = DatabaseManager(config.get_sudoer_db_path(user_id))
    db.set_payment_qr(user_id, file_id)
    db.close()

    result_text = f"""
✅ **QR Code Saved**

**📷 File ID:** `{file_id}`

Your QR code will be shown when using `.get` command.

{config.BRANDING_FOOTER} PAYMENT
Founder & DEVELOPER : {config.FOUNDER_USERNAME}
"""

    await event.edit(result_text)

print("✅ Plugin loaded: payment.py")
