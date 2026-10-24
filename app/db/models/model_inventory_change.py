from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime,ForeignKey,Index,Numeric,String,Text

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.BaseModel import Base
# from app.db.models.model_product import Product
# from app.db.models.model_sale import Sale


class InventoryChange(Base):
    __tablename__ = "inventory_changes"

    id: Mapped[int] = mapped_column(primary_key=True)

    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"),nullable=False)

    quantity: Mapped[Decimal] = mapped_column(Numeric(10, 3),nullable=False)

    change_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    type_action: Mapped[str] = mapped_column(String(50),nullable=False)

    id_sale: Mapped[int | None] = mapped_column(ForeignKey("sales.id", ondelete="SET NULL"), nullable=True)

    union_data: Mapped[str | None] = mapped_column(Text,nullable=True)

    product: Mapped["Product"] = relationship(back_populates="inventory_changes")

    sale: Mapped["Sale | None"] = relationship(back_populates="inventory_changes")




    __table_args__ = (
        Index("ix_inventory_changes_product_id", "product_id"),
        Index("ix_inventory_changes_change_date", "change_date"),
    )

    def __repr__(self) -> str:
        return (
            f"InventoryChange(id={self.id}, "
            f"product_id={self.product_id}, "
            f"quantity={self.quantity}, "
            f"type_action={self.type_action!r}, "
            f"id_sale={self.id_sale})"
        )