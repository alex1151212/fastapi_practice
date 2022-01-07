from fastapi.routing import APIRouter
from fastapi import Depends,HTTPException
from sqlalchemy.orm import Session

import schemas,models
from database import get_db
from hashing import Hash

app_user = APIRouter(
    
)



@app_user.post('/',tags=["User"])
def user_register(request:schemas.User ,db:Session = Depends(get_db)):
    new_user = models.User(username=request.username,password=Hash.bcrypt(requestpassword))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {
        "status":"ok",
        "data":f"Hello {new_user.username}"
    }


@app_user.get('/',tags=["User"])
def user_get_all(db:Session = Depends(get_db)):
    users = db.query(models.User).all()
    return users

@app_user.get('/{username}',tags=["User"])
def user_get_by_username(username,db:Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == username).first()
    return user

@app_user.delete('/{username}',tags=["User"])
def user_delete_by_username(username,db:Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == username).delete()
    db.commit()
    if user :
        return "Delete Successfuly!"
    raise HTTPException(404,"User Not Found!")
