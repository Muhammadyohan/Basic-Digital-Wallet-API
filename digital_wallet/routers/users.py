from typing import Annotated

from jwt.exceptions import InvalidTokenError

from fastapi import Depends, APIRouter, HTTPException, status, Request


from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from .. import security

from .. import models
from ..models.user import User, CreateUser, UpdateUser, ChangePassword
from ..models.db_models import DBUser

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/create")
async def create_user(
    user: CreateUser,
    password: str,
    session: Annotated[AsyncSession, Depends(models.get_session)],
) -> User:
    result = await session.exec(select(DBUser).where(DBUser.username == user.username))
    data = result.one_or_none()
    if data:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This username is exists.",
        )

    data = user.dict()
    db_user = DBUser(**data)
    db_user.hashed_password = security.get_password_hash(password)

    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)

    return db_user


@router.get("/me", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(security.get_current_active_user)],
):
    return current_user


@router.put("/{user_id}/change_password")
async def change_password(
    user_id: int,
    password_update: ChangePassword,
    current_user: Annotated[User, Depends(security.get_current_active_user)],
    session: Annotated[AsyncSession, Depends(models.get_session)],
) -> dict():  # type: ignore
    user = await session.get(DBUser, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if not security.verify_password(
        password_update.current_password, user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Password is incorrect",
        )

    user.hashed_password = security.get_password_hash(password_update.new_password)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return {"message": "Password changed successfully"}


@router.put("/{user_id}/update")
async def update_user(
    request: Request,
    user_id: int,
    user_update: UpdateUser,
    current_user: Annotated[User, Depends(security.get_current_active_user)],
    session: Annotated[AsyncSession, Depends(models.get_session)],
) -> User:

    db_user = await session.get(DBUser, user_id)

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if db_user.username != current_user.username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to update this user",
        )

    db_user.sqlmodel_update(user_update)
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)

    return db_user
