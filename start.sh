#!/bin/bash

# 确保脚本在出错时退出
set -e

# 检查并创建虚拟环境
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "Installing dependencies..."
pip install -r requirements.txt

# 检查是否安装了FFmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo "FFmpeg is not installed. Installing FFmpeg..."
    if [ -f /etc/debian_version ]; then
        # Debian/Ubuntu
        sudo apt-get update
        sudo apt-get install -y ffmpeg
    elif [ -f /etc/redhat-release ]; then
        # CentOS/RHEL
        sudo yum install -y epel-release
        sudo yum install -y ffmpeg
    elif command -v pacman &> /dev/null; then
        # Arch Linux
        sudo pacman -S --noconfirm ffmpeg
    else
        echo "Unable to install FFmpeg automatically. Please install it manually."
        exit 1
    fi
fi

# 创建日志目录
mkdir -p logs

# 启动WebSocket服务器（后台运行）
echo "Starting WebSocket server..."
python src/websocket.py > logs/websocket.log 2>&1 &
WEBSOCKET_PID=$!

# 等待WebSocket服务器启动
sleep 2

# 启动Flask应用
echo "Starting Flask application..."
python src/app.py > logs/app.log 2>&1 &
FLASK_PID=$!

# 保存进程ID
echo $WEBSOCKET_PID > .websocket.pid
echo $FLASK_PID > .flask.pid

echo "Services started. Check logs/app.log and logs/websocket.log for details."
echo "Access the application at http://localhost:5000"

# 捕获SIGINT和SIGTERM信号
trap cleanup SIGINT SIGTERM

cleanup() {
    echo "Stopping services..."
    kill $(cat .websocket.pid) 2>/dev/null || true
    kill $(cat .flask.pid) 2>/dev/null || true
    rm -f .websocket.pid .flask.pid
    deactivate
    exit 0
}

# 等待用户输入
read -p "Press Enter to stop the services..."
cleanup 