from flask import Flask, request, jsonify, render_template_string
from yt_dlp import YoutubeDL
import os
import re
import logging
import sys
import queue
import asyncio
import websockets

app = Flask(__name__)

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 任务队列
task_queue = queue.Queue()
download_progress_websockets = {}

class CustomLogger:
    def debug(self, msg):
        logging.debug(msg)

    def warning(self, msg):
        logging.warning(msg)

    def error(self, msg):
        logging.error(msg)

async def send_progress(websocket, progress):
    try:
        await websocket.send(progress)
    except websockets.ConnectionClosed:
        pass

def progress_hook(d):
    if d['status'] == 'downloading':
        task_id = d.get('task_id')
        if task_id and task_id in download_progress_websockets:
            progress_info = {
                'percent': d['_percent_str'],
                'speed': d.get('_speed_str', '未知'),
                'eta': d.get('_eta_str', '未知')
            }
            asyncio.run(send_progress(download_progress_websockets[task_id], 
                f"进度：{progress_info['percent']} | 速度：{progress_info['speed']} | 剩余时间：{progress_info['eta']}"))

def setup_download_options(url, output_dir, number, check=False, max_retries=3, audio_format='m4a', task_id=None):
    base_dir = "/mnt/shares/audiobooks/"
    new_output_dir = os.path.join(base_dir, output_dir)
    os.makedirs(new_output_dir, exist_ok=True)

    if check:
        filename = '%(title)s.%(ext)s'
    else:
        title_pattern = re.compile(r'^(.*?)(\.m4a)?$')
        def format_title(title):
            match = title_pattern.match(title)
            if match and match.group(2):
                return match.group(1)
            else:
                return f"{title}.{audio_format}"
        filename = f"{output_dir} - {number}.{audio_format}"

    filepath = os.path.join(new_output_dir, filename)

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': audio_format,
            'preferredquality': '192',
        }],
        'outtmpl': filepath,
        'noplaylist': True,
        'ignoreerrors': True,
        'download_archive': os.path.join(new_output_dir, '.downloaded_videos.txt'),
        'logger': CustomLogger(),
        'progress_hooks': [progress_hook],
        'task_id': task_id
    }
    return ydl_opts

async def download_audio(ydl, url, output_dir, number, check=False, max_retries=3):
    task_id = str(id(url))
    retries = 0
    websocket = None
    try:
        websocket = await websockets.connect('ws://localhost:8765')
        download_progress_websockets[task_id] = websocket

        while retries <= max_retries:
            try:
                info_dict = ydl.extract_info(url, download=True)
                actual_filename = os.path.basename(info_dict['requested_downloads'][0]['filepath'])
                break
            except Exception as e:
                if retries < max_retries:
                    retries += 1
                    logging.info(f"下载失败，正在进行第{retries}/{max_retries}次重试...")
                else:
                    raise e
    finally:
        if websocket:
            del download_progress_websockets[task_id]
            await websocket.close()

    return f"音频已下载到'{os.path.dirname(ydl.options['outtmpl'])}'目录下，并以'{actual_filename}'命名。"

def enqueue_download_task(url, output_dir, number, check=False):
    try:
        task_queue.put((url, output_dir, number, check))
        return True
    except queue.Full:
        logging.error("任务队列已满，无法添加新任务，请稍后再试。")
        return False

async def process_task_queue():
    try:
        websocket = await websockets.connect('ws://localhost:8765')
        while not task_queue.empty():
            task = task_queue.get()
            url, output_dir, number, check = task
            ydl = YoutubeDL(setup_download_options(url, output_dir, number, check))
            results = []
            for i in range(1, number + 1):
                url_with_param = f"{url}?p={i}"
                result = await download_audio(ydl, url_with_param, output_dir, i, check)
                results.append(result)
                if "No such playlist" in result:
                    break
            await websocket.send("\n".join(results))
            task_queue.task_done()
    except Exception as e:
        logging.error(f"处理任务队列出现异常：{str(e)}")
    finally:
        await websocket.close()

@app.route('/download', methods=['POST'])
async def download():
    data = request.get_json()
    url = data.get('url')
    output_dir = data.get('output_dir')
    number = int(data.get('number', 1))
    check = data.get('check', False)

    if enqueue_download_task(url, output_dir, number, check):
        asyncio.create_task(process_task_queue())
        return jsonify({"message": "任务已添加到队列，正在排队下载，请稍后查看进度。"})
    return jsonify({"message": "任务添加到队列失败，请检查相关配置或稍后重试。"})

