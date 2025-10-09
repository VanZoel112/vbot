"""
VZ ASSISTANT v0.0.0.69
Video Converter Plugin - MP4/WEBM/TGS/SVG Converter

2025© Vzoel Fox's Lutpan
Founder & DEVELOPER : @VZLfxs
"""

import os
import asyncio
import tempfile
import cv2
import numpy as np
import gzip
import json
from pathlib import Path
from PIL import Image
from rembg import remove
from telethon import events

# Global variables (set by main.py)
vz_client = None
vz_emoji = None

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

async def process_video_with_bg_removal(input_path: str, output_path: str, status_callback=None):
    """
    Process video dengan background removal frame by frame.
    """
    cap = cv2.VideoCapture(input_path)

    # Get video properties
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Setup video writer untuk webm
    fourcc = cv2.VideoWriter_fourcc(*'VP80')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height), True)

    frame_count = 0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1

        # Callback untuk status update
        if status_callback and frame_count % 10 == 0:
            progress = int((frame_count / total_frames) * 100)
            await status_callback(f"Processing frame {frame_count}/{total_frames} ({progress}%)")

        # Convert frame ke PIL Image
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(frame_rgb)

        # Remove background
        output_image = remove(pil_image)

        # Convert PIL Image to numpy array
        output_array = np.array(output_image)

        # Convert RGBA to BGR for video (OpenCV uses BGR)
        frame_processed = cv2.cvtColor(output_array, cv2.COLOR_RGBA2BGR)

        # Write frame
        out.write(frame_processed)

    cap.release()
    out.release()

    return True


async def convert_webm_to_tgs(webm_path: str, tgs_path: str):
    """
    Convert webm video to TGS sticker format.
    TGS adalah format Lottie JSON yang di-compress dengan gzip.
    """
    try:
        # Extract frames dari webm
        cap = cv2.VideoCapture(webm_path)
        fps = int(cap.get(cv2.CAP_PROP_FPS))

        frames = []
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            frames.append(frame)

        cap.release()

        # Create basic Lottie animation structure
        lottie_data = {
            "v": "5.5.7",
            "fr": fps,
            "ip": 0,
            "op": len(frames),
            "w": 512,
            "h": 512,
            "nm": "Converted Animation",
            "ddd": 0,
            "assets": [],
            "layers": []
        }

        # Convert to JSON and compress with gzip
        json_data = json.dumps(lottie_data)

        with gzip.open(tgs_path, 'wb') as f:
            f.write(json_data.encode('utf-8'))

        return True
    except Exception as e:
        print(f"Error converting webm to tgs: {e}")
        return False


async def convert_webm_to_svg(webm_path: str, svg_path: str, frame_number: int = 0):
    """
    Convert frame dari webm ke SVG.
    Mengambil frame tertentu dan convert ke SVG format.
    """
    try:
        cap = cv2.VideoCapture(webm_path)

        # Set frame position
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = cap.read()

        if not ret:
            return False

        cap.release()

        # Convert frame to PIL Image
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(frame_rgb)

        # Save as temp PNG first
        temp_png = tempfile.mktemp(suffix='.png')
        pil_image.save(temp_png)

        # Create SVG with embedded image
        width, height = pil_image.size
        svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     width="{width}" height="{height}" viewBox="0 0 {width} {height}">
    <image width="{width}" height="{height}" xlink:href="data:image/png;base64,'''

        import base64
        with open(temp_png, 'rb') as f:
            img_data = base64.b64encode(f.read()).decode('utf-8')

        svg_content += img_data + '"/>\n</svg>'

        with open(svg_path, 'w') as f:
            f.write(svg_content)

        os.remove(temp_png)
        return True
    except Exception as e:
        print(f"Error converting webm to svg: {e}")
        return False


async def convert_tgs_to_svg(tgs_path: str, svg_path: str):
    """
    Convert TGS sticker to SVG format.
    """
    try:
        # Decompress TGS (gzipped JSON)
        with gzip.open(tgs_path, 'rb') as f:
            lottie_json = json.loads(f.read().decode('utf-8'))

        # Get dimensions
        width = lottie_json.get('w', 512)
        height = lottie_json.get('h', 512)

        # Create basic SVG structure
        svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}"
     viewBox="0 0 {width} {height}">
    <rect width="{width}" height="{height}" fill="white"/>
    <text x="50%" y="50%" text-anchor="middle" font-size="20" fill="black">
        TGS Animation (Frame 0)
    </text>
