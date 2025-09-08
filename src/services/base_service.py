import shutil
import uuid

from fastapi import UploadFile, HTTPException, File
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pathlib import Path
from pydantic.networks import EmailStr

from core.config import settings

conf = ConnectionConfig(
    MAIL_USERNAME = settings.EMAIL_USER,
    MAIL_PASSWORD = settings.EMAIL_PASSWORD,
    MAIL_FROM = settings.EMAIL_USER,
    MAIL_PORT = settings.EMAIL_PORT,
    MAIL_SERVER = settings.EMAIL_HOST,
    MAIL_STARTTLS = settings.EMAIL_USE_TLS,
    MAIL_SSL_TLS = settings.EMAIL_USE_SSL,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True
)


class BaseService:

    @staticmethod
    async def upload_image(file: UploadFile, image_path: str):
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Only image files allowed")

        media_dir: Path = settings.media_path / image_path
        media_dir.mkdir(parents=True, exist_ok=True)

        filename = f"{uuid.uuid4().hex}_{file.filename}"
        file_path = media_dir / filename

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return {"image_path": f"/media/{image_path}/{filename}"}

    @staticmethod
    async def send_message_to_email(emails_to: list, message: str) -> bool:
        recipients = [str(e) for e in emails_to]
        send_message = MessageSchema(
            subject="Test",
            recipients=recipients,
            body=message,
            subtype=MessageType.html
        )
        try:
            fm = FastMail(conf)
            await fm.send_message(send_message)
            return True
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Email send failed: {e}")
