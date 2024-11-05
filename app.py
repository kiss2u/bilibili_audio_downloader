from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from yt_dlp import YoutubeDL
import os
import re
import logging
import sys

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class CustomLogger:
    def __init__(self, sid):
        self.sid = sid

    def debug(self, msg):
        logging.debug(msg)

    def warning(self, msg):
        logging.warning(msg)

    def error(self, msg):
        logging.error(msg)

    def info(self, msg):
        socketio.emit('download_progress', {'message': msg}, room=self.sid)

def progress_hook(d, sid):
    if d['status'] == 'downloading':
        message = f"\rDownloading: {d['_percent_str']} at {d['_speed_str']}"
        socketio.emit('download_progress', {'message': message}, room=sid)
        sys.stdout.flush()

def download_audio(url, output_dir, number, check=False, max_retries=3, sid=None):
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
        'logger': CustomLogger(sid),
        'progress_hooks': [lambda d: progress_hook(d, sid)],
    }

    retries = 0
    while retries <= max_retries:
        try:
            with YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=True)
            actual_filename = os.path.basename(info_dict['requested_downloads'][0]['filepath'])
            break
        except Exception as e:
            if retries < max_retries:
                retries += 1
                logging.info(f"下载失败，正在进行第{retries}/{max_retries}次重试...")
            else:
                raise e

    return f"音频已下载到'{new_output_dir}'目录下，并以'{actual_filename}'命名。"

@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()
    url = data.get('url')
    output_dir = data.get('output_dir')
    number = int(data.get('number', 1))
    check = data.get('check', False)
    sid = request.sid

    results = []
    for i in range(1, number + 1):
        url_with_param = f"{url}?p={i}"
        result = download_audio(url_with_param, output_dir, i, check, sid=sid)
        results.append(result)
        if "No such playlist" in result:
            break

    return jsonify(results)

@app.route('/')
def home():
    return app.send_static_file('index.html')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8080, debug=True)
