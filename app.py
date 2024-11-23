from flask import Flask, request, jsonify, render_template_string
from yt_dlp import YoutubeDL
import os
import re
import logging
import sys

app = Flask(__name__)

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class CustomLogger:
    def debug(self, msg):
        logging.debug(msg)

    def warning(self, msg):
        logging.warning(msg)

    def error(self, msg):
        logging.error(msg)

def progress_hook(d):
    if d['status'] == 'downloading':
        print(f"\rDownloading: {d['_percent_str']}", end="")
        sys.stdout.flush()

def download_audio(url, output_dir, number, check=False, max_retries=3):
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
        'logger': CustomLogger(),
        'progress_hooks': [progress_hook],
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

    results = []
    for i in range(1, number + 1):
        url_with_param = f"{url}?p={i}"
        result = download_audio(url_with_param, output_dir, i, check)
        results.append(result)
        if "No such playlist" in result:
            break

    return jsonify(results)

@app.route('/')
def home():
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>BiliBili Audio Downloader</title>
        <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    </head>
    <body>
        <h1>BiliBili Audio Downloader</h1>
        <form id="downloadForm">
            <label for="url">视频URL:</label><br>
            <input type="text" id="url" name="url"><br>
            <label for="output_dir">输出目录:</label><br>
            <input type="text" id="output_dir" name="output_dir"><br>
            <label for="number">循环次数:</label><br>
            <input type="number" id="number" name="number" value="1"><br>
            <label for="check">是否保留原名:</label><br>
            <input type="checkbox" id="check" name="check"><br>
            <button type="button" onclick="startDownload()">开始下载</button>
            <button type="button" onclick="showConstructedUrlAndNumber()">显示构造</button>
        </form>
        <div id="results"></div>
        <div id="constructedInfo" style="display:none;">
            <p>构造的新网址: <span id="constructedUrl"></span></p>
            <p>循环次数: <span id="constructedNumber"></span></p>
            <p>输出目录: <span id="constructedOutputDir"></span></p>
            <p>保留原名: <span id="constructedCheck"></span></p>
        </div>

        <script>
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
                if (pageFromUrl && !isNaN(pageFromUrl)) {
                    $('#number').val(pageFromUrl);  // 使用从URL中提取的page作为number
                    number = parseInt(pageFromUrl, 10);  // 更新number变量
                }

                $.ajax({
                    url: '/download',
                    type: 'POST',
                    contentType: 'application/json',
                    data: JSON.stringify({url: newUrl, output_dir: output_dir, number: number, check: check}),
                    success: function(response) {
                        $('#results').empty();
                        response.forEach(function(result) {
                            $('#results').append('<p>' + result + '</p>');
                        });
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
                $('#constructedNumber').text(!isNaN(number) ? number : "用户给定的数字");
                $('#constructedOutputDir').text(output_dir);
                $('#constructedCheck').text(check ? '已启用' : '未启用');

                $('#constructedInfo').css('display', 'block');
            }
        </script>
    </body>
    </html>
    """)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
