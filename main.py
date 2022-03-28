from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from routers import blog, users

app = FastAPI()
app.include_router(blog.router)
app.include_router(users.router)


@app.get("/")
async def root():
    return RedirectResponse(url='/docs/')
