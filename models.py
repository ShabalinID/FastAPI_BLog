from typing import Optional, List
from pydantic import BaseModel, HttpUrl


class Message(BaseModel):
    message_id: Optional[int] = None
    author: str
    published: str
    body: Optional[str] = None
    link: Optional[HttpUrl] = None


class Media(BaseModel):
    media_id: Optional[int] = None
    media_url: str
    media_type: str
    message_id: int


class LinkDetail(BaseModel):
    link_image: Optional[HttpUrl] = None
    link_description: Optional[str] = None


class MessageDetail(Message):
    link_detail: Optional[LinkDetail] = None
    media_list: Optional[List[Media]] = None
    message_likes: Optional[int] = 0


class User(BaseModel):
    user_id: Optional[int] = None
    username: str
    hashed_password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class Like(BaseModel):
    like_id: Optional[int] = None
    message_id: int
    username: str
