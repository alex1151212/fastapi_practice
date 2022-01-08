from sqlalchemy.sql.expression import true
from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    username: str
    password:str

    class Config():
        orm_mode = True

class User_obj(BaseModel):
    username:str
    id:int
    
    class Config():
        orm_mode = True

# class TokenData(BaseModel):
#     username: Optional[str] = None

class Business(BaseModel):
    business_name:str
    city:str
    business_description:Optional[str]
    logo:Optional[str]
    owner:str

class Item(BaseModel):
    name:str
    category:str
    price:str
    product_image:str
    business:str
