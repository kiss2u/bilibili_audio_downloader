# 设置执行策略
Set-ExecutionPolicy RemoteSigned -Scope Process -Force

# 激活虚拟环境
.\venv\Scripts\Activate.ps1

# 启动WebSocket服务器（在新窗口中）
Start-Process powershell -ArgumentList "-NoExit -Command `".\venv\Scripts\Activate.ps1; python websocket_server.py`""

# 等待2秒确保WebSocket服务器启动
Start-Sleep -Seconds 2

# 启动Flask应用
python bili.py

# 安装依赖
pip install -r requirements.txt 