#!/bin/bash

# 登录到Docker Hub（如果需要）
# docker login

# 设置版本号
VERSION="1.0.0"

# 构建并推送多架构镜像
docker buildx create --use
docker buildx build --platform linux/amd64,linux/arm64 \
    -t yourusername/bilibili-audio-downloader:${VERSION} \
    -t yourusername/bilibili-audio-downloader:latest \
    --push . 