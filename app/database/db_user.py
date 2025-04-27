from sqlalchemy.orm import Session
from app.schemas import UserDetails
from app.database.models import DBUser
from fastapi.exceptions import HTTPException
from fastapi import status
from app.database.hash import Hash

def check_email_address(db: Session,email : str):
    user = db.query(DBUser).filter(DBUser.email == email).first()
    if user:
        return True 
    else :
        return False

# Create User
def create_user(db: Session, data : UserDetails):
    if check_email_address(db=db, email=data.email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered.")
    new_user = DBUser(
        user_name = data.user_name,
        email = data.email,
        password = Hash.dcrypt(data.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user) #to generate id
    return new_user

def update_user(user : DBUser,email:str,password:str, db:Session):
    db_user = db.query(DBUser).filter(DBUser.id == user.id).first()
    if user:
        if email:
            user.email = email
        if password:
            user.password = Hash.dcrypt(password)
        db.commit()
        return db_user
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User Not found.")
    
def delete_user(user : DBUser, db: Session):
    db_user = db.query(DBUser).filter(DBUser.id == user.id).first()
    if user:
        db.delete(db_user)
        db.commit()
        return {"Message" : "User Deleted."}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User Not found.")
    
def get_user(user_name:str, db:Session):
    user = db.query(DBUser).filter(DBUser.user_name == user_name).first()
    if user:
        return user
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User Not found.")





