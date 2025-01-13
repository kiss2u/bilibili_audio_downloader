import asyncio
from dataclasses import dataclass
from typing import Optional
import uuid

@dataclass
class TaskStatus:
    task_id: str
    url: str
    output_dir: str
    status: str = "queued"
    progress: str = "0%"
    error: Optional[str] = None

# 全局任务队列
task_queue = asyncio.Queue()
task_statuses = {}

def enqueue_task(url: str, output_dir: str, number: int = 1, check: bool = False) -> bool:
    try:
        task_id = str(uuid.uuid4())
        task = TaskStatus(
            task_id=task_id,
            url=url,
            output_dir=output_dir
        )
        task_statuses[task_id] = task
        task_queue.put_nowait(task)
        return True
    except Exception as e:
        print(f"Error enqueueing task: {e}")
        return False 