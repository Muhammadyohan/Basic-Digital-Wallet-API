from pydantic import BaseModel, ConfigDict

class BaseUser(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None

class CreateUser(BaseUser):
    pass

class UpdateUser(BaseUser):
    pass

class User(BaseUser):
    id: int