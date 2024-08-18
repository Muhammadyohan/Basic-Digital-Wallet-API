from typing import Annotated

from jwt.exceptions import InvalidTokenError

from fastapi import Depends, APIRouter, HTTPException, status


from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from .. import security

from .. import models
from ..models.user import User, CreateUser, UpdateUser
from ..models.db_models import DBUser

router = APIRouter(prefix="/users", tags=["users"])


@router.post("")
async def create_user(
    user: CreateUser,
    password: str,
    session: Annotated[AsyncSession, Depends(models.get_session)],
):
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


@router.get("/me/items")
async def read_own_items(
    current_user: Annotated[User, Depends(security.get_current_active_user)],
):
    return [{"item_id": "Foo", "owner": current_user.username}]
