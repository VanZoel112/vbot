# 🦊 VzoelFox Premium Emoji Usage (vbot)

Dokumen ini menjadi referensi utama untuk memahami cara kerja emoji premium di repo `vbot`. Panduan ini disusun berdasarkan struktur `emojiprime.json` terbaru serta menyiapkan dasar untuk helper emoji yang akan menyusul setelah dokumen ini dikaji.

---

## 1. Arsitektur Emoji Premium

Premium emoji disimpan dalam berkas [`emojiprime.json`](./emojiprime.json) dengan struktur berikut:

- `emoji_mapping` — pasangan **emoji unicode** → **custom emoji id Telegram**.
- `emoji_names` — alias resmi yang digunakan saat ini (huruf kapital & underscore).
- `categories` — pengelompokan emoji berdasarkan fungsi (identity, system, status, dll).
- `usage_mapping` — pola pemakaian default untuk command (`ping_latency`, `process_animation`, dll).
- `telegram_entities` — contoh payload `MessageEntityCustomEmoji` untuk setiap emoji.

Helper yang tersedia sekarang adalah `utils.emoji.build_premium_emoji_entities(text)`.
Fungsi ini mencari emoji pada string dan membangun daftar `MessageEntityCustomEmoji` agar Telethon bisa mengirim custom emoji premium tanpa memecah pesan menjadi beberapa edit.

```python
from utils.emoji import build_premium_emoji_entities

text = "🤩 Status aktif!"
entities = build_premium_emoji_entities(text)
await event.edit(text, formatting_entities=entities)

> Catatan: Untuk saat ini, helper di atas hanya men-scan emoji yang persis ada di emoji_mapping. Pastikan teks pesan menggunakan emoji yang terdaftar.




---

2. Alias Emoji: Kondisi Saat Ini & Rencana Baru

Alias huruf kapital pada emoji_names akan tetap dipertahankan untuk kompatibilitas internal. Namun, kita akan menambahkan alias snake_case agar konsisten dengan implementasi di repo vzl2. Tabel di bawah memetakan alias lama → emoji → custom id beserta alias rencana.

Alias Lama (emoji_names)	Emoji	Custom Emoji ID	Alias Baru yang Diusulkan	Kategori Utama

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


Rencana Implementasi Lanjutan

1. Helper Alias — Buat kelas PremiumEmojiManager yang memuat JSON, menyediakan getemoji('utama'), get_custom_id('utama'), format_response(['utama', 'petir'], text), dan fallback emoji non-premium.


2. Command Pattern Registry — Normalisasi struktur usage_mapping agar bisa dipanggil via get_command_emojis('ping') dan get_status_emojis('success') seperti pada repo vzl2.


3. Fallback & Validation — Tambahkan pengecekan untuk emoji yang belum terdaftar agar developer cepat tahu saat ada emoji baru di teks.



Dokumen ini akan menjadi acuan saat mengerjakan tiga poin di atas.


---

3. Contoh Pemakaian (Saat Ini)

Berikut alur yang sudah berjalan di plugin alive (serupa untuk ping):

from utils.emoji import build_premium_emoji_entities

text = "🤩 **Vz ASSISTANT**\n\n✅ System online"
entities = build_premium_emoji_entities(text)
await event.edit(text, formatting_entities=entities)

Langkah penting:

1. Gunakan emoji yang tercantum dalam tabel di atas.


2. Panggil build_premium_emoji_entities sebelum event.edit atau _edit_with_premium.


3. Hindari memasukkan emoji yang belum ada di emoji_mapping — akan tampil sebagai emoji biasa tanpa premium ID.




---

4. Checklist Integrasi Selanjutnya

Setelah dokumen ini disetujui:

[ ] Refactor helper emoji agar menyediakan API setara vzoel_emoji (alias snake_case).

[ ] Sesuaikan semua plugin untuk memakai helper baru dan alias hasil normalisasi.

[ ] Tambahkan test sederhana untuk memastikan semua emoji dalam tabel memiliki custom emoji id yang valid.



---

Referensi:

vzl2 EMOJI_USAGE.md sebagai baseline konsep.

emojiprime.json pada repo ini untuk data aktual.


🦊 Disusun untuk memudahkan migrasi emoji premium VzoelFox.



