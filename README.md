# BiliBili Audio Downloader
# 哔哩哔哩有声下载助手

基于 yt_dlp 的哔哩哔哩音频下载工具，支持Docker部署。

## 快速开始

### 使用 Docker（推荐）

```bash
# 拉取镜像
docker pull yourusername/bilibili-audio-downloader:latest

# 运行容器
docker run -d \
    -p 5000:5000 \
    -p 8765:8765 \
    -v ./downloads:/mnt/shares/audiobooks \
    yourusername/bilibili-audio-downloader:latest
```

### 使用 Docker Compose

```bash
# 克隆仓库
git clone https://github.com/yourusername/bilibili_audio_downloader.git
cd bilibili_audio_downloader

# 启动服务
docker-compose up -d
```

## 使用方法

1. 访问 `http://localhost:5000`
2. 输入视频URL和下载设置
3. 点击下载按钮

## 支持的平台
- linux/amd64
- linux/arm64

## 许可证
MIT License
