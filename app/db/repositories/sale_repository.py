from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.db.models.model_sale import Sale
from app.db.database import SessionLocal
from app.db.models import InventoryChange, Product, SaleItem
from app.utils.times import get_now_dt


class SaleRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, sale_id: int):
        return self.session.get(Sale, sale_id)

    def add(self,total_amount,payment_method: str,cash_combine=None,card_combine=None):
        sale = Sale(
            total_amount=total_amount,
            payment_method=payment_method,
            cash_combine=cash_combine,
            card_combine=card_combine,
            sale_date=get_now_dt()
        )

        self.session.add(sale)
        self.session.flush()

        return sale

    def get_next_sale_number(self) -> int:
        statement = select(func.max(Sale.id))
        max_id = self.session.scalar(statement)

        return (max_id or 0) + 1

    @staticmethod
    def add_sale_with_items(
            total_amount,
            payment_method: str,
            products: list[Product],
            is_barcode: bool=True,
            cash_combine=None,
            card_combine=None,
    ):
        try:
            with SessionLocal() as session:
                sale = Sale(
                    sale_date=get_now_dt(),
                    total_amount=total_amount,
                    payment_method=payment_method,
                    cash_combine=cash_combine,
                    card_combine=card_combine,
                )

                session.add(sale)
                session.flush()  # Получаем sale.id до commit

                for product in products:
                    product_id = product.id
                    quantity = product.current_quantity
                    price = product.price

                    item = SaleItem(
                        sale_id=sale.id,
                        product_id=product_id,
                        quantity=quantity,
                        item_price=price,
                    )

                    session.add(item)

                    if is_barcode:
                        db_product = session.get(Product, product_id)

                        if db_product is None:
                            raise ValueError(f"Товар с ID {product_id} не найден")

                        db_product.quantity -= quantity

                    inventory_change = InventoryChange(
                        product_id=product_id, quantity=quantity, type_action="sale", sale_id=sale.id
                    )

                    session.add(inventory_change)

                session.commit()
                return sale.id

        except Exception:
            raise