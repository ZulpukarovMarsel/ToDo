
from passlib.context import CryptContext

from services.base_service import BaseService

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


class UserService(BaseService):
    def __init__(self, user_repository):
        self.user_repository = user_repository

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Хеширует пароль пользователя
        """
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """Проверяем пароль пользователя"""
        return pwd_context.verify(password, hashed_password)

    async def create_user(self, user_data):
        """
        Создает нового пользователя в базе данных и хэшируем его пароль
        """
        user_data = user_data.copy()
        user_data['password'] = self.hash_password(user_data['password'])
        return await self.user_repository.create_data(user_data)
