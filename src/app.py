import os
import sys
from flask import Flask, request, jsonify, render_template
import threading
import asyncio
import logging
import traceback
import websockets
from src.downloader import BilibiliDownloader
from src.models.queue import enqueue_task

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

logger.info("Starting application...")

# 从环境变量获取配置
DOWNLOAD_DIR = os.getenv('DOWNLOAD_DIR', '/mnt/shares/audiobooks')
logger.info(f"Download directory: {DOWNLOAD_DIR}")

# 创建Flask应用，指定模板目录
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))
logger.info(f"Template directory: {template_dir}")
logger.info(f"Static directory: {static_dir}")

app = Flask(__name__, 
           template_folder=template_dir,
           static_folder=static_dir)

# 添加错误处理
@app.errorhandler(Exception)
def handle_error(error):
    logger.error(f"Unhandled error: {error}")
    logger.error(traceback.format_exc())
    return jsonify({
        "error": str(error),
        "traceback": traceback.format_exc()
    }), 500

try:
    downloader = BilibiliDownloader(base_dir=DOWNLOAD_DIR)
except Exception as e:
    logger.error(f"Error initializing downloader: {e}")
    logger.error(traceback.format_exc())
    raise

@app.route('/')
def home():
    try:
        logger.info("Accessing home page")
        logger.info(f"Available templates: {os.listdir(template_dir)}")
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error in home route: {e}")
        logger.error(traceback.format_exc())
        raise

@app.route('/download', methods=['POST'])
def download():
    try:
        data = request.get_json()
        logger.info(f"Received download request: {data}")
        
        url = data.get('url')
        output_dir = data.get('output_dir')
        number = int(data.get('number', 1))
        check = data.get('check', False)

        if enqueue_task(url, output_dir, number, check):
            def run_async():
                try:
                    asyncio.run(downloader.process_queue())
                except Exception as e:
                    logger.error(f"Error in async task: {e}")
                    logger.error(traceback.format_exc())
            
            thread = threading.Thread(target=run_async)
            thread.start()
            
            return jsonify({"message": "任务已添加到队列，正在排队下载，请稍后查看进度。"})
        return jsonify({"message": "任务添加到队列失败，请检查相关配置或稍后重试。"})
    except Exception as e:
        logger.error(f"Error in download route: {e}")
        logger.error(traceback.format_exc())
        raise

if __name__ == '__main__':
    logger.info("Running Flask app...")
    app.run(host='0.0.0.0', port=5000, debug=True) 