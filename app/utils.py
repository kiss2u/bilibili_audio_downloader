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
            actual_filename = os.path.basename(info_dict['requested_downloads'][0]['filepath'])
            ws.send(f"音频已下载到'{new_output_dir}'目录下，并以'{actual_filename}'命名。")
            break
        except Exception as e:
            if retries < max_retries:
                retries += 1
                logging.info(f"下载失败，正在进行第{retries}/{max_retries}次重试...")
            else:
                ws.send("下载失败，请检查URL和网络连接。")
                raise e

class CustomLogger:
    def __init__(self, ws=None):
        self.ws = ws

    def debug(self, msg):
        logging.debug(msg)

    def warning(self, msg):
        logging.warning(msg)

    def error(self, msg):
        logging.error(msg)

def progress_hook(ws, d):
    if d['status'] == 'downloading':
        percent = d['_percent_str'].replace('%', '')
        try:
            ws.send(f"Downloading: {percent}%")
        except WebSocketError:
            pass
        sys.stdout.flush()
