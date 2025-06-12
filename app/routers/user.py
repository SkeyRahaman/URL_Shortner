from fastapi import APIRouter, Depends, status
from app.schemas import UserDetails, UserDetailsUpdatable, UserDisplay
from sqlalchemy.orm import Session
from app.database import get_db
from app.database import db_user
from app.database.models import DBUser
from app.authentication.authentication import get_curren_user


router = APIRouter(
    prefix="/user",
    tags=["User"]
)


@router.post("/new_user", response_model=UserDetails, status_code=status.HTTP_201_CREATED)
def create_new_user(data : UserDetails, db: Session = Depends(get_db)):
    return db_user.create_user(db,data)

@router.put("/update_user", response_model=UserDetails)
def update_user(email:str = None, password:str = None,db: Session = Depends(get_db), user : DBUser = Depends(get_curren_user)):
    return db_user.update_user(user=user,email=email,password=password,db=db)

@router.post("/DELETE_USER")
def delete_user(user : DBUser = Depends(get_curren_user), db:Session = Depends(get_db)):
    return db_user.delete_user(user=user, db=db)

@router.get("/me", response_model=UserDisplay)
def get_current_user(user: DBUser = Depends(get_curren_user)):
    return user