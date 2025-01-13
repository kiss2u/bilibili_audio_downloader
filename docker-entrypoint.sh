#!/bin/bash
set -e

# 启动WebSocket服务器
python3 src/websocket.py &

# 等待WebSocket服务器启动
sleep 2

# 启动Flask应用
exec python3 src/app.py 