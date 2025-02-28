import json
import asyncio
import logging
from fastapi import WebSocket
from typing import List, Dict
from app.infastructure.redis_client import redis_client


logger = logging.getLogger(__name__)


class WebsocketManager:
    
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}
        self.redis_pubsub = None
        self.redis_task = None
    
    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)

    async def disconnect(self, websocket: WebSocket, user_id: int):
        if user_id in self.active_connections and websocket in self.active_connections[user_id]:
            self.active_connections[user_id].remove(websocket)
            print(f"Disconnected from WebSocket for user {user_id}")
            logger.info(f"�� Disconnected from WebSocket for user {user_id}")
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
                print(f"User {user_id} has no active WebSocket connections")
                logger.info(f"User {user_id} has no active WebSocket connections")

        
    async def send_message(self, user_id: int, message: str, data: dict = None):
        if user_id in self.active_connections:
            message_data_json = json.dumps({'message': message, 'data': data})

            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_text(message_data_json)
                except:
                    await self.disconnect(connection, user_id=user_id)


    async def listen_to_redis(self):
        self.redis_pubsub = await redis_client.get_redis_pubsub()

        async with self.redis_pubsub.pubsub() as pubsub:
            await pubsub.subscribe('websocket_channel')
            print("📡 WebSocket Manager subscribed to Redis Pub/Sub...")
            logger.info("📡 WebSocket Manager subscribed to Redis Pub/Sub...")

            async for message in pubsub.listen():
                print(f"📡 RAW Redis Message: {message}")  # Debug log
                logger.info(f"📡 RAW Redis Message: {message}")
                
                if message['type'] == 'message':
                    try:
                        data = json.loads(message['data'])
                        print(f"📡 Received from Redis: {data}")
                        logger.info(f"📡 Received from Redis: {data}")
                        if isinstance(data['data'], list):
                            if len(data['data']) > 0:
                                user_id = data['data'][0].get('user_id')
                            else:
                                print("⚠️ Received empty notification list, skipping...")
                                continue
                        else:  
                            user_id = data['data'].get('user_id')
                        if user_id:
                            await self.send_message(user_id, data['message'], data['data'])
                    except Exception as e:
                        print(f"❌ WebSocket Redis Listen Error: {e}")
                        logger.error(f"❌ WebSocket Redis Listen Error: {e}")

    async def start_redis_listener(self):
        if not self.redis_task:
            print("🚀 Starting Redis Pub/Sub Listener for WebSockets...")
            self.redis_task = asyncio.create_task(self.listen_to_redis())

ws_manager = WebsocketManager()





    # def __init__(self):
    #     self.active_connection: List[WebSocket] = []
    #     self.redis_pubsub = None
    #     self.redis_task = None

    
    # async def connect(self, websocket: WebSocket):
    #     await websocket.accept()
    #     self.active_connection.append(websocket)

    # async def disconnect(self, websocket: WebSocket):
    #     if websocket in self.active_connection:
    #         self.active_connection.remove(websocket)
    
    # async def send_message(self, message: str, data: dict = None):
    #     message_data_json = json.dumps({'message': message, 'data': data})

    #     for connection in self.active_connection:
    #         try:
    #             await connection.send_text(message_data_json)
    #         except:
    #             await self.disconnect(connection)

    # async def listen_to_redis(self):
    #     self.redis_pubsub = await redis_client.get_redis_pubsub()