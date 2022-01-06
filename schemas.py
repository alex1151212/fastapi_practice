from sqlalchemy.sql.expression import true
from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    username: str
    password:str

    class Config():
        orm_mode = True

class TokenData(BaseModel):
    username: Optional[str] = None

class User_obj(BaseModel):
    username:str
    id:int
    
    class Config():
        orm_mode = True