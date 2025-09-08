from sqlalchemy import select

from .base_repository import BaseRepository
from models.otp import OTP


class OTPRepository(BaseRepository):
    model = OTP

    async def get_otp_by_email_code(self, email: str, code: int):
        result = await self.db.execute(
            select(self.model).where(self.model.email == email, self.model.code == code)
        )
        return result.scalar_one_or_none()

    async def get_otp_by_email(self, email: str):
        result = await self.db.execute(
            select(self.model).where(self.model.email == email)
        )
        return result.scalar_one_or_none()
