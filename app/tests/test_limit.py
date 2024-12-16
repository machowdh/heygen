from fastapi.testclient import TestClient
from sqlmodel import Session
from app.models import Video
from datetime import datetime, timezone


def test_rate_limit_on_status(client: TestClient, session: Session, headers: dict):
    """
    Test hitting the rate limit on the /translate/status/{id} endpoint, using fastapi-limiter
    """
    video = Video(
        video_url="https://example.com/video.mp4",
        status="pending",
        start_time=datetime.now(timezone.utc),
        delay=10,
    )

    session.add(video)
    session.commit()

    for i in range(11):
        response = client.get(f"/translate/status/{video.id}", headers=headers)
        if i < 10:
            assert response.status_code == 200
        else:
            assert response.status_code == 429
            assert response.json()["detail"] == "Too Many Requests"
