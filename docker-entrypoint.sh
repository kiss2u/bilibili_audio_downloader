#!/bin/bash
set -ex  # 添加 -x 显示执行的命令

cd /app

echo "Current directory: $(pwd)"
echo "Python path: $PYTHONPATH"
echo "Virtual env: $VIRTUAL_ENV"
echo "PATH: $PATH"

echo "Checking Python installation..."
which python3
python3 --version

echo "Checking installed packages..."
pip list

echo "Checking directory structure..."
ls -la
ls -la src/

echo "Starting WebSocket server..."
python3 -m src.websocket &

# 等待WebSocket服务器启动
sleep 2
echo "WebSocket server started"

echo "Starting Flask application..."
# 使用 exec 确保进程正确接收信号
exec python3 -m src.app 