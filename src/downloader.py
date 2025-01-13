import os
import asyncio
import yt_dlp
from typing import Optional
from .models.queue import task_queue, TaskStatus, task_statuses

class BilibiliDownloader:
    def __init__(self, base_dir: str = '/mnt/shares/audiobooks'):
        self.base_dir = base_dir
        self.ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': '%(title)s.%(ext)s',
            'progress_hooks': [self._progress_hook],
        }

    def _progress_hook(self, d):
        if d['status'] == 'downloading':
            # 计算下载进度
            total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            downloaded = d.get('downloaded_bytes', 0)
            if total > 0:
                progress = (downloaded / total) * 100
                # 更新任务状态
                if 'task_id' in d:
                    task_id = d['task_id']
                    if task_id in task_statuses:
                        task_statuses[task_id].progress = f"{progress:.1f}%"

    async def download_audio(self, url: str, output_dir: str, task_id: str) -> bool:
        try:
            # 确保输出目录存在
            full_output_dir = os.path.join(self.base_dir, output_dir)
            os.makedirs(full_output_dir, exist_ok=True)

            # 更新下载选项
            self.ydl_opts.update({
                'outtmpl': os.path.join(full_output_dir, '%(title)s.%(ext)s'),
            })

            # 添加任务ID到下载选项
            def progress_hook_with_task_id(d):
                d['task_id'] = task_id
                self._progress_hook(d)

            self.ydl_opts['progress_hooks'] = [progress_hook_with_task_id]

            # 更新任务状态
            if task_id in task_statuses:
                task_statuses[task_id].status = "downloading"

            # 执行下载
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                ydl.download([url])

            # 更新任务状态为完成
            if task_id in task_statuses:
                task_statuses[task_id].status = "completed"
                task_statuses[task_id].progress = "100%"

            return True

        except Exception as e:
            # 更新任务状态为失败
            if task_id in task_statuses:
                task_statuses[task_id].status = "failed"
                task_statuses[task_id].error = str(e)
            return False

    async def process_queue(self):
        while True:
            try:
                task = await task_queue.get()
                if task:
                    await self.download_audio(task.url, task.output_dir, task.task_id)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error processing task: {e}")
            finally:
                task_queue.task_done() 