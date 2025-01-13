@echo off
REM 激活虚拟环境
call venv\Scripts\activate.bat

REM 启动WebSocket服务器（在新窗口中）
start cmd /k "venv\Scripts\activate.bat && python websocket_server.py"

REM 等待WebSocket服务器启动
timeout /t 2

REM 运行测试
pytest test_bili.py -v

REM 结束后关闭WebSocket服务器窗口
taskkill /F /IM python.exe /FI "WINDOWTITLE eq websocket_server.py"

pause 