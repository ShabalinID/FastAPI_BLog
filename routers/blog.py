from datetime import datetime

import aiohttp
from bs4 import BeautifulSoup
from decouple import config
from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import Page, paginate, add_pagination
from starlette import status

import security
from database.blog import BlogDatabase
from dependencies import MessageForm
from models import Message, MessageDetail, LinkDetail, User

router = APIRouter(
    prefix="/blog",
    tags=["blog"],
)


database_path = config("database_path")
blog_database = BlogDatabase(database_path=database_path)


@router.get("/list", response_model=Page[Message], description="Endpoint for browsing list of blog messages "
                                                               "with pagination.")
async def get_blog_list():
    messages = await blog_database.get_all_messages()
    return paginate(messages)


add_pagination(router)


@router.post("/new_message", response_model=Message, description="Form for uploading new message in blog. "
                                                                 "One of the field must be filled. "
                                                                 "Bearer authorization token required!")
async def new_message(form_data: MessageForm = Depends()):
    if form_data.message_is_empty() or form_data.valid_media_mime():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid form!",
            headers={"New message": "Unprocessable Entity"},
        )
    else:
        message = Message(
            author=form_data.author,
            published=datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            body=form_data.body,
            link=form_data.link
        )
        await blog_database.insert_new_message(message)
        if form_data.have_media():
            await blog_database.save_message_media(message=message,
                                                   media_list=form_data.media_list)
        return message


@router.get("/detail/{message_id}", response_model=MessageDetail, description="Message detail shown by pointing "
                                                                              "message id")
async def get_message_detail(message_id: int):
    message = await blog_database.get_message_details(message_id=message_id)
    if message:
        media_list = await blog_database.get_media_list(message_id=message_id)
        link_url = Message(**message).link
        link_detail = await get_link_detail(url=link_url)
        message_likes = await blog_database.get_message_likes(message_id=message_id)
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
            url_og_image = None
            url_og_description = None
            soup_find_image = soup.find("meta", property="og:image")
            soup_find_description = soup.find("meta", property="og:image")
            if soup_find_image:
                url_og_image = soup_find_image.get('content')
            if soup_find_description:
                url_og_description = soup_find_description.get('content')
            link_detail = LinkDetail(link_image=url_og_image,
                                     link_description=url_og_description)
            return link_detail


@router.get("/delete/{message_id}", description="Delete message by pointing message_id. "
                                                "Your must be an author of this message! "
                                                "Bearer authorization token required!")
async def delete_message(message_id: int,
                         current_user: User = Depends(security.get_current_user)):
    exception200 = HTTPException(status_code=200, detail="Message has been deleted")
    exception401 = HTTPException(status_code=401, detail="Wrong authorization token")
    exception404 = HTTPException(status_code=404, detail="Item not found")

    message_author = await blog_database.is_author(message_id=message_id)
    if message_author is None:
        raise exception404
    elif message_author[0] == current_user:
        await blog_database.delete_message(message_id=message_id)
        raise exception200
    else:
        raise exception401


@router.get("/like_message/{message_id}", description="Endpoint for like/unlike message by message_id. "
                                                      "Bearer authorization token required!")
async def set_message_like(message_id: int,
                           current_user: User = Depends(security.get_current_user)):

    exception200_like = HTTPException(status_code=200, detail="You like the message")
    exception200_unlike = HTTPException(status_code=200, detail="You unlike the message")
    exception401 = HTTPException(status_code=401, detail="Wrong authorization token")
    exception404 = HTTPException(status_code=404, detail="Item not found")

    if current_user is None:
        raise exception401
    message = await blog_database.get_message_details(message_id=message_id)
    if message is None:
        raise exception404
    else:
        if await blog_database.message_is_liked(message_id=message_id, username=current_user):
            await blog_database.unlike_message(message_id=message_id, username=current_user)
            raise exception200_unlike
        else:
            await blog_database.insert_like(message_id=message_id, username=current_user)
            raise exception200_like
