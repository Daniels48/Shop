from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Index, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.BaseModel import Base
# from app.db.models.model_sale_item import SaleItem
# from app.db.models.model_inventory_change import InventoryChange


class Sale(Base):
    __tablename__ = "sales"

    id: Mapped[int] = mapped_column(primary_key=True)

    sale_date: Mapped[datetime] = mapped_column(DateTime(timezone=True),nullable=False)

    total_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2),nullable=False)

    payment_method: Mapped[str] = mapped_column(String(50),nullable=False)

    cash_combine: Mapped[Decimal | None] = mapped_column(Numeric(10, 2),nullable=True)

    card_combine: Mapped[Decimal | None] = mapped_column(Numeric(10, 2),nullable=True)

    items: Mapped[list["SaleItem"]] = relationship(back_populates="sale",passive_deletes=True)

    inventory_changes: Mapped[list["InventoryChange"]] = relationship(back_populates="sale",passive_deletes=True)



    __table_args__ = (
        Index("ix_sales_sale_date", "sale_date"),
        Index("ix_sales_payment_method", "payment_method"),
    )

    def __repr__(self) -> str:
        return (
            f"Sale(id={self.id}, "
            f"sale_date={self.sale_date}, "
            f"total_amount={self.total_amount}, "
            f"payment_method={self.payment_method!r})"
        )