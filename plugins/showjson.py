"""
VZ ASSISTANT v0.0.0.69
ShowJSON Plugin - Metrics & Emoji Mapping Viewer

2025© Vzoel Fox's Lutpan
Founder & DEVELOPER : @VZLfxs
"""

from telethon import events, Button
import json
import os
import config
from helpers.inline import get_showjson_buttons

# Global variables (set by main.py)
vz_client = None
vz_emoji = None

# ============================================================================
# SHOWJSON COMMAND
# ============================================================================

@events.register(events.NewMessage(pattern=r'^\.showjson$', outgoing=True))
async def showjson_handler(event):
    global vz_client, vz_emoji

    """
    .showjson - Display metrics and emoji mapping data

    Shows:
    - Emoji premium ID mapping
    - File IDs from media
    - Usage metrics/statistics
    - JSON formatted output

    Auto-triggered by gcast, tagall for emoji conversion.
    """
    user_id = event.sender_id

    await vz_client.edit_with_premium_emoji(event, "📊 Loading data...")

    # Load emoji mapping
    emoji_data = config.load_emoji_mapping()

    if not emoji_data:
        await vz_client.edit_with_premium_emoji(event, "❌ Emoji mapping not found!")
        return

    # Build main menu
    main_text = f"""
📊 **SHOW JSON - Data Viewer**

**📋 Available Data:**

**🎨 Emoji Mapping**
├ Total Emojis: {emoji_data.get('metrics', {}).get('total_emojis', 0)}
├ Conversions: {emoji_data.get('metrics', {}).get('total_conversions', 0)}
└ Version: {emoji_data.get('version', 'Unknown')}

**📁 Categories:**
├ Identity: {len(emoji_data.get('categories', {}).get('identity', {}).get('emojis', []))}
├ System: {len(emoji_data.get('categories', {}).get('system', {}).get('emojis', []))}
├ Status: {len(emoji_data.get('categories', {}).get('status', {}).get('emojis', []))}
├ Communication: {len(emoji_data.get('categories', {}).get('communication', {}).get('emojis', []))}
├ Process: {len(emoji_data.get('categories', {}).get('process', {}).get('emojis', []))}
└ Special: {len(emoji_data.get('categories', {}).get('special', {}).get('emojis', []))}

**💡 Select option below to view details**

{config.BRANDING_FOOTER} SHOWJSON
Founder & DEVELOPER : {config.FOUNDER_USERNAME}
"""

    # Create buttons
    buttons = [
        [
            Button.inline("📊 Metrics", b"json_metrics"),
            Button.inline("🎨 Emojis", b"json_emojis")
        ],
        [
            Button.inline("📁 Categories", b"json_categories"),
            Button.inline("🔧 Raw JSON", b"json_raw")
        ],
        [Button.inline("❌ Close", b"json_close")]
    ]

    try:
        await event.edit(main_text, buttons=buttons)
    except:
        await vz_client.edit_with_premium_emoji(event, main_text)

# ============================================================================
# CALLBACK HANDLERS
# ============================================================================

@events.register(events.CallbackQuery(pattern=b"json_metrics"))
async def json_metrics_callback(event):
    global vz_client, vz_emoji

    """Show metrics data."""
    emoji_data = config.load_emoji_mapping()
    metrics = emoji_data.get('metrics', {})

    metrics_text = f"""
📊 **EMOJI METRICS**

**📈 Statistics:**
├ Total Emojis: {metrics.get('total_emojis', 0)}
├ Total Conversions: {metrics.get('total_conversions', 0)}
├ Last Conversion: {metrics.get('last_conversion', 'Never')}
└ Most Used: {metrics.get('most_used_emoji', 'N/A')}

**ℹ️ Version:**
└ {emoji_data.get('version', 'Unknown')} ({emoji_data.get('last_updated', 'Unknown')})

**📝 Description:**
{emoji_data.get('description', 'Premium emoji mapping for VZ ASSISTANT')}

{config.BRANDING_FOOTER} SHOWJSON
"""

    buttons = [
        [Button.inline("◀️ Back", b"json_back")],
        [Button.inline("❌ Close", b"json_close")]
    ]

    try:
        await event.edit(metrics_text, buttons=buttons)
    except:
        await vz_client.edit_with_premium_emoji(event, metrics_text)

    await event.answer()

