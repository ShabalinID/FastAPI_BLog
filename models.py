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


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class Media(BaseModel):
    media_id: Optional[int] = None
    media_url: str
    media_type: str
    message_id: int

