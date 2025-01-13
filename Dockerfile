# 构建阶段
FROM python:3.12-slim AS builder

# 设置工作目录
WORKDIR /build

# 只复制依赖文件
COPY requirements.txt .

# 安装构建依赖并创建虚拟环境
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt && \
    find /opt/venv -name "*.pyc" -delete && \
    find /opt/venv -name "__pycache__" -delete

# 验证基本依赖安装
RUN /opt/venv/bin/python -c "import flask; import websockets; import yt_dlp"

# 运行阶段
FROM python:3.12-slim

# 添加标签
LABEL org.opencontainers.image.source="https://github.com/kiss2u/bilibili_audio_downloader"
LABEL org.opencontainers.image.description="Bilibili Audio Downloader"
LABEL org.opencontainers.image.licenses="MIT"

# 设置工作目录
WORKDIR /app

# 安装运行时依赖
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/* && \
    apt-get clean

# 从builder阶段复制虚拟环境
COPY --from=builder /opt/venv /opt/venv

# 设置环境变量
ENV VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:$PATH" \
    PYTHONPATH="/app:$PYTHONPATH" \
    PYTHONUNBUFFERED=1 \
    FLASK_ENV=production \
    PYTHONDONTWRITEBYTECODE=1

# 创建必要的目录
RUN mkdir -p /mnt/shares/audiobooks static/css && \
    # 创建非root用户
    useradd -m -r -s /bin/bash app && \
    chown -R app:app /app /mnt/shares/audiobooks /opt/venv

# 复制应用文件
COPY --chown=app:app src/ ./src/
COPY --chown=app:app templates/ ./templates/
COPY --chown=app:app static/ ./static/

# 创建空的__init__.py文件
RUN touch src/__init__.py && \
    touch src/models/__init__.py

# 切换到非root用户
USER app

# 暴露端口
EXPOSE 5000 8765

# 添加健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/ || exit 1

# 复制启动脚本
COPY --chown=app:app docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# 设置入口点
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
