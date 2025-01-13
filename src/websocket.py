import asyncio
import json
import logging
import websockets

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 存储所有连接的客户端
CLIENTS = set()

async def register(websocket):
    CLIENTS.add(websocket)
    try:
        await websocket.wait_closed()
    finally:
        CLIENTS.remove(websocket)

async def broadcast_message(message):
    if CLIENTS:
        await asyncio.gather(
            *[client.send(json.dumps(message)) for client in CLIENTS]
        )

async def websocket_handler(websocket, path):
    logger.info(f"New client connected from {websocket.remote_address}")
    await register(websocket)

async def start_server():
    logger.info("Starting WebSocket server...")
    async with websockets.serve(websocket_handler, "0.0.0.0", 8765):
        await asyncio.Future()  # 运行直到被取消

def run_server():
    logger.info("Initializing WebSocket server...")
    asyncio.run(start_server())

if __name__ == "__main__":
    run_server() 