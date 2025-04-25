from fastapi import FastAPI
from authentication import auth_router
from database import engine
from database import models
from routers import user,url

app = FastAPI()
models.Base.metadata.create_all(engine)

app.include_router(auth_router.router)
app.include_router(user.router)
app.include_router(url.router)

