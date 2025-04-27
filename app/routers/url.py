from fastapi import APIRouter, Depends, status
from app.authentication.authentication import get_curren_user
from app.schemas import UrlData, UrlDisplay
from sqlalchemy.orm import Session
from app.database import get_db, db_url
from app.database.models import DBUser
from fastapi.responses import RedirectResponse


router = APIRouter(
    prefix="/url",
    tags=["URL"],
)



@router.post("/create_short_url", response_model=UrlDisplay, status_code=status.HTTP_201_CREATED)
def create_short_url(url:str, description:str, db:Session = Depends(get_db),user : DBUser = Depends(get_curren_user)):
    return db_url.add_url(long_url=url, description=description, user_id=user.id, db=db)

@router.get("/get_url_object/{short_url}", response_model=UrlDisplay)
def get_short_url(short_url:str,db:Session=Depends(get_db)):
    return db_url.get_url(short_url=short_url, db=db)

@router.get("/{short_url}", response_model=UrlDisplay)
def get_short_url(short_url:str,db:Session=Depends(get_db)):
    long_url =  db_url.get_url(short_url=short_url, db=db).long_url
    return RedirectResponse(url=long_url, status_code=status.HTTP_302_FOUND)