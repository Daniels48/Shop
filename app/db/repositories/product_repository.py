from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.db.models.model_product import Product
from app.db.models.model_product_barcode import ProductBarcode


class ProductRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, product_id: int):
        return self.session.get(Product, product_id)

    def get_by_barcode(self, barcode: str):
        statement = (
            select(Product)
            .join(ProductBarcode, ProductBarcode.product_id == Product.id)
            .where(ProductBarcode.barcode == barcode)
        )
        return self.session.scalar(statement)

    def get_all(self, sort_by: str = "id", ascending: bool = True):
        allowed_sort_fields = {
            "id": Product.id,
            "name": Product.name,
            "price_sale": Product.price_sale,
            "quantity": Product.quantity,
        }

        column = allowed_sort_fields.get(sort_by, Product.id)
        column = column.asc() if ascending else column.desc()

        statement = select(Product).order_by(column)
        return list(self.session.scalars(statement).all())

    def search(self, search_text: str, limit: int = 8):
        statement = (
            select(Product)
            .where(func.lower(Product.name).contains(search_text.lower()))
            .limit(limit)
        )
        return list(self.session.scalars(statement).all())

    def add(self, product: Product):
        self.session.add(product)
        self.session.flush()
        return product

    def delete(self, product: Product):
        self.session.delete(product)

    def get_inventory_summary(self):
        statement = select(
            func.count(Product.id),
            func.coalesce(func.sum(Product.quantity), 0),
            func.coalesce(
                func.sum(Product.quantity * Product.price_sale),
                0,
            ),
        )

        return self.session.execute(statement).one()