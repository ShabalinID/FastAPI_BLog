from datetime import datetime
from fastapi import Request, Depends, APIRouter
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
# TODO import PyOpenGraph

from database.core import SqliteDatabase
from models.models import MessageForm, MessageDB
import auth

router = APIRouter(
    prefix="/blog",
    tags=["blog"],
    responses={404: {"description": "Not found"}},
)

router.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

database_name = "sqlite.db"
database = SqliteDatabase(database_name=database_name)

@router.get("/")
async def blog_list(request: Request):
    messages = await database.get_all_messages()
    return templates.TemplateResponse("blog/list.html", {"request": request,
                                                         "messages": messages})


@router.get("/new_message")
async def get_new_message(request: Request):
    author = await auth.get_user_name()
    return templates.TemplateResponse("blog/new_message.html", {"request": request,
                                                                "author": author})


@router.post("/new_message")
async def post_new_message(request: Request,
                           form_data: MessageForm = Depends()):
    author = await auth.get_user_name()
    if form_data.message_is_empty():
        status = "You need to feel one of the field for new Post!"
    else:
        message = MessageDB(
            author=author,
            published=datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            body=form_data.body,
            link=form_data.link
        )
        await database.insert_new_message(message)
        status = "New message was added!"
    return templates.TemplateResponse("blog/new_message.html", {"request": request,
                                                                "author": author,
                                                                "status": status})


@router.get("/{message_id}")
async def get_message_detail(request: Request,
                             message_id: int):
    db_result = await database.get_message_details(message_id=message_id)
    if db_result:
        message = MessageDB(**db_result)
        return templates.TemplateResponse("blog/detail.html", {"request": request,
                                                               "message": message})
    else:
        return RedirectResponse(url='/blog/')
