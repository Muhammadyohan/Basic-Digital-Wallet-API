import datetime
from datetime import timedelta

from typing import Annotated

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession


from .. import security
from .. import config
from .. import models
from ..models.user import Token
from ..models.db_models import DBUser


router = APIRouter(prefix="/token", tags=["autthentication"])


@router.post("")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[AsyncSession, Depends(models.get_session)],
) -> Token:
    settings = config.get_settings()

    result = await session.exec(
        select(DBUser).where(DBUser.username == form_data.username)
    )

    db_user = result.one_or_none()

    if db_user is None:
        raise HTTPException(status_code=404, detail="Incorrect username")

    db_user = db_user.dict()
    user = security.authenticate_user(db_user, form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user.last_login_date = datetime.datetime.now()
    db_user = await session.get(DBUser, user.id)
    db_user.sqlmodel_update(user)
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    refresh_token = security.create_refresh_token(
        data={"sub": user.username},
        expires_delta=access_token_expires,
    )

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        scope="",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        expires_at=datetime.datetime.now() + access_token_expires,
        issued_at=user.last_login_date,
        user_id=user.id,
    )
