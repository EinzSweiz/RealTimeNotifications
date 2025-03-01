from fastapi import APIRouter, WebSocket, Path
from app.presentation.websocket.websocket_manager import ws_manager
from app.infastructure.kafka_producer import KafkaProducerService
from typing import Annotated
from contextlib import asynccontextmanager
import asyncio
import json

websocket_router = APIRouter(tags=['Websocket'])
producer = KafkaProducerService()

@websocket_router.websocket('/ws/{user_id}')
async def websocket_endpoint(websocket: WebSocket, user_id: Annotated[int, Path()]):
    await ws_manager.connect(websocket=websocket, user_id=user_id)

    try:
        while True:
            data = await websocket.receive_text()
            print(f"📩 Received WebSocket Message: {data}")
            event = json.loads(data)

            event_type = event.get('type')
            event_name = event.get('event')

            # 🛑 **Validate Event Type and Name**
            if not event_type or not event_name:
                error_response = json.dumps({"error": "Invalid event format, ignoring..."})
                await websocket.send_text(error_response)
                continue  # Do not close WebSocket, just ignore

            if event_type != "notification" or event_name not in ["create", "fetch", "read"]:
                error_response = json.dumps({"error": "Unsupported event type or event name"})
                await websocket.send_text(error_response)
                await websocket.close()
                break  # Stop the loop, close WebSocket

            # ✅ **If valid, proceed with Kafka**
            topic = f"{event_type}.{event_name}"
            print('Topic:', topic)

            event['user_id'] = user_id
            await producer.send_message(topic, event)

    except Exception as e:
        print(f"WebSocket Error: {e}")

    finally:
        await ws_manager.disconnect(websocket, user_id=user_id)
