from fastapi import FastAPI
from app.authentication import auth_router
from app.database import engine, models
from app.routers import user,url

app = FastAPI(
    title="URL_Shortner",
    description="This API powers a URL shortener app built with FastAPI."
)
models.Base.metadata.create_all(engine)

app.include_router(auth_router.router)
app.include_router(user.router)
app.include_router(url.router)

@app.get("/health")
async def health_check():
    return {"message": "HEALTHY"}