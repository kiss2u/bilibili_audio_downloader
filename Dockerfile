# 第一阶段：构建阶段
FROM python:3.9-slim AS builder

# 设置工作目录
WORKDIR /app

# 安装 git 和其他必要的工具
RUN apt-get update && apt-get install -y git build-essential

# 复制当前目录下的所有文件到容器的工作目录
COPY . /app

# 更新 pip 并安装依赖
RUN pip install --upgrade pip
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# 第二阶段：运行阶段
FROM python:3.9-slim

# 安装 git
RUN apt-get update && apt-get install -y git

# 设置工作目录
WORKDIR /app

# 安装依赖
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt /app/
RUN pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt

# 复制应用代码
COPY --from=builder /app/app.py /app/

# 暴露端口
EXPOSE 8080

# 设置环境变量
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV FLASK_RUN_PORT=8080

# 运行 Flask 应用
CMD ["flask", "run", "--host=0.0.0.0", "--port=8080"]
