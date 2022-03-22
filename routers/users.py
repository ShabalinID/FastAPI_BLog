from fastapi import Request, Depends, APIRouter
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse, RedirectResponse

from database.users import UserDatabase
from models import User
import security


router = APIRouter(
    prefix="/user",
    tags=["user"],
    default_response_class=HTMLResponse,
)

database_name = "sqlite.db"
users_database = UserDatabase(database_name=database_name)

router.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@router.get("/login", response_class=HTMLResponse)
async def get_login_form(request: Request):
    current_user = security.get_current_user(request)
    if current_user is None:
        return templates.TemplateResponse("users/login.html", {"request": request})
    else:
        return RedirectResponse(url='/blog/')


@router.post("/login", response_class=HTMLResponse)
async def post_login_form(request: Request,
                          form_data: OAuth2PasswordRequestForm = Depends()):
    current_user = security.get_current_user(request)
    if current_user is None:
        authorized_user = security.authenticate_user(username=form_data.username,
                                                     password=form_data.password)
        if not authorized_user:
            response = templates.TemplateResponse("users/login.html", {"request": request,
                                                                       "login_status": False})
        else:
            response = templates.TemplateResponse("users/login.html", {"request": request,
                                                                       "login_status": True})
            security.get_access_token(response=response, user=authorized_user)
        return response
    else:
        return RedirectResponse(url='/blog/')


@router.get("/singup", response_class=HTMLResponse)
async def get_singup_form(request: Request):
    current_user = security.get_current_user(request)
    if current_user is None:
        return templates.TemplateResponse("users/register.html", {"request": request})
    else:
        return RedirectResponse(url='/blog/')


@router.post("/singup", response_class=HTMLResponse)
async def post_singup_form(request: Request,
                           form_data: OAuth2PasswordRequestForm = Depends()):
    current_user = security.get_current_user(request)
    if current_user is None:
        if users_database.username_is_taken(form_data.username):
            success = False
        else:
            hashed_password = security.get_password_hash(form_data.password)
            user = User(
                username=form_data.username,
                hashed_password=hashed_password
            )
            users_database.insert_new_user(user)
            success = True
        return templates.TemplateResponse("users/register.html", {"request": request,
                                                                  "success": success})
    else:
        return RedirectResponse(url='/blog/')


@router.get("/logout", response_class=HTMLResponse)
async def get_logaut(request: Request):
    current_user = security.get_current_user(request)
    response = RedirectResponse(url='/blog/')
    if current_user:
        security.log_out(response)
    return response
