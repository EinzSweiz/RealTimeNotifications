import websockets
import asyncio
import pytest
import json

    
url = "ws://localhost:8002/ws/1"

@pytest.mark.asyncio
async def test_websocket_notification_read():
    async with websockets.connect(url) as websocket:
        try:
            message = {"type": "notification", "event": "read", "notification_id": "1b4c6d95-cebf-4bbb-92c5-f4365bdaab41"}
            await websocket.send(json.dumps(message))
            response = await websocket.recv()

            actual_data = json.loads(response)['data']
            expected_data = {
                "notification_id": "1b4c6d95-cebf-4bbb-92c5-f4365bdaab41",
                "user_id": 1,
                "message": "Your application was rejected",
                "type": "proposal_rejected",
                "read": True
            }
            actual_data.pop('created_at')
            assert actual_data == expected_data

        finally:
            await websocket.close()
            await asyncio.sleep(0.1)

@pytest.mark.asyncio
async def test_websocket_notification_create():
    async with websockets.connect(url) as websocket:
        try:
            message = {"type": "notification", "event": "create", "message": "Your application was rejected", "notification_type": "proposal_rejected", "user_email": "riad.sultanov.1999@gmail.com"}
            await websocket.send(json.dumps(message))
            response = await websocket.recv()

            actual_data = json.loads(response)['data']
            expected_data = {
                "user_id": 1,
                "message": "Your application was rejected",
                "type": "proposal_rejected",
                "read": False
            }
            actual_data.pop('created_at')
            actual_data.pop('notification_id')
            assert actual_data == expected_data
        finally:
            await websocket.close()
            await asyncio.sleep(0.1)

@pytest.mark.asyncio
async def test_websocket_invalid_event_type():
    async with websockets.connect(url) as websocket:
        try:
            message = {"type": "invalid", "event": "create", "message": "Your application was rejected", "notification_type": "proposal_rejected", "user_email": "riad.sultanov.1999@gmail.com"}
            await websocket.send(json.dumps(message))
            response = await websocket.recv()

            actual_data = json.loads(response)['error']
            assert actual_data == "Unsupported event type or event name"

        finally:
            await websocket.close()
            await asyncio.sleep(0.1)

@pytest.mark.asyncio
async def test_websocket_invalid_event_name():
    async with websockets.connect(url) as websocket:
        try:
            message = {"type": "notification", "event": "invalid", "message": "Your application was rejected", "notification_type": "proposal_rejected", "user_email": "riad.sultanov.1999@gmail.com"}
            await websocket.send(json.dumps(message))
            response = await websocket.recv()

            actual_data = json.loads(response)['error']
            assert actual_data == "Unsupported event type or event name"

        finally:
            await websocket.close()
            await asyncio.sleep(0.1)

@pytest.mark.asyncio
async def test_websocket_fetch():
    async with websockets.connect(url) as websocket:
        try:
            message = {"type": "notification", "event": "fetch"}
            await websocket.send(json.dumps(message))
            response = await websocket.recv()
            response_message = json.loads(response)['message']
            assert response_message == "Notifications Fetched"

        finally:
            await websocket.close()
            await asyncio.sleep(0.1)