from typing import Optional
from pydantic import BaseModel

class Shop(BaseModel):
    shop_id: str
    username: str
    password: str
    balance: float
    billing_type: str = "prepaid"  # Default to prepaid billing type
    commission_rate: Optional[float] = 0.1