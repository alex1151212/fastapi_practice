
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
    Request,
    Response
)
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from starlette.responses import RedirectResponse
import models
import schemas
from websocket import ConnectionManager
from aiortc import (
    RTCIceCandidate,
    RTCPeerConnection,
    RTCSessionDescription,
    VideoStreamTrack,
)

from sqlalchemy.orm import Session
from database import get_db ,Base,engine

from typing import Optional,List
from fastapi.security import OAuth2PasswordRequestForm
from hashing import Hash
import JWTtoken

from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from router.user import app_user
from router.chatroom import app_chatroom


app = FastAPI(
    title="Fastapi Project" ,
    description="",
    version="Beta 1.0.0",
    docs_url="/docs",
    redoc_url='/redocs',
)

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://192.168.1.101:3000",
]

app.include_router(app_user,prefix='/user')
app.include_router(app_chatroom)

models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="./templates/static"), name="static")

# @app.middleware("http")
# async def Auth(
#     request: Request,
#     Authentication:Optional[str]=Cookie(None)
#     ):
#     if Authentication is None :
#         return RedirectResponse("/login")

    # user = JWTtoken.verify_token(Authentication)
    
    # if user is None:
    #     HTTPException(401)


@app.get("/root")
def get_root():
    return {"fastapi":"test"}

manager = ConnectionManager()

@app.get('/webrtc')
def webrtc_render(request:Request):

    return templates.TemplateResponse("webrtc.html",{
        "request":request,
    })
@app.websocket("/socket.io")
async def websocket_endpoint(websocket: WebSocket, username: str):
    await manager.connect()



@app.get("/")
def login_get_view(
    request:Request,
    Authentication: Optional[str] = Cookie(None),
    ):

    if Authentication is None:
        return RedirectResponse("/login",307)

    user = JWTtoken.verify_token(Authentication)

    if user is None:
        return RedirectResponse("/login",307)

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
def signup_post_view():
    response =  RedirectResponse('/login',302)
    response.delete_cookie("Authentication")
    return response



#........................................................................



@app.post("/business")
def business_register(request:schemas.Business,db:Session=Depends(get_db)):
    new_business = models.Business(
        business_name = request.business_name,
        city = request.city,
        business_description=request.business_description,
        logo = request.logo,
        owner = request.owner,
    )
    db.add(new_business)
    db.commit()
    db.refresh(new_business)
    return {
        "status":"ok",
        "data":f"Hello {new_business.business_name}"
    }

@app.get("/business")
def business_get_all(db=Depends(get_db)):
    business = db.query(models.Business).all()
    return business

@app.get("/business/{business_name}")
def business_get_all(business_name,db:Session=Depends(get_db)):
    business = db.query(models.Business).filter(models.Business.business_name==business_name).first()
    return business

@app.delete("/business/{business_name}")
def business_delete_by_businessName(business_name,db:Session=Depends(get_db)):
    business = db.query(models.Business).filter(models.Business.business_name == business_name).delete()
    db.commit()
    if business :
        return f"Delete Successfuly! {business}"
    raise HTTPException(404,f"Business Not Found!{business}")

@app.post("/item")
def item_register(request:schemas.Item,db:Session=Depends(get_db)):
    item = models.Item(
        name = request.name,
        category = request.category,
        price = request.price,
        product_image = request.product_image,
        business = request.business,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return {
        "status":"ok",
        "data":f"Create Successfuly!"
    }
    
@app.get('/item/{item_name}')
def item_get_by_name(item_name,db:Session=Depends(get_db)):
    item = db.query(models.Item).filter(models.Item.name == item_name).all()
    if item is None :
        raise HTTPException(404,f"item Not Found!{item_name}")
    return item

@app.get('/item/')
def item_get_all(db:Session=Depends(get_db)):
    item = db.query(models.Item).all()
    if item is None :
        raise HTTPException(404,f"item Not Found!")
    return item
