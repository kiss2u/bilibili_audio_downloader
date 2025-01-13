# PowerShell测试运行脚本
# 用于在Windows环境下运行测试

# 设置执行策略
Set-ExecutionPolicy RemoteSigned -Scope Process -Force

# 激活虚拟环境
.\venv\Scripts\Activate.ps1

# 启动WebSocket服务器
$wsProcess = Start-Process powershell -ArgumentList "-NoExit -Command `".\venv\Scripts\Activate.ps1; python src/websocket.py`"" -PassThru

# 等待WebSocket服务器启动
Start-Sleep -Seconds 2

# 运行测试
pytest test_bili.py -v

# 结束WebSocket服务器进程
Stop-Process -Id $wsProcess.Id -Force 