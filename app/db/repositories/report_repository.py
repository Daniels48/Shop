from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.db.models.model_product import Product
from app.db.models.model_sale import Sale
from app.db.models.model_sale_item import SaleItem
from app.db.models.model_inventory_change import InventoryChange
from app.db.models.model_product_barcode import ProductBarcode


class ReportRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_inventory_summary(self):
        """Количество товаров, общее количество и стоимость остатков."""
        statement = select(
            func.count(Product.id),
            func.coalesce(func.sum(Product.quantity), 0),
            func.coalesce(
                func.sum(Product.quantity * Product.price_sale), 0,
            ),
        )

        return self.session.execute(statement).one()

    def get_available_months(self, barcode_product: str | None = None):
        """Месяцы, в которых были изменения остатков."""
        statement = (
            select(
                func.to_char(
                    InventoryChange.change_date,
                    "YYYY-MM",
                ).label("month_str")
            )
            .select_from(InventoryChange)
            .join(
                Product,
                InventoryChange.product_id == Product.id,
            )
            .join(
                ProductBarcode,
                ProductBarcode.product_id == Product.id,
            )
            .distinct()
            .order_by("month_str")
        )

        if barcode_product:
            statement = statement.where(
                ProductBarcode.barcode == barcode_product
            )

        statement = statement.order_by(
            func.to_char(InventoryChange.change_date, "YYYY-MM").desc()
        )

        return list(self.session.scalars(statement).all())

    def get_action_details(self, record_id: int, is_sale: bool = True):
        """
        Подробности продажи или изменения остатков.

        Формат результата сохранён похожим на старый Database:
        продажа:
        (sale_id, sale_date, payment_method, product_name, quantity, item_price)

        изменение остатков:
        (change_id, change_date, type_action, product_name, quantity, union_data)
        """
        if is_sale:
            statement = (
                select(
                    Sale.id,
                    Sale.sale_date,
                    Sale.payment_method,
                    Product.name,
                    SaleItem.quantity,
                    SaleItem.item_price,
                )
                .select_from(SaleItem)
                .join(Sale, SaleItem.sale_id == Sale.id)
                .join(Product, SaleItem.product_id == Product.id)
                .where(Sale.id == record_id)
            )
        else:
            statement = (
                select(
                    InventoryChange.id,
                    InventoryChange.change_date,
                    InventoryChange.type_action,
                    Product.name,
                    InventoryChange.quantity,
                    InventoryChange.union_data,
                )
                .select_from(InventoryChange)
                .join(
                    Product,
                    InventoryChange.product_id == Product.id,
                )
                .where(InventoryChange.id == record_id)
            )

        return list(self.session.execute(statement).all())