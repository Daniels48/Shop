from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.model_product_barcode import ProductBarcode


class BarcodeRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_barcode(self, barcode: str):
        statement = select(ProductBarcode).where(
            ProductBarcode.barcode == barcode
        )
        return self.session.scalar(statement)

    def exists(self, barcode: str) -> bool:
        statement = select(ProductBarcode.id).where(
            ProductBarcode.barcode == barcode
        )
        return self.session.scalar(statement) is not None

    def get_all(self) -> list[str]:
        statement = select(ProductBarcode.barcode)
        return list(self.session.scalars(statement).all())

    def add(self, product_id: int, barcode: str):
        barcode_record = ProductBarcode(
            product_id=product_id,
            barcode=barcode,
        )
        self.session.add(barcode_record)
        self.session.flush()
        return barcode_record

    def get_by_product_id(self, product_id: int):
        statement = select(ProductBarcode).where(
            ProductBarcode.product_id == product_id
        )
        return list(self.session.scalars(statement).all())

    def move_to_product(
        self,
        source_product_id: int,
        target_product_id: int,
    ):
        statement = select(ProductBarcode).where(
            ProductBarcode.product_id == source_product_id
        )

        barcodes = self.session.scalars(statement).all()

        for barcode in barcodes:
            barcode.product_id = target_product_id

        self.session.flush()