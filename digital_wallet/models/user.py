import datetime

import pydantic
from pydantic import BaseModel, ConfigDict


class BaseUser(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    email: str = pydantic.Field(json_schema_extra=dict(example="admin@email.local"))
    username: str = pydantic.Field(json_schema_extra=dict(example="admin"))
    first_name: str = pydantic.Field(json_schema_extra=dict(example="Firstname"))
    last_name: str = pydantic.Field(json_schema_extra=dict(example="Lastname"))
    disabled: bool = False


class CreateUser(BaseUser):
    pass


class UpdateUser(BaseUser):
    pass


class User(BaseUser):
    id: int
    last_login_date: datetime.datetime | None = pydantic.Field(
        json_schema_extra=dict(example="2023-01-01T00:00:00.000000"), default=None
    )


class UserList(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    users: list[User]


class ChangePassword(BaseModel):
    current_password: str
    new_password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
