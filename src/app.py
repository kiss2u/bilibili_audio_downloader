from flask import Flask, render_template, request, jsonify, Response
from utils.downloader import BiliDownloader
import os
import json
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('BiliDownloader-Web')

app = Flask(__name__)
downloader = BiliDownloader()

@app.route('/')
def index():
    logger.info("访问主页")
    return render_template('index.html')

@app.route('/check_playlist', methods=['POST'])
def check_playlist():
    data = request.get_json()
    bvid = data.get('bvid')
    logger.info(f"检查播放列表: {bvid}")
    try:
        count = downloader.check_playlist(bvid)
        logger.info(f"播放列表检查完成: {count} 个视频")
        return jsonify({'success': True, 'count': count})
    except Exception as e:
        logger.error(f"播放列表检查失败: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/download', methods=['GET'])
def download():
    bvid = request.args.get('bvid')
    output_dir = request.args.get('output_dir')
    rename = request.args.get('rename', 'false').lower() == 'true'
    
    if not bvid or not output_dir:
        logger.error("下载请求缺少必要参数")
        return jsonify({'error': '缺少必要参数'}), 400
    
    logger.info(f"开始下载任务: bvid={bvid}, output_dir={output_dir}, rename={rename}")
    
    def generate():
        try:
            for progress in downloader.download(bvid, output_dir, rename):
                yield f"data: {json.dumps(progress)}\n\n"
        except Exception as e:
            logger.error(f"下载过程出错: {str(e)}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    logger.info("启动Web服务器")
    app.run(debug=True) 