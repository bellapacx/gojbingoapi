from http.client import HTTPException
from typing import List, Optional
from fastapi import APIRouter, Header
from firebase_client import db
from utils.token import verify_token
from models.game import StartGameRequest
from uuid import uuid4
from firebase_admin import firestore  # ✅ Add this import
from models.winings import WiningEntry
from datetime import datetime
from isoweek import Week  # pip install isoweek

router = APIRouter()

@router.get("/games")
def get_games(authorization: str = Header(...)):
    verify_token(authorization.split(" ")[-1])
    return [doc.to_dict() for doc in db.collection("games").stream()]

@router.post("/games")
def create_game(data: dict, authorization: str = Header(...)):
    verify_token(authorization.split(" ")[-1])
    db.collection("games").add(data)
    return {"status": "game recorded"}



from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from uuid import uuid4
from datetime import datetime
from firebase_admin import firestore

db = firestore.client()
router = APIRouter()

class StartGameRequest(BaseModel):
    shop_id: str
    bet_per_card: float
    prize: float
    total_cards: int
    selected_cards: list
    winning_pattern: str = None  # optional

@router.post("/startgame")
async def start_game(data: StartGameRequest):
    round_id = str(uuid4())
    now = datetime.utcnow()
    today_str = now.strftime("%Y-%m-%d")

    # Fetch shop document
    shop_query = db.collection("shops").where("shop_id", "==", data.shop_id).limit(1).get()
    if not shop_query:
        raise HTTPException(status_code=404, detail="Shop not found")
    
    shop_doc = shop_query[0]
    shop_data = shop_doc.to_dict()

    # Use shop commission_rate or default 10%
    commission_rate = shop_data.get("commission_rate", 0.2)

    # Calculate commission
    total_bet = data.total_cards * data.bet_per_card
    commission_amount = total_bet * commission_rate

    # Check shop balance for prepaid/postpaid
    billing_type = shop_data.get("billing_type", "prepaid")
    current_balance = shop_data.get("balance", 0.0)

    if billing_type == "postpaid" and current_balance == 0.0:
        raise HTTPException(status_code=400, detail="Insufficient balance for postpaid shop")
    if billing_type == "prepaid" and current_balance < commission_amount:
        raise HTTPException(status_code=400, detail="Insufficient balance for prepaid shop")

    # Deduct commission for prepaid shops
    if billing_type == "prepaid":
        new_balance = current_balance - commission_amount
        db.collection("shops").document(shop_doc.id).update({"balance": new_balance})

    # Save game round
    db.collection("game_rounds").document(round_id).set({
        "round_id": round_id,
        "shop_id": data.shop_id,
        "date": today_str,
        "bet_per_card": data.bet_per_card,
        "total_cards": data.total_cards,
        "prize": data.prize,
        "commission_rate": commission_rate,
        "commission_amount": commission_amount,
        "winning_pattern": data.winning_pattern,
        "status": "ongoing",
        "started_at": firestore.SERVER_TIMESTAMP
    })

    # === Update or create daily report document ===
    report_ref = db.collection("shop_reports").document(data.shop_id).collection("daily_reports").document(today_str)
    report_doc = report_ref.get()

    if report_doc.exists:
        report_data = report_doc.to_dict()
        report_data["play_count"] += 1
        report_data["placed_bets"] += total_bet
        report_data["awarded"] += data.prize
        report_data["net_cash"] += total_bet - data.prize
        report_data["company_commission"] += (total_bet - data.prize) * 0.2
    else:
        report_data = {
            "date": today_str,
            "play_count": 1,
            "placed_bets": total_bet,
            "awarded": data.prize,
            "net_cash": total_bet - data.prize,
            "company_commission": (total_bet - data.prize) * 0.2
        }

    report_ref.set(report_data)

    return {
        "status": "success",
        "message": "Game started",
        "round_id": round_id,
        "commission_rate": commission_rate,
        "commission_amount": commission_amount
    }


@router.post("/winings")
async def record_wining(entry: WiningEntry):
    wining_id = str(uuid4())  # Unique ID for the document

    wining_data = {
        "card_id": entry.card_id,
        "round_id": entry.round_id,
        "shop_id": entry.shop_id,
        "prize": entry.prize,
        "timestamp": firestore.SERVER_TIMESTAMP,  # Requires import from google.cloud.firestore
    }

    db.collection("winings").document(wining_id).set(wining_data)

    return {"status": "success", "message": "Wining recorded", "id": wining_id}


class SaveGameRequest(BaseModel):
    shop_id: str
    bet_per_card: float
    prize: float
    total_cards: int
    selected_cards: List[int]
    interval: int
    language: str
    commission_rate: float
    winning_pattern: Optional[str] = None
    
@router.post("/savegame")
async def save_game(req: SaveGameRequest):
    try:
        round_id = str(uuid4())
        now = datetime.utcnow().isoformat()
        today_str = datetime.utcnow().strftime("%Y-%m-%d")

        # Fetch shop document
        shop_query = db.collection("shops").where("shop_id", "==", req.shop_id).limit(1).get()
        if not shop_query:
           raise HTTPException(status_code=404, detail="Shop not found")
    
        shop_doc = shop_query[0]
        shop_data = shop_doc.to_dict()

    # Use shop commission_rate or default 10%
        commission_rate = shop_data.get("commission_rate", 0.2)

    # Calculate commission
        total_bet = req.total_cards * req.bet_per_card
        commission_amount = total_bet * commission_rate

        # Round data
        round_data = {
            "shopId": req.shop_id,
            "roundId": round_id,
            "betPerCard": req.bet_per_card,
            "prize": req.prize,
            "totalCards": req.total_cards,
            "selectedCards": req.selected_cards,
            "interval": req.interval,
            "language": req.language,
            "commissionRate": req.commission_rate,
            "winningPattern": req.winning_pattern,
            "started_at": now,
            "status": "ongoing",
        }

        # Save round to Firestore (collection: roundsPerShop, doc: shop_id)
        # Check if document exists for this shop ID in roundsPerShop
        round_doc_ref = db.collection("roundsPerShop").document(req.shop_id)
        round_doc = round_doc_ref.get()
        
        if round_doc.exists:
            # Document exists, update it
            round_doc_ref.update(round_data)
        else:
            # Document doesn't exist, create it
            round_doc_ref.set(round_data)

        # === Update or create daily report document ===
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
