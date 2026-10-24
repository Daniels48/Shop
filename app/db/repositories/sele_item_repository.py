from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.model_sale_item import SaleItem


class SaleItemRepository:
    def __init__(self, session: Session):
        self.session = session

    def add(self,sale_id: int,product_id: int,quantity,item_price):
        item = SaleItem(
            sale_id=sale_id,
            product_id=product_id,
            quantity=quantity,
            item_price=item_price,
        )

        self.session.add(item)
        self.session.flush()

        return item

    def get_by_sale_id(self, sale_id: int):
        statement = select(SaleItem).where(
            SaleItem.sale_id == sale_id
        )
        return list(self.session.scalars(statement).all())