import asyncio
import websockets
from flask import Flask, request, jsonify, render_template_string
from yt_dlp import YoutubeDL
import os
import re
import logging
import sys
import queue
import json
from dataclasses import dataclass, asdict
from typing import Dict, Optional
from datetime import datetime
import threading

app = Flask(__name__)

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 用于存储每个下载任务对应的websocket连接对象
download_progress_websockets = {}

# 提前创建基础输出目录
base_dir = "/mnt/shares/audiobooks/"
if not os.path.exists(base_dir):
    os.makedirs(base_dir)

# 任务队列，存储待执行的下载任务信息
task_queue = queue.Queue()

# 添加任务状态类
@dataclass
class TaskStatus:
    task_id: str
    url: str
    output_dir: str
    status: str  # 'queued', 'downloading', 'completed', 'failed'
    progress: str = "0%"
    message: str = ""
    created_at: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# 在全局变量区域添加任务状态字典
task_statuses: Dict[str, TaskStatus] = {}

class CustomLogger:
    def debug(self, msg):
        logging.debug(msg)

    def warning(self, msg):
        logging.warning(msg)

    def error(self, msg):
        logging.error(msg)


def progress_hook(d):
    if d['status'] == 'downloading':
        progress = d['_percent_str']
        task_id = d.get('task_id')
        if task_id:
            if task_id in task_statuses:
                task_statuses[task_id].progress = progress
                task_statuses[task_id].status = 'downloading'
            if task_id in download_progress_websockets:
                status_data = asdict(task_statuses[task_id])
                asyncio.run(send_progress(download_progress_websockets[task_id], json.dumps(status_data)))


async def send_progress(websocket, progress):
    """
    通过websocket发送下载进度信息到前端
    """
    try:
        await websocket.send(progress)
    except websockets.ConnectionClosed:
        pass


def format_audio_filename(title, output_dir, number, preferred_format):
    """
    根据给定的标题、输出目录、序号和音频格式生成音频文件名
    """
    title_pattern = re.compile(r'^(.*?)(\.m4a)?$')
    match = title_pattern.match(title)
    if match and match.group(2):
        base_title = match.group(1)
    else:
        base_title = f"{title}"
    return f"{output_dir} - {number}.{preferred_format}"


def setup_download_options(url, output_dir, number, check=False, max_retries=3, audio_format='m4a', task_id=None):
    """
    设置yt_dlp的下载选项，包括输出路径、音频提取格式等参数，同时添加task_id
    """
    new_output_dir = os.path.join(base_dir, output_dir)
    os.makedirs(new_output_dir, exist_ok=True)  # 这里只创建具体的输出子目录，且使用exist_ok避免重复创建已有目录

    if check:
        filename = '%(title)s.%(ext)s'
    else:
        filename = format_audio_filename("", output_dir, number, audio_format)

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
        'task_id': task_id  # 添加task_id参数，用于标识下载任务
    }
    return ydl_opts


async def download_audio(ydl, url, output_dir, number, check=False, max_retries=3, audio_format='m4a'):
    """
    执行音频下载操作，包含重试逻辑，并且处理websocket连接，接收外部传入的YoutubeDL对象
    """
    task_id = str(id(url))
    task_statuses[task_id] = TaskStatus(
        task_id=task_id,
        url=url,
        output_dir=output_dir,
        status='queued'
    )
    
    retries = 0
    websocket = None
    try:
        websocket = await websockets.connect('ws://localhost:8765')
        download_progress_websockets[task_id] = websocket
        
        while retries <= max_retries:
            try:
                task_statuses[task_id].status = 'downloading'
                info_dict = ydl.extract_info(url, download=True)
                actual_filename = os.path.basename(info_dict['requested_downloads'][0]['filepath'])
                task_statuses[task_id].status = 'completed'
                task_statuses[task_id].message = f"下载完成：{actual_filename}"
                break
            except Exception as e:
                error_msg = f"下载时发生异常: {str(e)}, 重试 {retries + 1}/{max_retries + 1}"
                task_statuses[task_id].message = error_msg
                if retries < max_retries:
                    retries += 1
                else:
                    task_statuses[task_id].status = 'failed'
                    return error_msg
    finally:
        if websocket:
            await send_progress(websocket, json.dumps(asdict(task_statuses[task_id])))
            del download_progress_websockets[task_id]
            await websocket.close()
        if task_id in task_statuses:
            # 设置一个超时时间后删除已完成的任务状态
            await asyncio.sleep(300)  # 5分钟后清理
            del task_statuses[task_id]
    return task_statuses[task_id].message


async def process_task_queue():
    """
    从任务队列中依次取出任务并执行下载操作，处理完一个任务后再处理下一个任务
    """
    try:
        websocket = await websockets.connect('ws://localhost:8765')  # 统一建立websocket连接
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
            # 将任务执行结果发送到前端（这里简单示例，可根据实际优化展示效果）
            await send_task_result_to_frontend(websocket, results)
            task_queue.task_done()
    except Exception as e:
        logging.error(f"处理任务队列出现异常: {str(e)}")
    finally:
        await websocket.close()  # 统一关闭websocket连接


