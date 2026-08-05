from sqlalchemy.orm import Session
from typing import Optional, List
from ..models.store import Inventory, CoinTransaction, HintTransaction

class StoreRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_inventory_item(self, user_id: int, item_type: str) -> Optional[Inventory]:
        return self.db.query(Inventory).filter(
            Inventory.user_id == user_id,
            Inventory.item_type == item_type
        ).first()

    def get_all_inventory(self, user_id: int) -> List[Inventory]:
        return self.db.query(Inventory).filter(Inventory.user_id == user_id).all()

    def update_inventory_quantity(self, user_id: int, item_type: str, delta: int) -> Inventory:
        item = self.get_inventory_item(user_id, item_type)
        if not item:
            item = Inventory(user_id=user_id, item_type=item_type, quantity=0)
            self.db.add(item)
        item.quantity = max(0, item.quantity + delta)
        self.db.commit()
        self.db.refresh(item)
        return item

    def record_coin_transaction(self, user_id: int, amount: int, source: str, balance_after: int) -> CoinTransaction:
        tx = CoinTransaction(user_id=user_id, amount=amount, source=source, balance_after=balance_after)
        self.db.add(tx)
        self.db.commit()
        self.db.refresh(tx)
        return tx

    def get_coin_transactions(self, user_id: int, limit: int = 50) -> List[CoinTransaction]:
        return self.db.query(CoinTransaction).filter(CoinTransaction.user_id == user_id).order_by(CoinTransaction.id.desc()).limit(limit).all()

    def record_hint_transaction(self, user_id: int, level_num: int, cost: int = 50) -> HintTransaction:
        tx = HintTransaction(user_id=user_id, level_num=level_num, cost=cost)
        self.db.add(tx)
        self.db.commit()
        self.db.refresh(tx)
        return tx
