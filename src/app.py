import os
from flask import Flask, request, jsonify, render_template
import threading
import asyncio
import websockets
from src.downloader import BilibiliDownloader
from src.models.queue import enqueue_task

print("Starting application...")  # 添加调试输出

# 从环境变量获取配置
DOWNLOAD_DIR = os.getenv('DOWNLOAD_DIR', '/mnt/shares/audiobooks')
print(f"Download directory: {DOWNLOAD_DIR}")  # 添加调试输出

app = Flask(__name__)
downloader = BilibiliDownloader(base_dir=DOWNLOAD_DIR)

@app.route('/')
def home():
    print("Accessing home page")  # 添加调试输出
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()
    url = data.get('url')
    output_dir = data.get('output_dir')
    number = int(data.get('number', 1))
    check = data.get('check', False)

    if enqueue_task(url, output_dir, number, check):
        def run_async():
            asyncio.run(downloader.process_queue())
        
        thread = threading.Thread(target=run_async)
        thread.start()
        
        return jsonify({"message": "任务已添加到队列，正在排队下载，请稍后查看进度。"})
    return jsonify({"message": "任务添加到队列失败，请检查相关配置或稍后重试。"}) 

if __name__ == '__main__':
    print("Running Flask app...")  # 添加调试输出
    app.run(host='0.0.0.0', port=5000) 