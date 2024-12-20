# BiliBili Audio Downloader  
# 哔哩哔哩有声下载助手

这是一个简单的 python 脚本，基于 yt_dlp 实现下载，基于 FFmpeg 实现音频提取功能，同时基于 Flask 实现简单的 web 页面以供简化操作。

简言之，在有限的资源下，通过网页点点点，就能实现从哔哩哔哩网站下载一整套有声书至本地磁盘，自动修改文件名，并自动提取音频。

## 安装

1. **安装依赖**：
   ```bash
   pip install flask yt-dlp
   ```

2. **克隆仓库**：
   ```bash
   git clone https://github.com/kiss2u/bilibili_audio_downloader.git
   cd bilibili_audio_downloader.py
   ```

3. **运行应用**：
   ```bash
   python bilibili_audio_downloader.py
   ```
## 更新 docker 使用

1. 对于 x86_64 架构：

   ```bash
   docker pull nbzzd6/bilibili-audio-downloader:latest
   docker run -d -p 8080:8080 -v ./path_to_your_volume:/mnt/shares/audiobooks nbzzd6/bilibili-audio-downloader:latest
   ```
2. 对于 ARM64 架构：

   ```bash
   docker pull nbzzd6/bilibili-audio-downloader:latest
   docker run -d -p 8080:8080 -v ./path_to_your_volume:/mnt/shares/audiobooks --platform linux/arm64 nbzzd6/bilibili-audio-downloader:latest
   ```
3. 使用 Docker Compose

   如果你希望使用 Docker Compose 来管理多个服务，可以创建一个 docker-compose.yml 文件：

   ```yaml
   version: '3.8'
   services:
     web:
      image: nbzzd6/bilibili-audio-downloader:latest
      platform: linux/amd64  # 或者 linux/arm64
      ports:
        - "8080:8080"
      volumes:
        - ./path_to_your_volume:/mnt/shares/audiobooks  # 卷映射
      environment:
        - FLASK_APP=run.py
        - FLASK_RUN_HOST=0.0.0.0
        - FLASK_RUN_PORT=8080
   ```

## 功能演示

   ![web界面](/screenshots/screenshot.png)

1. **访问主页**：
   打开浏览器访问 `http://localhost:5000`，如果在远程服务器上运行，可修改 `localhost` 为服务器 IP 地址，端口不变。

   ![演示](/screenshots/demo4.jpeg)

   第一步：输入最后一个视频播放列表的 URL，并填写输出目录，比如“夜幕下的哈尔滨”，第二步：点击显示构造按钮，检查自动获取的数据是否正常，第三步：如无错误，则点击开始下载，下载开始。

2. **输入视频 URL**：
   在表单中输入 BiliBili 视频的 URL，例如：`https://www.bilibili.com/video/BV1LTyaYeE3v?p=75?session_from=https%3A%2F%2Fwww.bilibili.com%2Fvideo%2FBV1LTyaYeE3v%3Fp%3D75`。

   ![哔哩哔哩视频 URL](/screenshots/demo1.jpeg)

3. **选择输出目录**：
   输入音频文件保存位置，默认为 `/mnt/shares/audiobooks/Your_Directory`,`Your_Directory` 为你自己指定的目录名，比如：当你填入“夜幕下的哈尔滨”时，实际保存路径为 `/mnt/shares/audiobooks/夜幕下的哈尔滨`。

4. **选择循环次数**：
   本脚本以遍历的方法下载整本有声书，所以需要提供循环次数，即该有声书选集数，可从URL中自动识别，若无法识别，可手动输入，建议取有声书最后一个选集的网址填入，例如：`https://www.bilibili.com/video/BV1LTyaYeE3v?p=75`，则脚本会自动获取该有声书的选集数，自动填入循环次数为 75，同时如果下载失败，会重试3次，且已经下载过的不会再次下载。

   ![选集数](/screenshots/demo2.jpeg)

5. **是否保留原名**：
   根据需要勾选是否保留哔哩哔哩网站原有的音频名字，默认不保留，以“你的目录名字 - 次数”命名，若打钩则表示保留。

6. **点击开始下载**：
   点击按钮开始下载音频，后台程序可以看到下载进程，下载完成后会在 web 界面返回结果，为了整个程序的轻量化，不在前端展示下载进程。

## 日志记录

- 日志可通过终端查看，下载进程也将在后台输出。

## 注意事项

- 请确保你有权下载相关音频文件，并遵守 BiliBili 的使用条款。
- 此工具仅用于学习和研究目的，请勿用于非法用途。
- 建议搭配 alist 使用，可以自动生成播放列表。

![alist演示](/screenshots/demo3.jpeg)
