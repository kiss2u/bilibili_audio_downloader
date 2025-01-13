#!/bin/bash

# 停止服务
if [ -f .websocket.pid ]; then
    echo "Stopping WebSocket server..."
    kill $(cat .websocket.pid) 2>/dev/null || true
    rm -f .websocket.pid
fi

if [ -f .flask.pid ]; then
    echo "Stopping Flask application..."
    kill $(cat .flask.pid) 2>/dev/null || true
    rm -f .flask.pid
fi

# 如果虚拟环境处于激活状态，则停用它
if [ -n "$VIRTUAL_ENV" ]; then
    deactivate
fi

echo "All services stopped." 