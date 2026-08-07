from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from ...db.session import get_db
from ...models.user import User, UserProgressSummary
from ...models.store import Inventory, EquippedItems, CoinTransaction
from ...api.v1.auth import require_current_user

router = APIRouter()

SHOP_ITEMS = [
    # Themes
    {"id": "theme_neon", "category": "themes", "name": "Default Neon", "description": "Sleek glowing cyan & dark slate default theme", "price": 0, "icon": "🎨", "type": "theme"},
    {"id": "theme_cyberpunk", "category": "themes", "name": "Cyberpunk Purple", "description": "Futuristic magenta & neon violet grid aesthetic", "price": 500, "icon": "👾", "type": "theme"},
    {"id": "theme_emerald", "category": "themes", "name": "Forest Emerald", "description": "Relaxing deep forest green & mint glow", "price": 750, "icon": "🌲", "type": "theme"},
    {"id": "theme_sunset", "category": "themes", "name": "Sunset Glow", "description": "Vibrant warm amber & crimson twilight design", "price": 1000, "icon": "🌅", "type": "theme"},

    # Arrow Skins
    {"id": "skin_classic", "category": "arrow_skins", "name": "Classic Arrow", "description": "Clean minimal arrow heads", "price": 0, "icon": "🎯", "type": "skin"},
    {"id": "skin_golden", "category": "arrow_skins", "name": "Golden Arrow", "description": "Shining 24k gold arrow vectors", "price": 400, "icon": "🌟", "type": "skin"},
    {"id": "skin_plasma", "category": "arrow_skins", "name": "Plasma Beam", "description": "Electric energy beam arrow heads", "price": 800, "icon": "⚡", "type": "skin"},
    {"id": "skin_wooden", "category": "arrow_skins", "name": "Wooden Craft", "description": "Rustic carved oak arrows", "price": 300, "icon": "🪵", "type": "skin"},

    # Board Themes
    {"id": "board_slate", "category": "board_themes", "name": "Dark Slate Grid", "description": "Classic dark tile background", "price": 0, "icon": "🧱", "type": "board"},
    {"id": "board_glass", "category": "board_themes", "name": "Glassmorphism", "description": "Frosted glass floating tiles", "price": 600, "icon": "🧊", "type": "board"},
    {"id": "board_hexagon", "category": "board_themes", "name": "Hexagon Matrix", "description": "Sci-fi hexagonal lattice background", "price": 900, "icon": "🔷", "type": "board"},

    # Boosters
    {"id": "hints_5", "category": "boosters", "name": "5x Hints Pack", "description": "Instantly adds 5 AI level solution hints", "price": 200, "icon": "💡", "type": "booster", "reward_type": "hints", "amount": 5},
    {"id": "undos_10", "category": "boosters", "name": "10x Undo Pack", "description": "Instantly adds 10 move undos", "price": 150, "icon": "↺", "type": "booster", "reward_type": "undos", "amount": 10},
    {"id": "hearts_3", "category": "boosters", "name": "Heart Refill (+3)", "description": "Refills 3 extra lives for retries", "price": 100, "icon": "❤️", "type": "booster", "reward_type": "hearts", "amount": 3},

    # Coin Packs
    {"id": "coins_500", "category": "coin_packs", "name": "Coin Sack (+500)", "description": "Free welcome daily coin pack", "price": 0, "icon": "💰", "type": "coins", "amount": 500},
    {"id": "coins_2000", "category": "coin_packs", "name": "Coin Vault (+2000)", "description": "Exchange 15 stars for 2000 coins", "price": 0, "icon": "💎", "type": "coins", "amount": 2000, "star_cost": 15}
]

class PurchaseRequest(BaseModel):
    item_id: str

class EquipRequest(BaseModel):
    item_id: str
    item_type: str # 'theme', 'skin', 'board'

def get_equipped_record(user_id: int, db: Session) -> EquippedItems:
    eq = db.query(EquippedItems).filter(EquippedItems.user_id == user_id).first()
    if not eq:
        eq = EquippedItems(user_id=user_id, equipped_theme="theme_neon", equipped_skin="skin_classic", equipped_board="board_slate")
        db.add(eq)
        db.commit()
        db.refresh(eq)
    return eq

