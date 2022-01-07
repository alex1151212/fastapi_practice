from fastapi.routing import APIRouter
from fastapi import (
    Depends,
    HTTPException,
    Cookie,
    Request,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional

import schemas,models,JWTtoken
from database import get_db
from hashing import Hash
from websocket import ConnectionManager


app_chatroom = APIRouter(
    
)

templates = Jinja2Templates(directory="templates")

manager = ConnectionManager()


@app_chatroom.get("/chat")
async def get(
    request:Request,
    Authentication:Optional[str]=Cookie(None)
    ):
    
    user = JWTtoken.verify_token(Authentication)
    if user is None:
        raise HTTPException(401)
    user_id = user.id
    print(user)
    print(user_id)
    return templates.TemplateResponse("chatroom.html",{
        "request":request,
        "user_id":user.id,
        "user":user.username
    })


@app_chatroom.websocket("/{username}/ws")
async def websocket_endpoint(websocket: WebSocket, username: str):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()

            #await manager.send_personal_message(f"You wrote: {data}", websocket)
            await manager.broadcast(f"使用者:{username} , 說:{data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"使用者 #{username} left the chat")
