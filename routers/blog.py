from datetime import datetime
from fastapi import Request, Depends, APIRouter
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
# TODO import PyOpenGraph

from database.blog import MessagesDatabase
from models import Message
from dependencies import MessageForm
import security

router = APIRouter(
    prefix="/blog",
    tags=["blog"],
    responses={404: {"description": "Not found"}},
)

router.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

database_name = "sqlite.db"
message_database = MessagesDatabase(database_name=database_name)


@router.get("/", response_class=HTMLResponse)
async def blog_list(request: Request):
    messages = await message_database.get_all_messages()
    return templates.TemplateResponse("blog/list.html", {"request": request,
                                                         "messages": messages})


@router.get("/new_message", response_class=HTMLResponse)
async def get_new_message(request: Request):
    author = await security.get_user_name()
    return templates.TemplateResponse("blog/new_message.html", {"request": request,
                                                                "author": author})


@router.post("/new_message", response_class=HTMLResponse)
async def post_new_message(request: Request,
                           form_data: MessageForm = Depends()):
    author = await security.get_user_name()
    if form_data.message_is_empty():
        status = "You need to feel one of the field for new Post!"
    else:
        message = Message(
            author=author,
            published=datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            body=form_data.body,
            link=form_data.link
        )
        await message_database.insert_new_message(message)
        status = "New message was added!"
    return templates.TemplateResponse("blog/new_message.html", {"request": request,
                                                                "author": author,
                                                                "status": status})


@router.get("/{message_id}", response_class=HTMLResponse)
async def get_message_detail(request: Request,
                             message_id: int):
    db_result = await message_database.get_message_details(message_id=message_id)
    if db_result:
        message = Message(**db_result)
        return templates.TemplateResponse("blog/detail.html", {"request": request,
                                                               "message": message})
    else:
        return RedirectResponse(url='/blog/')
