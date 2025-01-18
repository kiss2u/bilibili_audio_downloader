# 构建阶段
FROM --platform=$BUILDPLATFORM python:3.9-slim as builder

WORKDIR /app

# 安装系统依赖
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ffmpeg \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 安装Python依赖
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 运行阶段
FROM python:3.9-slim

WORKDIR /app

# 从构建阶段复制已安装的Python包
COPY --from=builder /root/.local /root/.local
COPY --from=builder /app /app

# 确保脚本可执行
RUN chmod +x /app/src/app.py

# 设置环境变量
ENV PATH=/root/.local/bin:$PATH
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