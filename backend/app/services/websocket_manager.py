from fastapi import WebSocket
from typing import List, Dict, Any
from app.services.redis_service import redis_client
import json
import asyncio

class ConnectionManager:
    def __init__(self):
        # Active connections: room_id -> list of {ws: WebSocket, user_id: str}
        self.active_connections: Dict[str, List[Dict[str, Any]]] = {}

    async def connect(self, websocket: WebSocket, room_id: str, user_id: str):
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = []
            # Start a listener for this room if it's the first connection
            asyncio.create_task(self.subscribe_to_room(room_id))
        
        self.active_connections[room_id].append({"ws": websocket, "user_id": user_id})

    def disconnect(self, websocket: WebSocket, room_id: str):
        if room_id in self.active_connections:
            # Filter out the specific websocket connection
            self.active_connections[room_id] = [
                conn for conn in self.active_connections[room_id] 
                if conn['ws'] != websocket
            ]
            if not self.active_connections[room_id]:
                del self.active_connections[room_id]

    async def broadcast(self, message_data: dict, room_id: str):
        """
        Broadcast message to room.
        Logic:
        - If 'blocked': Send ONLY to sender (message_data['user_id']).
        - Else: Send to all.
        """
        if room_id in self.active_connections:
            message_json = json.dumps(message_data) if isinstance(message_data, dict) else message_data
            parsed_msg = message_data if isinstance(message_data, dict) else json.loads(message_data)
            
            sender_id = parsed_msg.get('user_id')
            status = parsed_msg.get('status')

            for connection in self.active_connections[room_id]:
                try:
                    # Visibility Logic
                    if status == 'blocked':
                        if connection['user_id'] == sender_id:
                            await connection['ws'].send_text(message_json)
                        # Else: Do not send to others
                    else:
                        # Allowed or Warning: Send to all
                        await connection['ws'].send_text(message_json)
                        
                except Exception as e:
                    print(f"Error sending message: {e}")
                    # Remove dead connection? 
                    # manager.disconnect usually handles cleanup on WebSocketDisconnect exception in endpoint

    async def subscribe_to_room(self, room_id: str):
        """
        Subscribe to the Redis channel for this room and broadcast received messages
        to all local WebSocket connections.
        """
        pubsub = redis_client.redis.pubsub()
        await pubsub.subscribe(room_id)
        
        try:
            async for message in pubsub.listen():
                if message['type'] == 'message':
                    # Decode data first
                    data = message['data']
                    if isinstance(data, bytes):
                        data = data.decode('utf-8')
                        
                    # Parse JSON to dict for broadcast logic
                    try:
                        msg_dict = json.loads(data)
                        await self.broadcast(msg_dict, room_id)
                    except:
                         # Fallback for plain strings
                         # But we expect JSON now
                         pass
        except Exception as e:
            print(f"Redis subscription error for room {room_id}: {e}")

manager = ConnectionManager()
