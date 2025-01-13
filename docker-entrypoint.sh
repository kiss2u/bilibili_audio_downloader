#!/bin/bash
set -e

cd /app

# 启动WebSocket服务器
python3 -m src.websocket &

# 等待WebSocket服务器启动
sleep 2

# 启动Flask应用
exec python3 -m src.app 