@events.register(events.CallbackQuery(pattern=b"json_emojis"))
async def json_emojis_callback(event):
    global vz_client, vz_emoji

    """Show emoji list."""
    emoji_data = config.load_emoji_mapping()
    emoji_names = emoji_data.get('emoji_names', {})

    emojis_text = f"""
🎨 **EMOJI MAPPING - {len(emoji_names)} Emojis**

**📋 Available Emojis:**

"""

    for name, emoji in emoji_names.items():
        emoji_id = emoji_data.get('emoji_mapping', {}).get(emoji, 'Unknown')
        emojis_text += f"**{name}**\n"
        emojis_text += f"├ Emoji: {emoji}\n"
        emojis_text += f"└ ID: `{emoji_id}`\n\n"

    emojis_text += f"""
{config.BRANDING_FOOTER} SHOWJSON
"""

    buttons = [
        [Button.inline("◀️ Back", b"json_back")],
        [Button.inline("❌ Close", b"json_close")]
    ]

    try:
        await event.edit(emojis_text[:4096], buttons=buttons)  # Telegram limit
    except:
        await event.edit(emojis_text[:4096])

    await event.answer()

@events.register(events.CallbackQuery(pattern=b"json_categories"))
async def json_categories_callback(event):
    global vz_client, vz_emoji

    """Show categories."""
    emoji_data = config.load_emoji_mapping()
    categories = emoji_data.get('categories', {})

    cat_text = f"""
📁 **EMOJI CATEGORIES**

"""

    for cat_name, cat_data in categories.items():
        cat_text += f"**{cat_name.upper()}**\n"
        cat_text += f"├ Description: {cat_data.get('description', 'N/A')}\n"
        cat_text += f"└ Emojis: {', '.join(cat_data.get('emojis', []))}\n\n"

    cat_text += f"""
{config.BRANDING_FOOTER} SHOWJSON
"""

    buttons = [
        [Button.inline("◀️ Back", b"json_back")],
        [Button.inline("❌ Close", b"json_close")]
    ]

    try:
        await event.edit(cat_text, buttons=buttons)
    except:
        await vz_client.edit_with_premium_emoji(event, cat_text)

    await event.answer()

@events.register(events.CallbackQuery(pattern=b"json_raw"))
async def json_raw_callback(event):
    global vz_client, vz_emoji

    """Show raw JSON."""
    emoji_data = config.load_emoji_mapping()

    # Format JSON
    raw_json = json.dumps(emoji_data, indent=2, ensure_ascii=False)

    raw_text = f"""
🔧 **RAW JSON DATA**

```json
{raw_json[:3500]}
```

... (truncated)

**📁 Full file:**
`emojiprime.json`

{config.BRANDING_FOOTER} SHOWJSON
"""

    buttons = [
        [Button.inline("◀️ Back", b"json_back")],
        [Button.inline("❌ Close", b"json_close")]
    ]

    try:
        await event.edit(raw_text, buttons=buttons)
    except:
        await vz_client.edit_with_premium_emoji(event, raw_text)

    await event.answer()

@events.register(events.CallbackQuery(pattern=b"json_back"))
async def json_back_callback(event):
    global vz_client, vz_emoji

    """Go back to main menu."""
    # Trigger showjson again
    emoji_data = config.load_emoji_mapping()

    main_text = f"""
📊 **SHOW JSON - Data Viewer**

**📋 Available Data:**

**🎨 Emoji Mapping**
├ Total Emojis: {emoji_data.get('metrics', {}).get('total_emojis', 0)}
├ Conversions: {emoji_data.get('metrics', {}).get('total_conversions', 0)}
└ Version: {emoji_data.get('version', 'Unknown')}

**💡 Select option below to view details**

{config.BRANDING_FOOTER} SHOWJSON
"""

    buttons = [
        [
            Button.inline("📊 Metrics", b"json_metrics"),
            Button.inline("🎨 Emojis", b"json_emojis")
        ],
        [
            Button.inline("📁 Categories", b"json_categories"),
            Button.inline("🔧 Raw JSON", b"json_raw")
        ],
        [Button.inline("❌ Close", b"json_close")]
    ]

    try:
        await event.edit(main_text, buttons=buttons)
    except:
        await vz_client.edit_with_premium_emoji(event, main_text)

    await event.answer()

@events.register(events.CallbackQuery(pattern=b"json_close"))
async def json_close_callback(event):
    global vz_client, vz_emoji

    """Close showjson menu."""
    await event.delete()
    await event.answer("✅ JSON viewer closed")

print("✅ Plugin loaded: showjson.py")
