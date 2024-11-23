# 使用官方的 Python 基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 安装 git
RUN apt-get update && apt-get install -y git

# 复制当前目录的内容到工作目录
COPY . /app

# 更新 pip 并安装依赖
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# 暴露端口
EXPOSE 8080

# 设置环境变量
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV FLASK_RUN_PORT=8080

# 运行 Flask 应用
CMD ["flask", "run", "--host=0.0.0.0", "--port=8080"]
