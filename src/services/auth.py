import datetime
import random
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from repositories.users import UserRepository, BaseRepository


class AuthService(BaseRepository):
    def __init__(self):
        self.secret_key = settings.JWT_SECRET_KEY
        self.algorithm = settings.JWT_ALGORITHM

    def create_token(self, data: dict, expires_delta: int = None, type: str = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.datetime.utcnow() + datetime.timedelta(seconds=expires_delta)
            to_encode.update({"exp": int(expire.timestamp())})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def verify_token(self, token: str) -> dict:
        try:
            return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        except JWTError as e:
            return {'error': e}

    @classmethod
    async def get_user_from_token(cls, token: str, db: AsyncSession) -> dict:
        payload = cls().verify_token(token)
        if payload:
            user_id = payload.get("user_id")
            if user_id:
                user_repo = UserRepository(db)
                user = await user_repo.get_data_by_id(user_id)
                return user
        return None


class OTPService:

    @staticmethod
    async def generatore_code() -> int:
        code = random.randint(1000, 9999)
        return code

    def send_otp(self, email_to, code) -> bool:
        return True
