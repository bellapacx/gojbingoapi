from pydantic import BaseModel
from typing import List

class StartGameRequest(BaseModel):
    shop_id: str
    selected_cards: List[int]
    prize: float
    interval: int
    language: str
    bet_per_card: float
    commission_rate: float
    winning_pattern: str
