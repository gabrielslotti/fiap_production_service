from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB
from app.database import Base


class Order(Base):
    __tablename__ = 'order'

    id: Mapped[Integer] = mapped_column(type_=Integer, primary_key=True)
    external_id: Mapped[String(120)] = mapped_column(type_=String(120))
    status: Mapped[String(60)] = mapped_column(type_=String(60))
    items: Mapped[JSONB] = mapped_column(type_=JSONB, nullable=False)
