from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import Integer, String

from .base_models import BaseModel


class OTP(BaseModel):
    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False)
    code: Mapped[int] = mapped_column(Integer, nullable=False)

    def __repr__(self):
        return f"<OTP(id={self.id}, email={self.email}, code={self.code})>"
