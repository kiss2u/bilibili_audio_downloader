"""
pytest配置文件
提供测试所需的fixture和配置
"""

import pytest
import asyncio

@pytest.fixture(scope="function")
def event_loop():
    """
    为每个测试函数创建新的事件循环
    
    Returns:
        asyncio.AbstractEventLoop: 新的事件循环实例
    """
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()

@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """
    设置测试环境的全局配置
    在测试会话开始时运行一次
    """
    yield