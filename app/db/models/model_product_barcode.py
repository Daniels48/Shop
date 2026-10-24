from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.BaseModel import Base
# from app.db.models.model_product import Product


class ProductBarcode(Base):
    __tablename__ = "product_barcodes"

    id: Mapped[int] = mapped_column(primary_key=True)

    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"),nullable=False)

    barcode: Mapped[str] = mapped_column(String(255),nullable=False, unique=True)

    product: Mapped["Product"] = relationship(back_populates="barcodes")



    __table_args__ = (
        Index("ix_product_barcodes_product_id", "product_id"),
    )

    def __repr__(self) -> str:
        return (
            f"ProductBarcode(id={self.id}, "
            f"product_id={self.product_id}, "
            f"barcode={self.barcode!r})"
        )