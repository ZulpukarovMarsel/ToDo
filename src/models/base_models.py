import datetime
from sqlalchemy import text
from sqlalchemy.orm import DeclarativeBase, declared_attr, Mapped, mapped_column


class BaseModel(DeclarativeBase):
    __abstract__ = True

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower() + "s"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        server_default=text("TIMEZONE('Asia/Bishkek', now())")
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        server_default=text("TIMEZONE('Asia/Bishkek', now())"),
        onupdate=text("TIMEZONE('Asia/Bishkek', now())")
    )
