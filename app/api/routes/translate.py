import uuid
import random

from fastapi import APIRouter, HTTPException, Depends, Response
from fastapi_limiter.depends import RateLimiter

from app.models import Video, VideoResponse, VideoRequest
from app.db import SessionDep
from app.auth import CurrentUserDep

from datetime import datetime, timezone


router = APIRouter(prefix="/translate")


@router.post("/", response_model=VideoResponse)
def translate_video(
    video_request: VideoRequest, session: SessionDep, user: CurrentUserDep
):
    """
    Translate requested video at the requested video URL.
    """
    delay = random.randint(10, 60)
    video = Video(
        video_url=str(video_request.video_url),
        status="pending",
        start_time=datetime.now(timezone.utc),
        delay=delay,
    )
    session.add(video)
    session.commit()
    session.refresh(video)
    return video


@router.get(
    "/status/{id}",
    response_model=VideoResponse,
    dependencies=[Depends(RateLimiter(times=10, seconds=30))],
)
def get_translation_status(
    id: uuid.UUID, session: SessionDep, user: CurrentUserDep, response: Response
):
    """
    Get the translation status of the video with the given ID.
    """
    video = session.get(Video, id)
    if not video:
        raise HTTPException(status_code=404, detail="error")

    randomized_delay = random.randint(10, 60)
    if video.status == "completed":
        return video

    if randomized_delay >= video.delay and video.status == "pending":
        video.status = "completed"
        session.add(video)
        session.commit()
    return video
