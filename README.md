# B 站音频下载工具

[![Docker Build Status](https://img.shields.io/github/actions/workflow/status/kiss2u/bilibili_audio_downloader/docker-build.yml?label=Docker%20Build)](https://github.com/kiss2u/bilibili_audio_downloader/actions)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)

本工具提供从 Bilibili 下载音频内容并自动生成有声书目录结构的功能，支持多种音质选择和元数据写入。

## 主要特性

- 📥 B 站音频内容下载
- 📚 自动生成有声书目录结构
- 🎚️ 多音质选择（64k/132k/192k）
- 🏷️ ID3 元数据写入
- 🐳 完整的 Docker 支持
- 🔄 下载历史记录

## 快速开始

### 前置要求

- Python 3.8+
- FFmpeg
- Docker（可选）

```bash
pip install -r requirements.txt
```

## Docker 使用指南

### 构建镜像

```bash
cd docker
./build.sh  # 使用多阶段构建优化镜像
```

### 运行容器

```bash
docker run -d \
  -p 5000:5000 \
  -v /path/to/audiobooks:/app/audiobooks \
  -v /path/to/config.yaml:/app/config.yaml \
  --name bili-audio \
  ghcr.io/kiss2u/bilibili_audio_downloader:latest
```

### docker-compose 部署

```yaml
version: "3"
services:
  bili-audio:
    image: ghcr.io/kiss2u/bilibili_audio_downloader:latest
    ports:
      - "5000:5000"
    volumes:
      - ./audiobooks:/app/audiobooks
      - ./config.yaml:/app/config.yaml
    restart: unless-stopped
```

### 环境变量

| 变量名       | 默认值          | 说明         |
| ------------ | --------------- | ------------ |
| PORT         | 5000            | 服务监听端口 |
| LOG_LEVEL    | INFO            | 日志级别     |
| DOWNLOAD_DIR | /app/audiobooks | 音频存储路径 |

## 配置示例

```yaml
# config.yaml
cookie: "YOUR_BILI_COOKIE"
quality: 132k
concurrency: 3
proxy:
  http: "http://proxy:8080"
  https: "http://proxy:8080"
```

## 开发贡献

```bash
# 安装开发依赖
pip install -r requirements-dev.txt

# 运行测试
pytest tests/
```

## 许可证

MIT License
