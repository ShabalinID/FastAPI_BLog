from decouple import config
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from starlette import status

import security
from database.users import UserDatabase
from models import User, Token

router = APIRouter(
    prefix="/user",
    tags=["user"],
)

database_path = config("database_path")
users_database = UserDatabase(database_path=database_path)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="user/login")


@router.post("/singup", description="Sing up for adding new user in database using OAuth2PasswordRequestForm.")
async def post_singup_form(form_data: OAuth2PasswordRequestForm = Depends()):
    if await users_database.username_is_taken(form_data.username):
        return {"success": "False", "detail": "username is already taken"}
    else:
        hashed_password = security.get_password_hash(form_data.password)
        user = User(
            username=form_data.username,
            hashed_password=hashed_password
        )
        await users_database.insert_new_user(user)
        return {"success": "True", "detail": "successfully singed up"}


@router.post("/login", response_model=Token, description="Login for response JWT using OAuth2PasswordRequestForm.")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await security.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = await security.get_access_token(user=user)
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", description="Get username using OAuth2PasswordRequestForm.")
async def get_current_user(current_user: User = Depends(security.get_current_user)):
    return current_user
