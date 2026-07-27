from fastapi import Header, HTTPException, status

async def get_user_id(x_user_id: int = Header(...)) -> int:
    if x_user_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid X-User-Id header"
        )
    return x_user_id
