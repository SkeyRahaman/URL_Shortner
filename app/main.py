from fastapi import FastAPI
from app.authentication import auth_router
from app.database import engine, models
from app.routers import user,url

app = FastAPI()
models.Base.metadata.create_all(engine)

app.include_router(auth_router.router)
app.include_router(user.router)
app.include_router(url.router)

