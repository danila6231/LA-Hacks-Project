from fastapi import WebSocket, WebSocketDisconnect
from services.speech_recognition import SpeechRecognizer
import json
import asyncio
from typing import Dict, Optional
import logging
import wave
import io
from shared_state import CAPTIONS_BUFFER

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.recognizers: Dict[str, SpeechRecognizer] = {}
        self.connection_states: Dict[str, bool] = {}
        self.closing_connections: Dict[str, bool] = {}
        self.last_audio_times: Dict[str, float] = {}
        self.transcription_buffers: Dict[str, list] = {}  # New buffer for transcriptions

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        self.connection_states[client_id] = True
        self.last_audio_times[client_id] = asyncio.get_event_loop().time()
        self.transcription_buffers[client_id] = []  # Initialize empty buffer for new client

    async def disconnect(self, client_id: str):
        if client_id in self.closing_connections:
            return
        
        self.closing_connections[client_id] = True
        self.connection_states[client_id] = False
        
        try:
            if client_id in self.active_connections:
                await self.active_connections[client_id].close()
        except Exception:
            pass
        
        # Clean up all resources including the buffer
        if client_id in self.recognizers:
            del self.recognizers[client_id]
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        if client_id in self.connection_states:
            del self.connection_states[client_id]
        if client_id in self.last_audio_times:
            del self.last_audio_times[client_id]
        if client_id in self.closing_connections:
            del self.closing_connections[client_id]
        if client_id in self.transcription_buffers:
            del self.transcription_buffers[client_id]

    async def send_message(self, client_id: str, message: str):
        if client_id in self.connection_states and self.connection_states[client_id]:
            try:
                await self.active_connections[client_id].send_text(message)
                # Store transcription in buffer
                data = json.loads(message)
                if "text" in data and data["text"]:  # Only store non-empty complete transcriptions
                    # self.transcription_buffers[client_id].append(data["text"])
                    CAPTIONS_BUFFER.append(data["text"])
                    # print(f"Buffer updated: {self.transcription_buffers[client_id]}")  # Debug print
            except Exception as e:
                print(f"Error sending message: {str(e)}")  # Debug print
                await self.disconnect(client_id)

    async def handle_audio(self, client_id: str, audio_data: bytes):
        if client_id not in self.connection_states or not self.connection_states[client_id]:
            return

        self.last_audio_times[client_id] = asyncio.get_event_loop().time()
        
        if client_id not in self.recognizers:
            self.recognizers[client_id] = SpeechRecognizer()
        
        try:
            recognizer = self.recognizers[client_id]
            result = recognizer.process_audio_chunk(audio_data)
            
            if result:
                message = json.dumps({"text": result})
                await self.send_message(client_id, message)
        except Exception:
            await self.disconnect(client_id)

    async def _keep_alive(self, client_id: str):
        while client_id in self.connection_states and self.connection_states[client_id]:
            try:
                await asyncio.sleep(30)
                if client_id in self.connection_states and self.connection_states[client_id]:
                    await self.active_connections[client_id].ping()
            except Exception:
                await self.disconnect(client_id)
                break

manager = ConnectionManager()

async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    keep_alive_task = asyncio.create_task(manager._keep_alive(client_id))
    
    try:
        while True:
            try:
                data = await websocket.receive_bytes()
                await manager.handle_audio(client_id, data)
            except WebSocketDisconnect:
                break
            except Exception:
                break
    finally:
        keep_alive_task.cancel()
        await manager.disconnect(client_id) 