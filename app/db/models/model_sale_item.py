from decimal import Decimal

from sqlalchemy import ForeignKey, Index, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.BaseModel import Base
# from app.db.models.model_product import Product
# from app.db.models.model_sale import Sale


class SaleItem(Base):
    __tablename__ = "sale_items"

    id: Mapped[int] = mapped_column(primary_key=True)

    sale_id: Mapped[int] = mapped_column(ForeignKey("sales.id", ondelete="CASCADE"),nullable=False)

    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"),nullable=False)

    quantity: Mapped[Decimal] = mapped_column(Numeric(10, 3),nullable=False)

    item_price: Mapped[Decimal] = mapped_column(Numeric(10, 2),nullable=False)

    sale: Mapped["Sale"] = relationship(back_populates="items",)

    product: Mapped["Product"] = relationship(back_populates="sale_items")




    __table_args__ = (
        Index("ix_sale_items_sale_id", "sale_id"),
        Index("ix_sale_items_product_id", "product_id"),
        Index(
            "ix_sale_items_sale_id_product_id",
            "sale_id",
            "product_id",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"SaleItem(id={self.id}, "
            f"sale_id={self.sale_id}, "
            f"product_id={self.product_id}, "
            f"quantity={self.quantity}, "
            f"item_price={self.item_price})"
        )