async def send_task_result_to_frontend(websocket, results):
    """
    将任务执行结果发送到前端，可根据实际需求优化展示格式等
    """
    try:
        result_str = "\n".join(results)
        await websocket.send(result_str)
    except websockets.ConnectionClosed:
        pass


def enqueue_download_task(url, output_dir, number, check=False):
    """
    将下载任务信息添加到任务队列
    """
    try:
        task_queue.put((url, output_dir, number, check))
    except queue.Full:
        logging.error("任务队列已满，无法添加新任务，请稍后再试。")
        return jsonify({"message": "任务队列已满，无法添加新任务，请稍后再试。"})
    return True


@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()
    url = data.get('url')
    output_dir = data.get('output_dir')
    number = int(data.get('number', 1))
    check = data.get('check', False)

    if enqueue_download_task(url, output_dir, number, check):
        # 使用线程运行异步任务
        def run_async():
            asyncio.run(process_task_queue())
        
        thread = threading.Thread(target=run_async)
        thread.start()
        
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
        <form id="downloadForm" class="mb-4">
            <div class="mb-3">
                <label for="url" class="form-label">视频URL:</label>
                <input type="text" id="url" name="url" class="form-control">
            </div>
            <div class="mb-3">
                <label for="output_dir" class="form-label">输出目录:</label>
                <input type="text" id="output_dir" name="output_dir" class="form-control">
            </div>
            <div class="mb-3">
                <label for="number" class="form-label">循环次数:</label>
                <input type="number" id="number" name="number" value="1" class="form-control">
            </div>
            <div class="form-check mb-3">
                <input type="checkbox" id="check" name="check" class="form-check-input">
                <label for="check" class="form-check-label">是否保留原名:</label>
            </div>
            <button type="button" onclick="startDownload()" class="btn btn-primary">开始下载</button>
            <button type="button" onclick="showConstructedUrlAndNumber()" class="btn btn-secondary">显示构造</button>
        </form>
        <div id="results" class="mb-4"></div>
        <div id="progress" class="mb-4"></div>
        <div id="constructedInfo" style="display:none;">
            <p>构造的新网址: <span id="constructedUrl"></span></p>
            <p>循环次数: <span id="constructedNumber"></span></p>
            <p>输出目录: <span id="constructedOutputDir"></span></p>
            <p>保留原名: <span id="constructedCheck"></span></p>
        </div>

        <script>
            var websocket;
            function startDownload() {
                var url = $('#url').val();
                var output_dir = $('#output_dir').val();
                var number = parseInt($('#number').val(), 10);
                var check = $('#check').is(':checked');

                // 解析URL以获取BVid
                var parsedUrl = new URL(url);
                var pathParts = parsedUrl.pathname.split('/');
                var BVid = pathParts[2];
                var newUrl = `https://www.bilibili.com/video/${BVid}`;
                $('#constructedUrl').text(newUrl);  // 显示构造的新网址

                // 从查询字符串中获取page
                var searchParams = new URLSearchParams(parsedUrl.search);
                var pageFromUrl = searchParams.get('p');
                if (pageFromUrl &&!isNaN(pageFromUrl)) {
                    $('#number').val(pageFromUrl);  // 使用从URL中提取的page作为number
                    number = parseInt(pageFromUrl, 10);  // 更新number变量
                }

                // 将任务信息发送到后端添加到任务队列
                $.ajax({
                    url: '/download',
                    type: 'POST',
                    contentType: 'application/json',
                    data: JSON.stringify({url: newUrl, output_dir: output_dir, number: number, check: check}),
                    success: function(response) {
                        $('#results').empty();
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

                // 解析URL以获取BVid
                var parsedUrl = new URL(url);
                var pathParts = parsedUrl.pathname.split('/');
                var BVid = pathParts[2];
                var newUrl = `https://www.bilibili.com/video/${BVid}`;

                // 显示构造的新网址、循环次数和输出目录
                $('#constructedUrl').text(newUrl);
                $('#constructedNumber').text(!isNaN(number)? number : "用户给定的数字");
                $('#constructedOutputDir').text(output_dir);
                $('#constructedCheck').text(check? '已启用' : '未启用');

                $('#constructedInfo').css('display', 'block');
            }

            // 新增函数用于处理接收到的任务结果信息并展示
            function handleTaskResult(result) {
                $('#results').append('<p>' + result + '</p>');
            }

            // 建立websocket连接并监听任务结果消息
            websocket = new WebSocket('ws://localhost:8765');
            websocket.onmessage = function(event) {
                handleTaskResult(event.data);
            };
            websocket.onerror = function(error) {
                console.error('Websocket error:', error);
            };
            websocket.onclose = function() {
                console.log('Websocket connection closed');
            };
        </script>
    </body>
    </html>
    """)


# 添加任务状态清理函数
async def cleanup_old_tasks():
    while True:
        current_time = datetime.now()
        for task_id in list(task_statuses.keys()):
            task = task_statuses[task_id]
            # 清理超过1小时的已完成任务
            if task.status in ['completed', 'failed']:
                created_time = datetime.strptime(task.created_at, "%Y-%m-%d %H:%M:%S")
                if (current_time - created_time).total_seconds() > 3600:
                    del task_statuses[task_id]
        await asyncio.sleep(3600)  # 每小时检查一次


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000, debug=True)