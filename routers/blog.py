from fastapi import Depends, APIRouter, HTTPException, status
from fastapi_pagination import Page, add_pagination, paginate

from datetime import datetime
from bs4 import BeautifulSoup
import aiohttp
from decouple import config

from database.blog import BlogDatabase
from models import Message, MessageDetail, LinkDetail, User
from dependencies import MessageForm
import security


router = APIRouter(
    prefix="/blog",
    tags=["blog"],
)


database_path = config("database_path")
blog_database = BlogDatabase(database_path=database_path)


@router.get("/list", response_model=Page[Message])
async def get_blog_list():
    messages = await blog_database.get_all_messages()
    return paginate(messages)


add_pagination(router)


@router.post("/new_message")
async def new_message(form_data: MessageForm = Depends()):
    if form_data.message_is_empty() or form_data.valid_media_mime():
        credentials_exception = HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid form!",
            headers={"New message": "Unprocessable Entity"},
        )
        raise credentials_exception
    else:
        message = Message(
            author=form_data.author,
            published=datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            body=form_data.body,
            link=form_data.link
        )
        blog_database.insert_new_message(message)
        if form_data.have_media():
            await blog_database.save_message_media(message=message,
                                                   media_list=form_data.media_list)
        raise HTTPException(status_code=200, detail="Message has been deleted")


@router.get("/detail/{message_id}", response_model=MessageDetail)
async def get_message_detail(message_id: int):
    message = blog_database.get_message_details(message_id=message_id)
    if message:
        media_list = blog_database.get_media_list(message_id=message_id)
        link_url = Message(**message).link
        link_detail = await get_link_detail(url=link_url)
        message_likes = blog_database.get_message_likes(message_id=message_id)
        message_detail = MessageDetail(**message,
                                       media_list=media_list,
                                       link_detail=link_detail,
                                       message_likes=message_likes)
        return message_detail


async def get_link_detail(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url) as response:
            html = await response.text()
            soup = BeautifulSoup(html, 'lxml')
            url_og_image = soup.find("meta", property="og:image").get('content')
            url_og_description = soup.find("meta", property="og:description").get('content')
            link_detail = LinkDetail(link_image=url_og_image,
                                     link_description=url_og_description)
            return link_detail


@router.get("/delete/{message_id}")
async def delete_message(message_id: int,
                         current_user: User = Depends(security.get_current_user)):
    message_author = blog_database.is_author(message_id=message_id)
    if message_author is None:
        raise HTTPException(status_code=404, detail="Item not found")
    if message_author == current_user:
        blog_database.delete_message(message_id=message_id)
        raise HTTPException(status_code=200, detail="Message has been deleted")
    else:
        raise HTTPException(status_code=401, detail="Wrong authorization token")


@router.get("/like_message/{message_id}")
async def set_message_like(message_id: int,
                           current_user: User = Depends(security.get_current_user)):
    if current_user is None:
        raise HTTPException(status_code=401, detail="Wrong authorization token")
    message = blog_database.get_message_details(message_id=message_id)
    if message is None:
        raise HTTPException(status_code=404, detail="Item not found")
    else:
        if blog_database.message_is_liked(message_id=message_id, username=current_user):
            blog_database.unlike_message(message_id=message_id, username=current_user)
            raise HTTPException(status_code=200, detail="You unlike the message")
        else:
            blog_database.insert_like(message_id=message_id, username=current_user)
            raise HTTPException(status_code=200, detail="You like the message")