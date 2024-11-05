from yt_dlp import YoutubeDL
import os
import re

def download_audio(ws, url, output_dir, number, check=False, max_retries=3):
    base_dir = "/mnt/shares/audiobooks/"
    new_output_dir = os.path.join(base_dir, output_dir)
    os.makedirs(new_output_dir, exist_ok=True)
    
    preferred_format = 'm4a'

    if check:
        filename = '%(title)s.%(ext)s'
    else:
        title_pattern = re.compile(r'^(.*?)(\.m4a)?$')
        def format_title(title):
            match = title_pattern.match(title)
            if match and match.group(2):
                return match.group(1)
            else:
                return f"{title}.{preferred_format}"
        filename = f"{output_dir} - {number}.{preferred_format}"

    filepath = os.path.join(new_output_dir, filename)

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': preferred_format,
            'preferredquality': '192',
        }],
        'outtmpl': filepath,
        'noplaylist': True,
        'ignoreerrors': True,
        'download_archive': os.path.join(new_output_dir, '.downloaded_videos.txt'),
        'logger': CustomLogger(ws),
        'progress_hooks': [lambda d: progress_hook(ws, d)],
    }

    retries = 0
    while retries <= max_retries:
        try:
            with YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=True)
            actual_filename = os.path.basename(info_dict['requested'])
            ws.send(f"Download completed: {actual_filename}")
            break
        except Exception as e:
            ws.send(f"Error: {str(e)}")
            retries += 1
    else:
        ws.send("Max retries exceeded. Download failed.")
