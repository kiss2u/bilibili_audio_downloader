# BiliAudio-Downloader Docker 构建说明

## 先决条件

1. 安装 Docker Desktop：

   - Windows: https://docs.docker.com/desktop/install/windows-install/
   - macOS: https://docs.docker.com/desktop/install/mac-install/
   - Linux: https://docs.docker.com/engine/install/

2. 启用 Buildx 功能：
   ```bash
   docker buildx create --use
   ```

## 功能特性

- 支持 x64 和 arm 架构
- 多阶段构建优化镜像大小
- 生产环境最佳实践
- 资源限制和健康检查

## 构建步骤

1. 进入项目目录：

   ```bash
   cd BiliAudio-Downloader/docker
   ```

2. 构建并推送镜像：

   ```bash
   ./build.sh
   ```

3. 部署服务：
   ```bash
   docker-compose up -d
   ```

## 镜像优化

- 最终镜像大小：约 200MB
- 使用非 root 用户运行
- 自动清理构建缓存
