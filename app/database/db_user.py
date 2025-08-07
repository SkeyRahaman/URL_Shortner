from app.schemas import UserDetails
from app.database.models import DBUser
from fastapi.exceptions import HTTPException
from fastapi import status
from fastapi.concurrency import run_in_threadpool
from app.database.hash import PasswordHasher

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

async def check_email_address(db: AsyncSession,email : str):
    result = await db.execute(select(DBUser).filter(DBUser.email == email))
    user = result.scalars().first()
    return bool(user)

async def check_username_exist(db: AsyncSession,username : str):
    result = await db.execute(select(DBUser).filter(DBUser.user_name == username))
    user = result.scalars().first()
    return bool(user)

async def create_user(db: AsyncSession, data : UserDetails):
    new_user = DBUser(
        user_name = data.user_name,
        email = data.email,
        password = await run_in_threadpool(PasswordHasher.get_password_hash(data.password)
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

async def update_user(db: AsyncSession, user : DBUser,email:str,password:str):
    result = await db.execute(select(DBUser).filter(DBUser.id == user.id))
    db_user = result.scalars().first()
    if db_user:
        if email:
            db_user.email = email
        if password:
            db_user.password = PasswordHasher.get_password_hash(password)
        await db.commit()
        await db.refresh(db_user)
        return db_user
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User Not found.")
    
async def delete_user(user : DBUser, db: AsyncSession):
    result = await db.execute(select(DBUser).filter(DBUser.email == user.email))
    db_user = result.scalars().first()
    if db_user:
        await db.delete(db_user)
        await db.commit()
        return {"Message" : "User Deleted."}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User Not found.")
    
async def get_user(user_name:str, db: AsyncSession):
    result = await db.execute(select(DBUser).filter(DBUser.user_name == user_name))
    user = result.scalars().first()
    if user:
        return user
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User Not found.")
