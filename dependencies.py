from fastapi import Form, UploadFile, File
from typing import Optional, List
from pydantic import HttpUrl


class MessageForm:
    def __init__(self,
                 body: Optional[str] = Form(""),
                 link: Optional[HttpUrl] = Form(None),
                 media_list: Optional[List[UploadFile]] = None,
                 ):
        self.body = body
        self.link = link
        self.media_list = media_list

    def message_is_empty(self):
        if not (self.body or self.link or self.media_list[0].filename):
            return True
        else:
            return False

    def have_media(self):
        if self.media_list[0].filename:
            return True
        else:
            return False