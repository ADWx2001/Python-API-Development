from pydantic import BaseModel,EmailStr
from datetime import datetime

class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True

class PostCreate(PostBase):
    pass
    
#this class is the response to frontend
class Post(PostBase):
    # id: int
    # created_at: datetime

    class Config:
        form_attributes = True
         #add this config class for help pydantic model, because we use sql alchemy, it returns data that can't convert to the
                        #python dic type, pydantic model work with dictionaries, so we need to add this config to convert it to py dictionary

class UserBase(BaseModel):
    email: EmailStr
    password: str

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int
    created_at: datetime

    class Config:
        form_attributes = True