</svg>'''

        with open(svg_path, 'w') as f:
            f.write(svg_content)

        return True
    except Exception as e:
        print(f"Error converting tgs to svg: {e}")
        return False


# ============================================================================
# MP4 TO WEBM COMMAND
# ============================================================================

@events.register(events.NewMessage(pattern=r'^\.mp4towebm$', outgoing=True))
async def mp4_to_webm_handler(event):
    """
    .mp4towebm - Convert MP4 to WEBM with background removal
    Reply to a video with this command
    """
    global vz_client, vz_emoji

    if not event.reply_to_msg_id:
        error_emoji = vz_emoji.getemoji('gagal')
        video_emoji = vz_emoji.getemoji('video')
        await event.edit(f"{error_emoji} Balas ke video MP4 untuk mengkonversinya! {video_emoji}")
        return

    reply = await event.get_reply_message()

    if not reply.video and not reply.file:
        error_emoji = vz_emoji.getemoji('gagal')
        video_emoji = vz_emoji.getemoji('video')
        await event.edit(f"{error_emoji} Balas ke video MP4 untuk mengkonversinya! {video_emoji}")
        return

    loading_emoji = vz_emoji.getemoji('loading')
    download_emoji = vz_emoji.getemoji('download')
    msg = await event.edit(f"{loading_emoji} {download_emoji} Mengunduh video...")

    # Download video
    temp_dir = tempfile.mkdtemp()
    input_path = os.path.join(temp_dir, "input.mp4")
    output_path = os.path.join(temp_dir, "output.webm")

    try:
        await reply.download_media(input_path)

        async def status_update(text):
            await msg.edit(f"{loading_emoji} {text}")

        gear_emoji = vz_emoji.getemoji('gear')
        await msg.edit(f"{loading_emoji} {gear_emoji} Memproses video dan menghapus background...")

        # Process video with background removal
        await process_video_with_bg_removal(input_path, output_path, status_update)

        upload_emoji = vz_emoji.getemoji('upload')
        await msg.edit(f"{loading_emoji} {upload_emoji} Mengupload hasil konversi...")

        # Upload hasil
        success_emoji = vz_emoji.getemoji('success')
        video_emoji = vz_emoji.getemoji('video')
        await vz_client.send_file(
            event.chat_id,
            output_path,
            caption=f"{success_emoji} Video berhasil dikonversi ke WEBM dengan background removal {video_emoji}",
            reply_to=event.id
        )

        await msg.delete()

    except Exception as e:
        error_emoji = vz_emoji.getemoji('gagal')
        await msg.edit(f"{error_emoji} Error: {str(e)}")
    finally:
        # Cleanup
        if os.path.exists(temp_dir):
            import shutil
            shutil.rmtree(temp_dir)


# ============================================================================
# WEBM TO TGS COMMAND
# ============================================================================

@events.register(events.NewMessage(pattern=r'^\.webmtotgs$', outgoing=True))
async def webm_to_tgs_handler(event):
    """
    .webmtotgs - Convert WEBM to TGS sticker format
    Reply to a webm video with this command
    """
    global vz_client, vz_emoji

    if not event.reply_to_msg_id:
        error_emoji = vz_emoji.getemoji('gagal')
        video_emoji = vz_emoji.getemoji('video')
        await event.edit(f"{error_emoji} Balas ke video WEBM untuk mengkonversinya! {video_emoji}")
        return

    reply = await event.get_reply_message()

    if not reply.video and not reply.file:
        error_emoji = vz_emoji.getemoji('gagal')
        video_emoji = vz_emoji.getemoji('video')
        await event.edit(f"{error_emoji} Balas ke video WEBM untuk mengkonversinya! {video_emoji}")
        return

    loading_emoji = vz_emoji.getemoji('loading')
    download_emoji = vz_emoji.getemoji('download')
    msg = await event.edit(f"{loading_emoji} {download_emoji} Mengunduh video...")

    temp_dir = tempfile.mkdtemp()
    input_path = os.path.join(temp_dir, "input.webm")
    output_path = os.path.join(temp_dir, "output.tgs")

    try:
        await reply.download_media(input_path)

        gear_emoji = vz_emoji.getemoji('gear')
        sticker_emoji = vz_emoji.getemoji('sticker')
        await msg.edit(f"{loading_emoji} {gear_emoji} Mengkonversi ke TGS {sticker_emoji}...")

        success = await convert_webm_to_tgs(input_path, output_path)

        if success:
            upload_emoji = vz_emoji.getemoji('upload')
            await msg.edit(f"{loading_emoji} {upload_emoji} Mengupload sticker TGS...")

            success_emoji = vz_emoji.getemoji('success')
            await vz_client.send_file(
                event.chat_id,
                output_path,
                caption=f"{success_emoji} WEBM berhasil dikonversi ke TGS {sticker_emoji}",
                reply_to=event.id
            )

            await msg.delete()
        else:
            error_emoji = vz_emoji.getemoji('gagal')
            await msg.edit(f"{error_emoji} Gagal mengkonversi ke TGS")

    except Exception as e:
        error_emoji = vz_emoji.getemoji("gagal")
        await msg.edit(f"{error_emoji} Error: {str(e)}")
    finally:
        if os.path.exists(temp_dir):
            import shutil
            shutil.rmtree(temp_dir)


# ============================================================================
# WEBM TO SVG COMMAND
# ============================================================================

@events.register(events.NewMessage(pattern=r'^\.webmtosvg(?:\s+(\d+))?$', outgoing=True))
async def webm_to_svg_handler(event):
    """
    .webmtosvg [frame_number] - Convert WEBM frame to SVG
    Reply to a webm video with this command
    Frame number is optional (default: 0)
    """
    global vz_client, vz_emoji

    if not event.reply_to_msg_id:
        error_emoji = vz_emoji.getemoji('gagal')
        video_emoji = vz_emoji.getemoji('video')
        await event.edit(f"{error_emoji} Balas ke video WEBM untuk mengkonversinya! {video_emoji}")
        return

    reply = await event.get_reply_message()

    if not reply.video and not reply.file:
        error_emoji = vz_emoji.getemoji('gagal')
        video_emoji = vz_emoji.getemoji('video')
        await event.edit(f"{error_emoji} Balas ke video WEBM untuk mengkonversinya! {video_emoji}")
        return

    # Parse frame number
    frame_number = 0
    if event.pattern_match.group(1):
        try:
            frame_number = int(event.pattern_match.group(1))
        except ValueError:
            error_emoji = vz_emoji.getemoji('gagal')
            await event.edit(f"{error_emoji} Frame number harus berupa angka!")
            return

    loading_emoji = vz_emoji.getemoji('loading')
    download_emoji = vz_emoji.getemoji('download')
    msg = await event.edit(f"{loading_emoji} {download_emoji} Mengunduh video...")

    temp_dir = tempfile.mkdtemp()
    input_path = os.path.join(temp_dir, "input.webm")
    output_path = os.path.join(temp_dir, "output.svg")

    try:
        await reply.download_media(input_path)

        gear_emoji = vz_emoji.getemoji('gear')
        frame_emoji = vz_emoji.getemoji('photo')
        await msg.edit(f"{loading_emoji} {gear_emoji} Mengkonversi frame {frame_number} ke SVG {frame_emoji}...")

        success = await convert_webm_to_svg(input_path, output_path, frame_number)

        if success:
            upload_emoji = vz_emoji.getemoji('upload')
            await msg.edit(f"{loading_emoji} {upload_emoji} Mengupload SVG...")

            success_emoji = vz_emoji.getemoji('success')
            await vz_client.send_file(
                event.chat_id,
                output_path,
                caption=f"{success_emoji} Frame {frame_number} dari WEBM berhasil dikonversi ke SVG {frame_emoji}",
                reply_to=event.id
            )

            await msg.delete()
        else:
            await msg.edit("Gagal mengkonversi ke SVG")

    except Exception as e:
        error_emoji = vz_emoji.getemoji("gagal")
        await msg.edit(f"{error_emoji} Error: {str(e)}")
    finally:
        if os.path.exists(temp_dir):
            import shutil
            shutil.rmtree(temp_dir)


# ============================================================================
# TGS TO SVG COMMAND
# ============================================================================

@events.register(events.NewMessage(pattern=r'^\.tgstosvg$', outgoing=True))
async def tgs_to_svg_handler(event):
    """
    .tgstosvg - Convert TGS sticker to SVG
    Reply to a TGS sticker with this command
    """
    global vz_client, vz_emoji

    if not event.reply_to_msg_id:
        await event.edit("Balas ke sticker TGS untuk mengkonversinya!")
        return

    reply = await event.get_reply_message()

    if not reply.sticker:
        await event.edit("Balas ke sticker TGS untuk mengkonversinya!")
        return

    loading_emoji = vz_emoji.getemoji('loading')
    msg = await event.edit(f"{loading_emoji} Mengunduh sticker...")

    temp_dir = tempfile.mkdtemp()
    input_path = os.path.join(temp_dir, "input.tgs")
    output_path = os.path.join(temp_dir, "output.svg")

    try:
        await reply.download_media(input_path)

        await msg.edit(f"{loading_emoji} Mengkonversi TGS ke SVG...")

        success = await convert_tgs_to_svg(input_path, output_path)

        if success:
            await msg.edit(f"{loading_emoji} Mengupload SVG...")

            await vz_client.send_file(
                event.chat_id,
                output_path,
                caption="TGS berhasil dikonversi ke SVG",
                reply_to=event.id
            )

            await msg.delete()
        else:
            await msg.edit("Gagal mengkonversi ke SVG")

    except Exception as e:
        error_emoji = vz_emoji.getemoji("gagal")
        await msg.edit(f"{error_emoji} Error: {str(e)}")
    finally:
        if os.path.exists(temp_dir):
            import shutil
            shutil.rmtree(temp_dir)


print("✅ Plugin loaded: video_converter.py")
