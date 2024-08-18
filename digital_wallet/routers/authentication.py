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

from datetime import timedelta

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
    db_user = result.all()
    db_user = db_user[0]
    db_user = db_user.dict()
    if db_user is None:
        raise HTTPException(status_code=404, detail="Incorrect username")

    user = security.authenticate_user(db_user, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return Token(access_token=access_token, token_type="bearer")
