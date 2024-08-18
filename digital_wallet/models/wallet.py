from pydantic import BaseModel, ConfigDict


class BaseWallet(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    owner_first_name: str | None = None
    owner_last_name: str | None = None
    balance: float = 0.0


class CreateWallet(BaseWallet):
    pass


class UpdateWallet(BaseWallet):
    pass


class Wallet(BaseWallet):
    id: int
