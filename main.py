from datetime import datetime
from fastapi import FastAPI, Request, Depends, APIRouter
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordRequestForm
# TODO import PyOpenGraph

from database.core import SqliteDatabase
from models.models import MessageForm, User, MessageDB
import auth

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

database_name = "sqlite.db"
database = SqliteDatabase(database_name=database_name)


@app.get("/")
async def root():
    return RedirectResponse(url='/blog/')


@app.get("/blog/")
async def blog_list(request: Request):
    messages = await database.get_all_messages()
    return templates.TemplateResponse("blog/list.html", {"request": request,
                                                         "messages": messages})


@app.get("/blog/new_message")
async def get_new_message(request: Request):
    author = await auth.get_user_name()
    return templates.TemplateResponse("blog/new_message.html", {"request": request,
                                                                "author": author})


@app.post("/blog/new_message")
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


@app.get("/blog/{message_id}")
async def get_message_detail(request: Request,
                             message_id: int):
    db_result = await database.get_message_details(message_id=message_id)
    if db_result:
        message = MessageDB(**db_result)
        return templates.TemplateResponse("blog/detail.html", {"request": request,
                                                               "message": message})
    else:
        return RedirectResponse(url='/blog/')


@app.get("/user/login")
async def get_login_form(request: Request):
    authorized = False
    if not authorized:
        return templates.TemplateResponse("auth/login.html", {"request": request})
    else:
        return "Already authorized"


@app.post("/user/login")
async def post_login_form(request: Request,
                          form_data: OAuth2PasswordRequestForm = Depends()):
    hashed_password = await database.get_user_password(username=form_data.username)
    login_status = await auth.verify_password(plain_password=form_data.password,
                                              hashed_password=hashed_password)
    return templates.TemplateResponse("auth/login.html", {"request": request,
                                                          "login_status": login_status})


@app.get("/user/singup")
async def get_singup_form(request: Request):
    authorized = False
    if not authorized:
        return templates.TemplateResponse("auth/register.html", {"request": request})
    else:
        return "Already authorized"


@app.post("/user/singup")
async def post_singup_form(request: Request,
                           form_data: OAuth2PasswordRequestForm = Depends()):
    if await database.username_is_taken(form_data.username):
        success = False
    else:
        hashed_password = await auth.get_password_hash(form_data.password)
        user = User(
            username=form_data.username,
            hashed_password=hashed_password
        )
        await database.insert_new_user(user)
        success = True
    return templates.TemplateResponse("auth/register.html", {"request": request,
                                                             "success": success})
