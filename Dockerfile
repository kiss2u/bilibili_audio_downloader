# 使用官方Python镜像作为基础镜像
FROM python:3.12-slim

# 添加标签
LABEL org.opencontainers.image.source="https://github.com/yourusername/bilibili_audio_downloader"
LABEL org.opencontainers.image.description="Bilibili Audio Downloader"
LABEL org.opencontainers.image.licenses="MIT"

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY requirements.txt .
COPY src/ ./src/
COPY templates/ ./templates/
COPY static/ ./static/

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 创建下载目录
RUN mkdir -p /mnt/shares/audiobooks

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production

# 暴露端口
EXPOSE 5000 8765

# 添加健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/ || exit 1

# 复制启动脚本
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# 设置入口点
ENTRYPOINT ["docker-entrypoint.sh"]
