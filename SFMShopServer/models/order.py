from pydantic import BaseModel


class OrderCreate(BaseModel):
    user_id: int
    items: list[dict]




