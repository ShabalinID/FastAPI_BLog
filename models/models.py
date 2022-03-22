from fastapi import Form, UploadFile
from typing import Optional, List
from pydantic import BaseModel, HttpUrl


class MessageForm:
    def __init__(self,
                 body: Optional[str] = Form(""),
                 link: Optional[HttpUrl] = Form(None),
                 media_list: Optional[List[UploadFile]] = Form(None),
                 ):
        self.body = body
        self.link = link
        self.media_list = media_list

    def message_is_empty(self):
        if not (self.body or self.link or self.media_list):
            return True
        return False


class MessageDB(BaseModel):
    message_id: Optional[int] = None
    author: str
    published: str
    body: Optional[str] = ""
    link: Optional[str] = None


class User(BaseModel):
    user_id: Optional[int] = None
    username: str
    hashed_password: str