@router.get('/items', response_model=Dict[str, Any])
def get_shop_items(user: User = Depends(require_current_user), db: Session = Depends(get_db)):
    summary = db.query(UserProgressSummary).filter(UserProgressSummary.user_id == user.id).first()
    inv_records = db.query(Inventory).filter(Inventory.user_id == user.id).all()
    owned_ids = set(inv.item_type for inv in inv_records)
    
    # Default free items are owned automatically
    owned_ids.update(["theme_neon", "skin_classic", "board_slate"])

    eq = get_equipped_record(user.id, db)

    return {
        "coins": summary.total_coins if summary else 0,
        "stars": summary.total_stars if summary else 0,
        "equipped": {
            "theme": eq.equipped_theme,
            "skin": eq.equipped_skin,
            "board": eq.equipped_board
        },
        "owned": list(owned_ids),
        "items": SHOP_ITEMS
    }

@router.post('/purchase')
def purchase_item(req: PurchaseRequest, user: User = Depends(require_current_user), db: Session = Depends(get_db)):
    item = next((i for i in SHOP_ITEMS if i["id"] == req.item_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Shop item not found.")

    summary = db.query(UserProgressSummary).filter(UserProgressSummary.user_id == user.id).first()
    if not summary:
        summary = UserProgressSummary(user_id=user.id, total_coins=0, total_stars=0)
        db.add(summary)

    # Check star cost if coin pack
    star_cost = item.get("star_cost", 0)
    if star_cost > 0 and (summary.total_stars or 0) < star_cost:
        raise HTTPException(status_code=400, detail=f"Insufficient stars. Requires {star_cost} stars.")

    # Check coin cost
    if item["price"] > 0 and (summary.total_coins or 0) < item["price"]:
        raise HTTPException(status_code=400, detail="Insufficient coins to purchase item.")

    inv = db.query(Inventory).filter(Inventory.user_id == user.id, Inventory.item_type == req.item_id).first()

    # Cosmetic items are one-time purchase
    if item["type"] in ["theme", "skin", "board"] and inv:
        raise HTTPException(status_code=400, detail="Item already owned.")

    # Deduct price / stars
    if item["price"] > 0:
        summary.total_coins -= item["price"]
        db.add(CoinTransaction(user_id=user.id, amount=-item["price"], source=f"shop_purchase_{req.item_id}", balance_after=summary.total_coins))

    if star_cost > 0:
        summary.total_stars -= star_cost

    # Add item or grant coins/boosters
    if item["type"] in ["theme", "skin", "board"]:
        if not inv:
            db.add(Inventory(user_id=user.id, item_type=req.item_id, quantity=1))
    elif item["type"] == "coins":
        summary.total_coins += item["amount"]
    elif item["type"] == "booster":
        if not inv:
            inv = Inventory(user_id=user.id, item_type=item["reward_type"], quantity=0)
            db.add(inv)
        inv.quantity += item["amount"]

    db.commit()

    return {
        "success": True,
        "item_id": req.item_id,
        "total_coins": summary.total_coins,
        "total_stars": summary.total_stars
    }

@router.post('/equip')
def equip_item(req: EquipRequest, user: User = Depends(require_current_user), db: Session = Depends(get_db)):
    eq = get_equipped_record(user.id, db)
    
    # Check ownership
    inv = db.query(Inventory).filter(Inventory.user_id == user.id, Inventory.item_type == req.item_id).first()
    free_items = ["theme_neon", "skin_classic", "board_slate"]

    if req.item_id not in free_items and not inv:
        raise HTTPException(status_code=400, detail="You do not own this item.")

    if req.item_type == "theme":
        eq.equipped_theme = req.item_id
    elif req.item_type == "skin":
        eq.equipped_skin = req.item_id
    elif req.item_type == "board":
        eq.equipped_board = req.item_id

    db.commit()

    return {
        "success": True,
        "equipped": {
            "theme": eq.equipped_theme,
            "skin": eq.equipped_skin,
            "board": eq.equipped_board
        }
    }
