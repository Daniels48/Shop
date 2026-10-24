from sqlalchemy import select, func, literal, case, Numeric
from sqlalchemy.orm import Session, aliased

from app.db.models.model_inventory_change import InventoryChange
from app.db.models.model_product import Product
from app.db.database import SessionLocal
from app.db.models import Sale, ProductBarcode, SaleItem
from app.view.dialog.product_history.tabs.history_tab.calculator.enums import InventoryChangeStatistic


class InventoryRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_product(self, product_id: int):
        return self.session.get(Product, product_id)

    def change_quantity(self,product_id: int,quantity,type_action: str):
        product = self.get_product(product_id)

        if product is None:
            raise ValueError(f"Товар с ID {product_id} не найден")

        if type_action == "add":
            product.quantity += quantity
        elif type_action in {"sale", "clear"}:
            if product.quantity < quantity:
                raise ValueError("Недостаточно товара на складе")
            product.quantity -= quantity
        else:
            raise ValueError(f"Неизвестный тип изменения остатков: {type_action}")

        self.session.flush()
        return product

    def add_change(self,product_id: int,quantity,type_action: str,sale_id=None,union_data=None):
        change = InventoryChange(
            product_id=product_id,
            quantity=quantity,
            type_action=type_action,
            id_sale=sale_id,
            union_data=union_data,
        )

        self.session.add(change)
        self.session.flush()

        return change

    def get_by_product_id(self, product_id: int):
        statement = select(InventoryChange).where(
            InventoryChange.product_id == product_id
        )
        return list(self.session.scalars(statement).all())

    @staticmethod
    def get_inventory_changes(barcode_product: str | None = None,date_range: tuple[str, str] | None = None) \
            -> list[InventoryChangeStatistic]:
        if not date_range:
            raise ValueError("Параметр date_range обязателен")

        start_date, end_date = date_range

        lunch_codes = [
            "2117674458339",
            "2967148931185",
            "2627451727683",
            "5581777172473",
            "3828139792736",
        ]

        # Количество всех товаров в продаже
        quantity_subquery = (
            select(func.coalesce(func.sum(SaleItem.quantity), 0))
            .where(SaleItem.sale_id == Sale.id)
            .correlate(Sale)
            .scalar_subquery()
        )

        # Сумма обедов в продаже
        lunch_item = aliased(SaleItem)
        lunch_product = aliased(Product)
        lunch_barcode = aliased(ProductBarcode)

        lunch_amount_subquery = (
            select(
                func.coalesce(
                    func.sum(lunch_item.quantity * lunch_item.item_price),
                    literal(0, type_=Numeric(12, 2)),
                )
            )
            .select_from(lunch_item)
            .join(lunch_product, lunch_item.product_id == lunch_product.id)
            .where(lunch_item.sale_id == Sale.id)
            .where(
                select(literal(1))
                .select_from(lunch_barcode)
                .where(lunch_barcode.product_id == lunch_product.id)
                .where(lunch_barcode.barcode.in_(lunch_codes))
                .exists()
            )
            .correlate(Sale)
            .scalar_subquery()
        )

        # Сумма изменения
        amount_expression = case(
            (InventoryChange.type_action == "sale", Sale.total_amount),
            (InventoryChange.type_action == "union", 0),
            else_=(
                    InventoryChange.quantity
                    * func.coalesce(Product.price_sale, 0)
            ),
        )

        # Количество изменения
        quantity_expression = case(
            (
                InventoryChange.type_action == "sale",
                quantity_subquery,
            ),
            else_=InventoryChange.quantity,
        )

        statement = (
            select(
                InventoryChange.type_action.label("type_action"),
                Sale.payment_method.label("payment_method"),
                amount_expression.label("amount"),
                quantity_expression.label("quantity"),
                InventoryChange.change_date.label("change_date"),
                InventoryChange.id.label("change_id"),
                Sale.id.label("sale_id"),
                Sale.cash_combine.label("cash_amount_combine"),
                Sale.card_combine.label("card_amount_combine"),
                lunch_amount_subquery.label("lunch_amount"),
            )
            .select_from(InventoryChange)
            .outerjoin(Sale, InventoryChange.id_sale == Sale.id)
            .outerjoin(Product, InventoryChange.product_id == Product.id)
            .where(
                InventoryChange.change_date >= start_date,
                InventoryChange.change_date < end_date,
            )
            .order_by(InventoryChange.change_date.desc())
        )

        # Фильтр по штрихкоду без размножения строк
        if barcode_product:
            statement = statement.where(
                select(literal(1))
                .select_from(ProductBarcode)
                .where(ProductBarcode.product_id == Product.id)
                .where(ProductBarcode.barcode == barcode_product)
                .exists()
            )

        with SessionLocal() as session:
            rows = session.execute(statement).mappings().all()

            return [InventoryChangeStatistic(**row) for row in rows]