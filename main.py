
from sqlalchemy.sql.functions import user
import uvicorn
from fastapi import (
    FastAPI ,
    Depends ,
    HTTPException,
    Form,
    Cookie, 
    WebSocket,
    Query,
    status,
    WebSocketDisconnect,
)

from starlette.requests import Request
from starlette.responses import RedirectResponse
import models
import schemas
from websocket import ConnectionManager

from sqlalchemy.orm import Session
from database import get_db ,Base,engine

from typing import Optional,List
import oauth
from fastapi.security import OAuth2PasswordRequestForm
from hashing import Hash
import JWTtoken

from fastapi.templating import Jinja2Templates



app = FastAPI()

models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")

manager = ConnectionManager()

@app.get("/root")
def get_root():
    return {"fastapi":"test"}

@app.get("/chat")
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

async def get_token(
    websocket: WebSocket,
    token: Optional[str] = Cookie(None),
):
    if token is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
    return token


@app.websocket("/username/{username}/ws")
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

@app.get("/")
def login_get_view(
    request:Request,
    Authentication: Optional[str] = Cookie(None),
    ):

    user = JWTtoken.verify_token(Authentication)

    if Authentication is None or user is None:
        raise RedirectResponse("/login",307)

    return templates.TemplateResponse("home.html",{
        "request":request,
        "user":user.username,
    })

@app.get("/login")
def login_get_view(request:Request):
    return templates.TemplateResponse("auth/login.html",{
        "request":request,
    })

@app.post("/login")
def login_post_view(request:Request,
    username:str=Form(...),
    password:str=Form(...),
    db:Session=Depends(get_db)
    ):
    print(username,password)
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user :
        raise HTTPException(404,f"Invalid Credentials")
    
    if not Hash.verify(user.password,password):
        raise HTTPException(404,f"Incorrect password")

    access_token = JWTtoken.create_access_token(data={"username":user.username,"id":user.id})
    response = RedirectResponse("/",302)
    response.set_cookie("Authentication",access_token)
    return response

    # return templates.TemplateResponse("auth/login.html",{
    #     "request":request,
    # })

@app.get("/signup")
def signup_get_view(request:Request):
    return templates.TemplateResponse("auth/signup.html",{
        "request":request,
    })

@app.post("/signup")
def signup_post_view(request:Request,
    username:str=Form(...),
    password:str=Form(...),
    password_confirm:str=Form(...),
    db:Session = Depends(get_db)):
    print(username,password)
    if password != password_confirm:
        return templates.TemplateResponse("auth/signup.html",{
        "request":request,
    })
    user = {
        "username":username,
        "password":password,
    } 
    new_user = models.User(username=user['username'],password=Hash.bcrypt(user['password']))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    response =  RedirectResponse('/login',302)
    return response

@app.get("/logout")
def signup_post_view(
    request:Request,
    ):
    response =  RedirectResponse('/login',302)
    response.delete_cookie("Authentication")
    return response




@app.post('/user/',tags=["User"])
def user_register(request:schemas.User ,db:Session = Depends(get_db)):
    new_user = models.User(username=request.username,password=Hash.bcrypt(requestpassword))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {
        "status":"ok",
        "data":f"Hello {new_user.username}"
    }


@app.get('/user/',tags=["User"])
def user_get_all(db:Session = Depends(get_db)):
    users = db.query(models.User).all()
    return users

@app.get('/user/{username}',tags=["User"])
def user_get_by_username(username,db:Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == username).first()
    return user

@app.delete('/user/{username}',tags=["User"])
def user_delete_by_username(username,db:Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == username).delete()
    db.commit()
    if user :
        return "Delete Successfuly!"
    raise HTTPException(404,"User Not Found!")




@app.post('/user_login',tags=["Login"])
def user_login(request:OAuth2PasswordRequestForm = Depends(),db:Session=Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == request.username).first()
    if not user :
        raise HTTPException(404,f"Invalid Credentials")
    
    if not Hash.verify(user.password,request.password):
        raise HTTPException(404,f"Incorrect password")

    access_token = JWTtoken.create_access_token(data={"username":user.username,"id":user.id})
    return {"access_token":access_token,"token_type":"bearer"}

@app.post('/user/me',tags=["Login"])
async def get_current_user(current_user:models.User = Depends(oauth.get_current_user)):
    return current_user







  