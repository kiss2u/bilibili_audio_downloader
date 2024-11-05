from flask import Flask, request, render_template, jsonify, send_from_directory
from flask_sockets import Sockets
from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler
from .utils import download_audio
import logging
import os
import re
import sys
from websocket import create_connection

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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

def setup_routes(app):
    sockets = Sockets(app)

    @sockets.route('/ws')
    def handle_websocket(ws):
        while True:
            try:
                message = ws.receive()
                if message is None:
                    break
                data = eval(message)
                url = data.get('url')
                output_dir = data.get('output_dir')
                number = int(data.get('number', 1))
                check = data.get('check', False)

                for i in range(1, number + 1):
                    url_with_param = f"{url}?p={i}"
                    download_audio(ws, url_with_param, output_dir, i, check)
            except Exception as e:
                ws.send(str(e))
                break

    @app.route('/download', methods=['POST'])
    def download():
        data = request.json
        url = data.get('url')
        output_dir = data.get('output_dir')
        number = int(data.get('number', 1))
        check = data.get('check', False)

        # 发送 WebSocket 请求
        ws_url = f"ws://{request.host}/ws"
        ws = create_connection(ws_url)
        ws.send(str({
            'url': url,
            'output_dir': output_dir,
            'number': number,
            'check': check
        }))
        ws.close()

        return jsonify({"status": "success"})

    @app.route('/')
    def home():
        logging.info("Handling home page request")
        return
