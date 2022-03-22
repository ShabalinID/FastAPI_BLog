from fastapi import Request, Depends, APIRouter, Response, Cookie
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse


from database.users import UserDatabase
from models import User
import security

router = APIRouter(
    prefix="/user",
    tags=["user"],
    responses={404: {"description": "Not found"}},
)

database_name = "sqlite.db"
users_database = UserDatabase(database_name=database_name)

router.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@router.get("/login", response_class=HTMLResponse)
async def get_login_form(request: Request):
    authorized = False
    if not authorized:
        return templates.TemplateResponse("users/login.html", {"request": request})
    else:
        return "Already authorized"


@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(security.get_current_user)):
    return current_user


@router.post("/login", response_class=HTMLResponse)
async def post_login_form(request: Request,
                          response: Response,
                          form_data: OAuth2PasswordRequestForm = Depends()):
    authorized_user = security.authenticate_user(username=form_data.username,
                                                 password=form_data.password)
    if not authorized_user:
        login_status = "False"
    else:
        login_status = "True"
        access_token = security.get_access_token(authorized_user)
        print(access_token)
        response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return templates.TemplateResponse("users/login.html", {"request": request,
                                                           "login_status": login_status})


@router.get("/singup", response_class=HTMLResponse)
async def get_singup_form(request: Request):
    authorized = False
    if not authorized:
        return templates.TemplateResponse("users/register.html", {"request": request})
    else:
        return "Already authorized"


@router.post("/singup", response_class=HTMLResponse)
async def post_singup_form(request: Request,
                           form_data: OAuth2PasswordRequestForm = Depends()):
    if await users_database.username_is_taken(form_data.username):
        success = False
    else:
        hashed_password = await security.get_password_hash(form_data.password)
        user = User(
            username=form_data.username,
            hashed_password=hashed_password
        )
        await users_database.insert_new_user(user)
        success = True
    return templates.TemplateResponse("users/register.html", {"request": request,
                                                              "success": success})
