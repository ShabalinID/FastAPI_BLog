from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException, status, APIRouter, Response, Request
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from jose import JWTError, jwt, ExpiredSignatureError
from passlib.context import CryptContext

from database.users import UserDatabase
from models import User, Token, TokenData

SECRET_KEY = "dc56abe097584455ea1b39cc26b08d3113554776679ac4d5acd4504fd6a297d3"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

database_name = "sqlite.db"
users_database = UserDatabase(database_name=database_name)

router = APIRouter()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(username: str):
    user_db = users_database.get_user(username=username)
    if user_db:
        user = User(**user_db)
        return user
    else:
        return


def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if verify_password(password, user.hashed_password):
        return user
    return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_access_token(user: User,
                     response: Response):
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username},
                                       expires_delta=access_token_expires)
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return {"access_token": access_token, "token_type": "bearer"}


def get_current_user(request: Request):
    token = request.cookies.get('access_token')
    if token is not None:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception
            token_data = TokenData(username=username)
        except ExpiredSignatureError:
            response = JSONResponse()
            response.delete_cookie(key="access_token")
            return None
        except JWTError:
            raise credentials_exception
        user = get_user(username=token_data.username)
        if user is None:
            raise credentials_exception
        return user.username
    else:
        return None


def log_out(response: Response):
    response.delete_cookie(key="access_token")


