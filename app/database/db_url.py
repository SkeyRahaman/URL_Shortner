from sqlalchemy.orm import Session
import hashlib
import base64
from app.database.models import DBUrl
from config import Config
from fastapi.exceptions import HTTPException
from fastapi import status


def generate_short_code(original_url: str) -> str:
    """Generate a base64-encoded SHA-256 hash and truncate"""
    sha256 = hashlib.sha256(original_url.encode()).digest()
    encoded = base64.urlsafe_b64encode(sha256).decode().rstrip("=")
    return encoded[:Config.SHORT_URL_LENGTH]

def add_url(long_url:str, db:Session, user_id:int, description=""):
    new_url = DBUrl(
        long_url = long_url,
        short_url = generate_short_code(long_url),
        description = description,
        user_id = user_id
    )
    db.add(new_url)
    db.commit()
    db.refresh(new_url) #to generate id
    return new_url

def get_url(short_url : str, db:Session):
    url = db.query(DBUrl).filter(DBUrl.short_url == short_url).first()
    if url:
        return url
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="URL not found.")
    
# For GET /urls (list)
def get_user_urls(user_id: int, skip: int, limit: int, db: Session):
    return db.query(DBUrl).filter(DBUrl.user_id == user_id).offset(skip).limit(limit).all()

# In db_url.py
def update_url(
    short_url: str,
    new_long_url: str,
    new_description: str,  # Add this parameter
    user_id: int,
    db: Session
):
    url = db.query(DBUrl).filter(
        DBUrl.short_url == short_url,
        DBUrl.user_id == user_id
    ).first()
    
    if not url:
        raise HTTPException(status_code=404, detail="URL not found")
    
    url.long_url = new_long_url
    url.description = new_description  # Update description
    db.commit()
    db.refresh(url)
    return url

# For DELETE /urls/{short_url}
def delete_url(short_url: str, user_id: int, db: Session):
    url = db.query(DBUrl).filter(DBUrl.short_url == short_url, DBUrl.user_id == user_id).first()
    if not url:
        raise HTTPException(status_code=404, detail="URL not found or unauthorized")
    db.delete(url)
    db.commit()

# For DELETE /urls/{short_url}
def delete_url(short_url: str, user_id: int, db: Session):
    url = db.query(DBUrl).filter(DBUrl.short_url == short_url, DBUrl.user_id == user_id).first()
    if not url:
        raise HTTPException(status_code=404, detail="URL not found or unauthorized")
    db.delete(url)
    db.commit()
    return {"Message" : "URL Deleted."}
