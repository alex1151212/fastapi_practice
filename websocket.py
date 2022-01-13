from typing import List 

from fastapi import WebSocket, websockets
from aiortc import (
    RTCIceCandidate,
    RTCPeerConnection,
    RTCSessionDescription,
    VideoStreamTrack,
)


class ConnectionManager:

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)
    
        

    # async def handleSDPOffer(self,desc):
    #     print("*** 收到遠端送來的offer")
    #     try:
    #         if not self.peer:
    #             self.peer = RTCPeerConnection()
    #         print(" = 設定 remote description = ")
            
    #         await self.peer.setRemoteDescription(desc)
    #         if not self.cacheStream:
    #             await addStreamProcess() # getUserMedia & addTrack
    #         await self.peer.createAnswer()
    #     except :
    #         print("Error")

    # async def handleSDPAnswer(self,desc):
    #     print("*** 遠端接受我們的offer並發送answer回來")
        
    #     try:
    #         await self.peer.setRemoteDescription(desc)
    #     except:
    #         print("error")

