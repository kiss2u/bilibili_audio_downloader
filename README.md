# BiliBili Audio Downloader  
# 哔哩哔哩有声下载助手

这是一个基于 Flask 的 Web 应用程序，用于从 BiliBili 下载音频。用户可以通过简单的网页界面输入视频 URL 并选择输出目录，应用程序将下载选定视频的音频文件。

## 功能

- 从 BiliBili 视频下载音频文件。
- 支持自定义输出目录。
- 记录下载过程的日志。
- 用户界面友好，易于使用。

## 技术栈

- **Python**: 后端开发语言。
- **Flask**: Python 微框架，用于构建 Web 应用程序。
- **yt-dlp**: 用于下载音频的命令行工具。
- **HTML/CSS/JavaScript**: 前端页面展示。

## 安装

1. **安装依赖**：
   ```bash
   pip install flask yt-dlp
   ```

2. **克隆仓库**：
   ```bash
   git clone https://github.com/kiss2u/bilibili-audio-downloader.git
   cd bilibili-audio-downloader
   ```

3. **运行应用**：
   ```bash
   python app.py
   ```

## 使用方法

![](/sceenshots/screenshot.png)

1. **访问主页**：
   打开浏览器访问 `http://localhost:5000`。

2. **输入视频 URL**：
   在表单中输入 BiliBili 视频的 URL。

3. **选择输出目录**：
   输入音频文件保存位置，默认为 `/mnt/shares/audiobooks/你的目录名字`。

4. **选择循环次数**：
   可以自己识别，但需要提供有声列表中的最后一个音频链接，也可自己指定。

5. **是否保留原名**：
   根据需要勾选是否保留哔哩哔哩网站原有的音频名字，默认不保留，以“你的目录名字 - 次数”命名，若打钩则表示保留。

6. **点击开始下载**：
   点击按钮开始下载音频，后台程序可以看到下载进程，下载完成后会在 web 界面返回结果，为了整个程序的轻量化，不在前端展示下载进程。

## 日志记录

- 日志可通过终端查看。

## 注意事项

- 请确保你有权下载相关音频文件，并遵守 BiliBili 的使用条款。
- 此工具仅用于学习和研究目的，请勿用于非法用途。

## 贡献

欢迎贡献！如果你发现 bug 或有改进意见，请提交 issue 或 pull request。

