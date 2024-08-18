from pydantic import BaseModel, ConfigDict


class BaseMerchant(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    description: str | None = None
    telephone: str | None = None
    email: str | None = None
    age: int | None = None


class CreateMerchant(BaseMerchant):
    pass


class UpdateMerchant(BaseMerchant):
    pass


class Merchant(BaseMerchant):
    id: int


class MerchantList(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    merchants: list[Merchant]
    page: int
    page_count: int
    size_per_page: int
