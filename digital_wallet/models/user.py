from pydantic import BaseModel, ConfigDict


class BaseUser(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool = False


class CreateUser(BaseUser):
    pass


class UpdateUser(BaseUser):
    pass


class User(BaseUser):
    id: int


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
