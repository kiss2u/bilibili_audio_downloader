# BiliBili Audio Downloader
# 哔哩哔哩有声下载助手

[![Build Status](https://github.com/kiss2u/bilibili_audio_downloader/workflows/Build%20and%20Push%20Docker%20Image/badge.svg)](https://github.com/kiss2u/bilibili_audio_downloader/actions)
[![Docker Pulls](https://img.shields.io/docker/pulls/yourusername/bilibili-audio-downloader.svg)](https://hub.docker.com/r/yourusername/bilibili-audio-downloader)

基于 yt_dlp 的哔哩哔哩音频下载工具，支持Docker部署。支持批量下载、自动提取音频、进度显示等功能。

## 功能特点

- 🚀 支持批量下载整个视频系列
- 🎵 自动提取音频（支持多种格式）
- 📊 实时显示下载进度
- 🔄 自动重试机制
- 🐳 Docker支持（包括ARM架构）
- 🔒 安全的非root运行
- 💾 支持断点续传

## 快速开始

### 使用 Docker（推荐）

```bash
# 拉取最新稳定版
docker pull yourusername/bilibili-audio-downloader:latest

# 拉取开发版
docker pull yourusername/bilibili-audio-downloader:latest-dev

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
git clone https://github.com/kiss2u/bilibili_audio_downloader.git
cd bilibili_audio_downloader

# 启动服务
docker-compose up -d
```

## 使用方法

1. 访问 Web 界面：`http://localhost:5000`
2. 输入B站视频URL（支持单个视频和系列视频）
3. 设置输出目录和其他选项
4. 点击下载按钮开始下载

### URL格式示例

- 单个视频：`https://www.bilibili.com/video/BV1xx411c7mD`
- 系列视频：`https://www.bilibili.com/video/BV1xx411c7mD?p=1`

## 开发指南

### 本地开发环境

1. 安装依赖：
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate.bat  # Windows
pip install -r requirements.txt
```

2. 运行测试：
```bash
pytest -v
```

### Docker开发版本

```bash
# 构建本地开发版本
docker build -t bilibili-audio-downloader:dev .

# 运行开发版本
docker run -d \
    -p 5000:5000 \
    -p 8765:8765 \
    -v ./downloads:/mnt/shares/audiobooks \
    bilibili-audio-downloader:dev
```

## 项目结构

```
bilibili_audio_downloader/
├── src/                 # 源代码
│   ├── app.py          # Flask应用
│   ├── downloader.py   # 下载核心
│   └── websocket.py    # WebSocket服务
├── templates/          # 前端模板
└── static/            # 静态资源
```

## 支持的平台

- ✅ linux/amd64
- ✅ linux/arm64

## 版本说明

- latest: 稳定版本
- latest-dev: 开发版本
- YYYYMMDD.COMMITS.HASH: 具体版本号

## 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 许可证

MIT License

## 致谢

- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- [Flask](https://flask.palletsprojects.com/)
- [WebSocket](https://websockets.readthedocs.io/)
