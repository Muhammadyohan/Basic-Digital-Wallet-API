from pydantic import BaseModel, ConfigDict


class BaseWallet(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    balance: float = 0.0


class CreateWallet(BaseWallet):
    pass


class UpdateWallet(BaseWallet):
    pass

class Wallet(BaseWallet):
    id: int
