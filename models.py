from typing import Optional
from pydantic import BaseModel


class Message(BaseModel):
    message_id: Optional[int] = None
    author: str
    published: str
    body: Optional[str] = ""
    link: Optional[str] = None


class User(BaseModel):
    user_id: Optional[int] = None
    username: str
    hashed_password: str
