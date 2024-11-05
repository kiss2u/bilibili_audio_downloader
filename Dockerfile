# 第一阶段：构建阶段
FROM python:3.9-slim AS builder

# 设置工作目录
WORKDIR /app

# 复制项目文件到容器
COPY . /app

# 安装必要的系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# 升级 pip
RUN pip install --upgrade pip

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 创建目标目录
RUN mkdir -p /mnt/shares/audiobooks

# 第二阶段：运行阶段
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制构建阶段生成的文件
COPY --from=builder /app /app

# 创建目标目录
RUN mkdir -p /mnt/shares/audiobooks

# 暴露端口
EXPOSE 8080

# 运行应用
CMD ["python", "app.py"]
