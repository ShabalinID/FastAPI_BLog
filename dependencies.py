from fastapi import Form, UploadFile, File, Depends
from typing import Optional, List
from pydantic import HttpUrl

import security
from models import User


class MessageForm:
    def __init__(self,
                 author: User = Depends(security.get_current_user),
                 body: Optional[str] = Form(None, description="Text body for new message:"),
                 link: Optional[HttpUrl] = Form(None, description="Share a url link:"),
                 media_list: Optional[List[UploadFile]] = File(None,
                                                               description="Upload multiple images or video files \n"
                                                                           "(!Be sure to uncheck empty value box! "
                                                                           "In other cases it will raise an error)",
                                                               ),
                 ):
        self.author = author
        self.body = body
        self.link = link
        self.media_list = media_list

    def message_is_empty(self):
        if not (self.body or self.link or self.media_list):
            return True
        else:
            return False

    def have_media(self):
        if self.media_list:
            if self.media_list[0].filename:
                return True
            else:
                return False

    def valid_media_mime(self):
        if self.media_list:
            for media in self.media_list:
                if not media.content_type.startswith('image/') or not media.content_type.startswith('video/'):
                    return False
            return True
        else:
            return False
