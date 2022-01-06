from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import Depends,HTTPException

import  JWTtoken



oauth2_scheme = OAuth2PasswordBearer(tokenUrl="user_login")

def get_current_user(token:str =Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return JWTtoken.verify_token(token,credentials_exception)