# 使用官方的 Python 基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制当前目录的内容到工作目录
COPY . /app

# 安装所需的依赖项
RUN pip install --no-cache-dir -r requirements.txt

# 暴露端口
EXPOSE 8080

# 设置环境变量
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV FLASK_RUN_PORT=8080

# 运行 Flask 应用
CMD ["flask", "run", "--host=0.0.0.0", "--port=8080"]
