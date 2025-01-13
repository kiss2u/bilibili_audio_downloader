import asyncio
import websockets
import json
from typing import Dict

# WebSocket连接存储
websocket_connections: Dict[str, websockets.WebSocketServerProtocol] = {}

async def handle_websocket(websocket, path):
    """处理WebSocket连接"""
    try:
        async for message in websocket:
            await websocket.send(message)
    except websockets.ConnectionClosed:
        pass

async def start_websocket_server():
    """启动WebSocket服务器"""
    async with websockets.serve(handle_websocket, "localhost", 8765):
        await asyncio.Future()  # 永久运行

def run_websocket_server():
    """运行WebSocket服务器的入口点"""
    asyncio.run(start_websocket_server()) 