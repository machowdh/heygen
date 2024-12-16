from sqlmodel import SQLModel, Field
from pydantic import BaseModel, HttpUrl
from datetime import datetime, timezone
import uuid


class Video(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    video_url: str
    status: str
    start_time: str = Field(default_factory=lambda: datetime.now(timezone.utc))
    delay: int

    @property
    def start_time_as_datetime(self) -> datetime:
        if isinstance(self.start_time, str):
            return datetime.fromisoformat(self.start_time)
        return self.start_time


class VideoRequest(BaseModel):
    video_url: HttpUrl


class VideoResponse(SQLModel):
    id: uuid.UUID
    status: str
    delay: int
