"""
B站下载器测试模块
包含对下载、WebSocket和任务管理功能的测试
"""

import pytest
import asyncio
import websockets
import json
from bili import app, TaskStatus, task_statuses, enqueue_download_task, task_queue
from dataclasses import asdict

@pytest.mark.asyncio
class TestBiliDownloader:
    """测试B站下载器的各项功能"""

    def setup_method(self, method):
        """
        每个测试方法运行前的设置
        初始化测试客户端和清理队列
        """
        self.app = app.test_client()
        self.app.testing = True
        # 确保每个测试前队列为空
        while not task_queue.empty():
            task_queue.get()
        # 清空任务状态
        task_statuses.clear()

    def teardown_method(self, method):
        """
        每个测试方法运行后的清理工作
        """
        while not task_queue.empty():
            task_queue.get()
        task_statuses.clear()

    async def test_download_endpoint(self):
        test_data = {
            "url": "https://www.bilibili.com/video/BV1234567890",
            "output_dir": "test_dir",
            "number": 1,
            "check": False
        }
        
        response = self.app.post('/download', 
                               json=test_data,
                               content_type='application/json')
        
        assert response.status_code == 200
        response_data = response.get_json()
        assert "任务已添加到队列" in response_data['message']

    async def test_websocket_connection(self):
        # 首先确保websocket服务器正在运行
        try:
            uri = "ws://localhost:8765"
            async with websockets.connect(uri) as websocket:
                test_task = TaskStatus(
                    task_id="test_id",
                    url="test_url",
                    output_dir="test_dir",
                    status="downloading",
                    progress="50%"
                )
                
                await websocket.send(json.dumps(asdict(test_task)))
                response = await websocket.recv()
                response_data = json.loads(response)
                
                assert response_data['task_id'] == "test_id"
                assert response_data['progress'] == "50%"
        except ConnectionRefusedError:
            pytest.skip("WebSocket server is not running")

    async def test_task_status_management(self):
        task_id = "test_task_1"
        test_task = TaskStatus(
            task_id=task_id,
            url="test_url",
            output_dir="test_dir",
            status="queued"
        )
        
        task_statuses[task_id] = test_task
        assert task_id in task_statuses
        assert task_statuses[task_id].status == "queued"
        
        task_statuses[task_id].status = "downloading"
        task_statuses[task_id].progress = "75%"
        assert task_statuses[task_id].status == "downloading"
        assert task_statuses[task_id].progress == "75%"

    async def test_download_queue(self):
        test_urls = [
            "https://www.bilibili.com/video/BV111",
            "https://www.bilibili.com/video/BV222"
        ]
        
        for url in test_urls:
            result = enqueue_download_task(url, "test_dir", 1, False)
            assert result is True
            
        assert task_queue.qsize() == 2 