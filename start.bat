@echo off
REM 激活虚拟环境并启动服务

REM 使用 cmd 方式激活虚拟环境
call venv\Scripts\activate.bat

REM 启动WebSocket服务器（在新窗口中）
start cmd /k "venv\Scripts\activate.bat && python websocket_server.py"

REM 等待2秒确保WebSocket服务器启动
timeout /t 2

REM 启动Flask应用
python bili.py

REM 保持窗口打开
pause 