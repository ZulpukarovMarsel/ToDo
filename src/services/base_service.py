from fastapi import UploadFile, HTTPException, File
from core.config import settings
from pathlib import Path
import shutil
import uuid


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
