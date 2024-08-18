from pydantic import BaseModel, ConfigDict


class BaseWallet(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    describe: str | None = None
    owner_first_name: str | None = None
    owner_last_name: str | None = None
    balance: float = 0.0
    merchant_id: int | None = 0
    user_id: int | None = 0


class CreateWallet(BaseWallet):
    pass


class UpdateWallet(BaseWallet):
    pass


class Wallet(BaseWallet):
    id: int


class WalletList(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    items: list[Wallet]
    page: int
    page_count: int
    size_per_page: int
