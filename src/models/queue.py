import queue
from typing import Tuple

# 任务队列
task_queue = queue.Queue()

def enqueue_task(url: str, output_dir: str, number: int, check: bool) -> bool:
    """将下载任务添加到队列"""
    try:
        task_queue.put((url, output_dir, number, check))
        return True
    except queue.Full:
        return False 