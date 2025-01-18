FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ffmpeg \
    build-essential \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制应用代码
COPY . .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 确保脚本可执行
RUN chmod +x /app/src/app.py

# 设置环境变量
ENV FLASK_ENV=production

# 创建非root用户
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s \
    CMD curl -f http://localhost:5000/health || exit 1

# 暴露端口
EXPOSE 5000

# 启动命令
CMD ["python", "src/app.py"]
