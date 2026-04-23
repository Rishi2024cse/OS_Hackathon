from typing import Dict
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        # Maps user_id to WebSocket connection
        self.active_connections: Dict[int, WebSocket] = {}

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: int):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def send_personal_message(self, message: dict, user_id: int):
        if user_id in self.active_connections:
            websocket = self.active_connections[user_id]
            try:
                await websocket.send_json(message)
            except Exception:
                self.disconnect(user_id)

    async def broadcast(self, message: dict):
        for connection in list(self.active_connections.values()):
            try:
                await connection.send_json(message)
            except Exception:
                pass

manager = ConnectionManager()