@app.route('/')
def home():
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>BiliBili Audio Downloader</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
        <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    </head>
    <body class="container mt-5">
        <h1 class="text-center mb-4">BiliBili Audio Downloader</h1>
        <div class="alert alert-info" role="alert">
            当前排队任务数：<span id="queueCount">0</span>
            <button type="button" class="btn btn-sm btn-outline-info float-end" onclick="showHistory()">查看历史记录</button>
        </div>
        <div id="historyPanel" class="card mb-4" style="display: none;">
            <div class="card-header">
                下载历史记录
                <button type="button" class="btn-close float-end" onclick="hideHistory()"></button>
            </div>
            <div class="card-body">
                <ul id="historyList" class="list-group"></ul>
            </div>
        </div>
        <form id="downloadForm" class="mb-4">
            <div class="mb-3">
                <label for="url" class="form-label">视频 URL:</label>
                <input type="text" id="url" name="url" class="form-control" required>
            </div>
            <div class="mb-3">
                <label for="output_dir" class="form-label">输出目录:</label>
                <input type="text" id="output_dir" name="output_dir" class="form-control" required>
            </div>
            <div class="mb-3">
                <label for="number" class="form-label">循环次数:</label>
                <input type="number" id="number" name="number" value="1" class="form-control" required>
            </div>
            <div class="form-check mb-3">
                <input type="checkbox" id="check" name="check" class="form-check-input">
                <label for="check" class="form-check-label">是否保留原名</label>
            </div>
            <button type="button" onclick="startDownload()" class="btn btn-primary">开始下载</button>
            <button type="button" onclick="showConstructedUrlAndNumber()" class="btn btn-secondary">显示构造</button>
        </form>
        <div id="results" class="mb-4"></div>
        <div id="progress" class="mb-4"></div>
        <div id="constructedInfo" style="display:none;">
            <p>构造的新网址：<span id="constructedUrl"></span></p>
            <p>循环次数：<span id="constructedNumber"></span></p>
            <p>输出目录：<span id="constructedOutputDir"></span></p>
            <p>保留原名：<span id="constructedCheck"></span></p>
        </div>

        <script>
            var websocket;
            var queueCount = 0;

            function updateQueueCount() {
                $('#queueCount').text(queueCount);
            }

            function startDownload() {
                var url = $('#url').val();
                var output_dir = $('#output_dir').val();
                var number = parseInt($('#number').val(), 10);
                var check = $('#check').is(':checked');

                // 解析 URL 以获取 BVid
                var parsedUrl = new URL(url);
                var pathParts = parsedUrl.pathname.split('/');
                var BVid = pathParts[2];
                var newUrl = `https://www.bilibili.com/video/${BVid}`;
                $('#constructedUrl').text(newUrl);

                // 从查询字符串中获取 page
                var searchParams = new URLSearchParams(parsedUrl.search);
                var pageFromUrl = searchParams.get('p');
                if (pageFromUrl && !isNaN(pageFromUrl)) {
                    $('#number').val(pageFromUrl);
                    number = parseInt(pageFromUrl, 10);
                }

                $.ajax({
                    url: '/download',
                    type: 'POST',
                    contentType: 'application/json',
                    data: JSON.stringify({url: newUrl, output_dir: output_dir, number: number, check: check}),
                    success: function(response) {
                        queueCount++;
                        updateQueueCount();
                        $('#results').append('<p>' + response.message + '</p>');
                    },
                    error: function(error) {
                        console.error(error);
                    }
                });
            }

            function showConstructedUrlAndNumber() {
                var url = $('#url').val();
                var number = parseInt($('#number').val(), 10);
                var output_dir = $('#output_dir').val();
                var check = $('#check').is(':checked');

                // 解析 URL 以获取 BVid
                var parsedUrl = new URL(url);
                var pathParts = parsedUrl.pathname.split('/');
                var BVid = pathParts[2];
                var newUrl = `https://www.bilibili.com/video/${BVid}`;

                // 显示构造的新网址、循环次数和输出目录
                $('#constructedUrl').text(newUrl);
                $('#constructedNumber').text(!isNaN(number) ? number : "用户给定的数字");
                $('#constructedOutputDir').text(output_dir);
                $('#constructedCheck').text(check ? '已启用' : '未启用');

                $('#constructedInfo').css('display', 'block');
            }

            // 建立 websocket 连接
            websocket = new WebSocket('ws://localhost:8765');
            websocket.onmessage = function(event) {
                var data = event.data;
                if (data.startsWith('progress:')) {
                    var progressData = data.substring('progress:'.length);
                    $('#progress').html(progressData.split('|').map(p => `<div>${p.trim()}</div>`).join(''));
                } else {
                    var result = JSON.parse(data);
                    var statusClass = result.status === '成功' ? 'text-success' : 'text-danger';
                    $('#results').append(
                        `<div class="mb-2">
                            <div>${result.message}</div>
                            <small class="${statusClass}">状态：${result.status}</small>
                            ${result.retries ? `<div class="text-warning">重试次数：${result.retries}</div>` : ''}
                        </div>`
                    );
                    queueCount--;
                    updateQueueCount();
                    if (result.status === '成功') {
                        showNotification('下载完成', result.message);
                        addToHistory(result);
                    }
                }
            };

            function showNotification(title, message) {
                if (Notification.permission === 'granted') {
                    new Notification(title, { body: message });
                }
            }

            function addToHistory(result) {
                var historyItem = `
                    <li class="list-group-item">
                        <div>${result.message}</div>
                        <small class="text-muted">${new Date().toLocaleString()}</small>
                    </li>`;
                $('#historyList').prepend(historyItem);
            }

            // 请求通知权限
            if (Notification.permission !== 'granted') {
                Notification.requestPermission();
            }
            websocket.onerror = function(error) {
                console.error('WebSocket error:', error);
            };
            websocket.onclose = function() {
                console.log('WebSocket connection closed');
            };
        </script>
    </body>
    </html>
    """)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
