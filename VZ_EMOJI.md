# 🦊 VzoelFox's Emoji Usage Guide

## Cara Menggunakan Emoji Premium di Plugin

### 1. Format Standar (Recommended)

```python
# Di plugin handler:
async def my_handler(event):
    global vz_client, vz_emoji
    
    # Menggunakan single emoji
    emoji = vz_emoji.get_emoji('utama')  # 🤩
    await event.edit(f"{emoji} Hello VzoelFox!")
    
    # Menggunakan multiple emojis
    response = vz_emoji.format_emoji_response(['utama', 'petir'], "Power activated!")
    await event.edit(response)  # 🤩⛈ Power activated!

2. Format getemoji() - Lebih Mudah

# Di plugin handler:
async def my_handler(event):
    global vz_client, vz_emoji
    
    # Cara yang lebih mudah dengan fallback otomatis
    emoji1 = vz_emoji.getemoji('utama')    # 🤩
    emoji2 = vz_emoji.getemoji('petir')    # ⛈
    emoji3 = vz_emoji.getemoji('unknown')  # 🔸 (fallback)
    
    message = f"{emoji1} VzoelFox {emoji2} Assistant is active!"
    await event.edit(message)

3. Format f-string Template (Paling Mudah)

# Di plugin handler:
async def my_handler(event):
    global vz_client, vz_emoji
    
    # Template yang mudah dibaca
    message = f"""
{vz_emoji.getemoji('utama')} **VzoelFox Status**

{vz_emoji.getemoji('centang')} System: Online
{vz_emoji.getemoji('aktif')} Plugins: {vz_client.stats['plugins_loaded']}
{vz_emoji.getemoji('petir')} Commands: {vz_client.stats['commands_executed']}

{vz_emoji.get_vz_signature()} **Ready to serve!**
    """.strip()
    
    await event.edit(message)

Emoji Mapping (vz_emoji)

Alias Lama	Emoji	Custom Emoji ID	Alias Baru (snake_case)	Kategori

MAIN_VZOEL	🤩	6156784006194009426	utama, signature_main	identity
DEVELOPER	👨‍💻	6206398094007863809	developer, owner_dev	identity
OWNER	🌟	6185812822564277027	owner, founder	identity
GEAR	⚙️	5794353925360457382	loading, gear	system
CHECKLIST	✅	5796280063573890402	centang, success	system
PETIR	⛈	5794407002566300853	petir, storm	system
HIJAU	👍	6098412711991841301	hijau, latency_good	status
KUNING	⚠️	6097951256410592079	kuning, latency_warn	status
MERAH	👎	6098107013399581475	merah, latency_bad	status
TELEGRAM	✉️	5350291836378307462	telegram, inbox	communication
CAMERA	📷	5451643289218342306	camera, photo	communication
PROSES_1	😈	5267186839130753795	proses1, anim_stage_1	process
PROSES_2	🔪	5267498988763891103	proses2, anim_stage_2	process
PROSES_3	😐	6100140315342016955	proses3, anim_stage_3	process
ROBOT	👨‍🚀	6221865220428532247	robot, space	special
LOADING	♾	6098417814412992289	infinite, loading_loop	special
NYALA	🎚	5794128499706958658	nyala, active	system


Command Emoji Patterns

# Pre-defined patterns untuk commands
alive_emojis = vz_emoji.get_command_emojis('alive')    # ['utama', 'active/nyala', 'petir']
ping_emojis  = vz_emoji.get_command_emojis('ping')     # ['loading', 'centang', 'active/nyala']
vz_emojis = vz_emoji.get_command_emojis('vzoel')    # ['utama', 'petir', 'proses1']

Status Emoji Indicators

# Pre-defined status patterns
success_emojis = vz_emoji.get_status_emojis('success') # ['centang', 'utama']
loading_emojis = vz_emoji.get_status_emojis('loading') # ['loading', 'infinite']
error_emojis   = vz_emoji.get_status_emojis('error')   # ['merah', 'petir']

VzoelFox's Signature

# Signature emoji combination
signature = vz_emoji.get_vz_signature()  # 🤩⛈😈

# Menggunakan dalam message
message = f"{signature} VzoelFox's Territory {signature}"

Custom Emoji Support

VzoelFox's Assistant mendukung custom emoji Telegram Premium:

# Get custom emoji ID
custom_id = vz_emoji.get_custom_emoji_id('utama')  # "6156784006194009426"

# Untuk advanced usage dengan Telethon DocumentAttributeCustomEmoji
from telethon.tl.types import DocumentAttributeCustomEmoji

# Note: Implementasi custom emoji memerlukan Telegram Premium

Best Practices

1. Selalu gunakan getemoji() untuk single emoji dengan fallback


2. Gunakan format_emoji_response() untuk multiple emoji


3. Gunakan signature di awal/akhir message penting


4. Konsisten dengan tema emoji per command


5. Test fallback untuk user non-premium



Example Plugin

@events.register(events.NewMessage(pattern=r'\.mystatus'))
async def my_status_handler(event):
    """Status command with VzoelFox emojis"""
    if event.is_private or event.sender_id == (await event.client.get_me()).id:
        global vz_client, vz_emoji
        
        # Animated loading
        msg = await event.edit(f"{vz_emoji.getemoji('loading')} Checking status...")
        await asyncio.sleep(1)
        
        # Final status
        signature = vz_emoji.get_vz_signature()
        status_msg = f"""
**{signature} My VzoelFox Status**

{vz_emoji.getemoji('utama')} **User:** {(await event.client.get_me()).first_name}
{vz_emoji.getemoji('active')} **Plugins:** {len(vz_client.plugin_manager.plugins)}
{vz_emoji.getemoji('centang')} **Status:** Active & Running
{vz_emoji.getemoji('telegram')} **Engine:** VzoelFox v2.0.0

**{vz_emoji.getemoji('petir')} Ready to dominate!**
        """.strip()
        
        await msg.edit(status_msg)
        vz_client.increment_command_count()


---

🦊 Created by VzoelFox's t.me/VZLfxs (Lutpan)

