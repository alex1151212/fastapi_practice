from sqlalchemy import Boolean, Column, ForeignKey, Integer,String,func, Date , DateTime,Text,Numeric
from sqlalchemy.orm import relationship

from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(16),unique=True,nullable=False,comment="使用者名稱")
    password = Column(String(16),nullable=False,comment="密碼")

    is_verified = Column(Boolean, default=False)

    #items = relationship("Item", back_populates="owner")

    created_at = Column(DateTime,server_default=func.now(),comment="創建時間")
    updated_at = Column(DateTime,server_default=func.now(),onupdate=func.now() ,comment="更新時間")


class Business(Base):
    __tablename__ = "business"

    id = Column(Integer, primary_key=True, index=True)
    business_name = Column(String(16),nullable=False,unique=True)
    city = Column(String(16),nullable=False)
    business_description = Column(Text(16),nullable=False)
    logo = Column(String(200),nullable=False,default="default.jpg")
    owner = Column(Integer,ForeignKey('users.id'))
    items = relationship("Item")


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(16),nullable=False,unique=True,index=True)
    Category = Column(String(30),index=True)
    price = Column(Numeric(30),index=True)
    product_image = Column(String(200),nullable=False,default="productDefault.jpg")
    business = Column(Integer,ForeignKey('business.id'))



      