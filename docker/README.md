# BiliAudio Downloader Docker 使用指南

## 1. 构建 Docker 镜像

```bash
docker build -t bili-audio-downloader .
```

## 2. 运行容器

```bash
docker run -d \
  --name bili-audio-downloader \
  -p 5000:5000 \
  -v /path/to/config:/app/config \
  -v /path/to/downloads:/app/downloads \
  bili-audio-downloader
```

## 3. 使用 docker-compose

```yaml
version: "3"
services:
  bili-audio:
    image: bili-audio-downloader
    container_name: bili-audio-downloader
    ports:
      - "5000:5000"
    volumes:
      - ./config:/app/config
      - ./downloads:/app/downloads
    restart: unless-stopped
```

## 4. 访问 Web 界面

打开浏览器访问：http://localhost:5000

## 5. 环境变量配置

- `BILI_COOKIE`: B 站登录 cookie
- `DOWNLOAD_DIR`: 下载目录路径（默认为/app/downloads）
- `LOG_LEVEL`: 日志级别（默认为 INFO）

## 6. 更新镜像

```bash
docker pull kiss2u/bilibili_audio_downloader:latest
docker-compose down
docker-compose up -d
```

## 7. 查看日志

```bash
docker logs -f bili-audio-downloader
```

## 8. 停止容器

```bash
docker stop bili-audio-downloader
```

## 9. 删除容器

```bash
docker rm bili-audio-downloader
```
