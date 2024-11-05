# 使用官方的 Python 基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制项目文件到容器
COPY . /app

# 安装依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    && pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# 暴露端口
EXPOSE 8080

# 运行应用
CMD ["python", "app.py"]
