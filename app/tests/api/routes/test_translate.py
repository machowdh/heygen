from fastapi.testclient import TestClient
from sqlmodel import Session
from app.models import Video
from datetime import datetime, timezone
import uuid
import time


def test_translate_video(client: TestClient, session: Session, headers: dict):
    """
    Test creating a new video translation request.
    """
    video_url = "https://example.com/video.mp4"
    response = client.post(
        "/translate/", json={"video_url": video_url}, headers=headers
    )

    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["status"] == "pending"
    assert "delay" in data

    video = session.get(Video, uuid.UUID(data["id"]))
    assert video is not None
    assert video.video_url == video_url
    assert video.status == "pending"


def test_get_translation_status(client: TestClient, session: Session, headers: dict):
    """
    Test fetching the translation status of a video.
    """
    video = Video(
        video_url="https://example.com/video.mp4",
        status="pending",
        start_time=datetime.now(timezone.utc),
        delay=1,
    )
    session.add(video)
    session.commit()

    response = client.get(f"/translate/status/{video.id}", headers=headers)
    assert response.status_code == 200
    data = response.json()

    assert data["id"] == str(video.id)
    assert data["status"] in ["pending", "completed"]

    time.sleep(2)
    response = client.get(f"/translate/status/{video.id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    print(response.json())
    assert data["status"] == "completed"
