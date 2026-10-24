from decimal import Decimal

from sqlalchemy import Index, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.BaseModel import Base
# from app.db.models.model_inventory_change import InventoryChange
# from app.db.models.model_sale_item import SaleItem
# from app.db.models.model_product_barcode import ProductBarcode


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    price_sale: Mapped[Decimal] = mapped_column(Numeric(10, 2),nullable=False)
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(10, 3),nullable=False,default=Decimal("1.000"),server_default="1.000"
    )

    # Штрихкоды товара
    barcodes: Mapped[list["ProductBarcode"]] = relationship(back_populates="product",passive_deletes=True)

    # Позиции продаж с этим товаром
    sale_items: Mapped[list["SaleItem"]] = relationship(back_populates="product",passive_deletes=True)

    # История изменения остатков
    inventory_changes: Mapped[list["InventoryChange"]] = relationship(back_populates="product",passive_deletes=True)

    __table_args__ = (
        Index("ix_products_name", "name"),
    )

    def __repr__(self) -> str:
        return (
            f"Product(id={self.id}, "
            f"name={self.name!r}, "
            f"price_sale={self.price_sale}, "
            f"quantity={self.quantity})"
        )