from sqlalchemy.orm import Session
from typing import List, Dict, Any
from ..repositories.store_repo import StoreRepository
from ..repositories.progress_repo import ProgressRepository

class StoreService:
    def __init__(self, db: Session):
        self.db = db
        self.store_repo = StoreRepository(db)
        self.progress_repo = ProgressRepository(db)

    def get_user_inventory(self, user_id: int) -> List[Dict[str, Any]]:
        items = self.store_repo.get_all_inventory(user_id)
        summary = self.progress_repo.get_or_create_summary(user_id)
        
        # Always include coin & hint balances
        inv_map = {item.item_type: item.quantity for item in items}
        inv_map["coins"] = summary.total_coins or 0
        inv_map["hints"] = inv_map.get("hints", 5)
        
        return [{"item_type": k, "quantity": v} for k, v in inv_map.items()]

    def grant_coins(self, user_id: int, amount: int, source: str = "admin_grant") -> int:
        summary = self.progress_repo.get_or_create_summary(user_id)
        summary.total_coins = max(0, (summary.total_coins or 0) + amount)
        self.db.commit()
        
        self.store_repo.record_coin_transaction(user_id, amount, source, summary.total_coins)
        return summary.total_coins

    def use_hint(self, user_id: int, level_num: int, cost: int = 50) -> bool:
        summary = self.progress_repo.get_or_create_summary(user_id)
        if (summary.total_coins or 0) < cost:
            return False
            
        summary.total_coins -= cost
        self.db.commit()
        
        self.store_repo.record_coin_transaction(user_id, -cost, "hint_purchase", summary.total_coins)
        self.store_repo.record_hint_transaction(user_id, level_num, cost)
        return True

    def get_transaction_history(self, user_id: int) -> List[Dict[str, Any]]:
        txs = self.store_repo.get_coin_transactions(user_id)
        return [
            {
                "id": tx.id,
                "amount": tx.amount,
                "source": tx.source,
                "balance_after": tx.balance_after,
                "created_at": tx.created_at.isoformat()
            } for tx in txs
        ]
