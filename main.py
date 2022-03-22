from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
# TODO import PyOpenGraph

from routers import blog, users

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.include_router(blog.router)
app.include_router(users.router)


@app.get("/")
async def root():
    return RedirectResponse(url='/blog/')
