#!/bin/bash
set -e

cd /app

echo "Starting WebSocket server..."
python3 -m src.websocket &

# 等待WebSocket服务器启动
sleep 2
echo "WebSocket server started"

echo "Starting Flask application..."
# 使用 exec 确保进程正确接收信号
exec python3 -m src.app 