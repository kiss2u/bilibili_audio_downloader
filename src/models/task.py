from dataclasses import dataclass
from datetime import datetime
from typing import Dict

@dataclass
class TaskStatus:
    task_id: str
    url: str
    output_dir: str
    status: str  # 'queued', 'downloading', 'completed', 'failed'
    progress: str = "0%"
    message: str = ""
    created_at: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# 全局任务状态字典
task_statuses: Dict[str, TaskStatus] = {} 