from pydantic import BaseModel

class WiningEntry(BaseModel):
    card_id: int
    round_id: str
    shop_id: str
    prize: float