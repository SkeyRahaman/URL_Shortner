from app.schemas import UserDetails
from app.database.models import DBUser
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional

from app.authentication.password_hash import PasswordHasher

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
        password = await run_in_threadpool(PasswordHasher.get_password_hash, data.password)
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

async def update_user(
    db: AsyncSession,
    user: DBUser,
    email: Optional[str] = None,
    password: Optional[str] = None
) -> Optional[DBUser]:
    """Update an existing user's email and/or password."""
    result = await db.execute(
        select(DBUser).filter(DBUser.id == user.id)
    )
    db_user = result.scalars().first()
    if not db_user:
        return None

    if email:
        db_user.email = email
    if password:
        db_user.password = PasswordHasher.get_password_hash(password)

    await db.commit()
    await db.refresh(db_user)
    return db_user


async def delete_user(
    user: DBUser,
    db: AsyncSession
) -> bool:
    """Delete a user by email. Returns True if deleted, False if not found."""
    result = await db.execute(
        select(DBUser).filter(DBUser.email == user.email)
    )
    db_user = result.scalars().first()
    if not db_user:
        return False

    await db.delete(db_user)
    await db.commit()
    return True
    
async def get_user(user_name:str, db: AsyncSession):
    result = await db.execute(select(DBUser).filter(DBUser.user_name == user_name))
    return result.scalars().first()
