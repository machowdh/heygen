from dotenv import load_dotenv
import uuid
import httpx
import os

from exceptions.PendingStatusException import PendingStatusException
from exceptions.RateLimitExceededException import RateLimitExceededException
from client.utils.retry import custom_retry_with_exponential_backoff


class VideoTranslator:
    def __init__(self, server_url: str):
        load_dotenv()
        self.api_key = os.getenv("API_KEY")
        self.server_url = server_url
        self.requested_videos = {}

    @custom_retry_with_exponential_backoff(
        initial_delay=0.1,
        exponential_base=2.0,
        jitter=True,
        max_retries=45,
        max_delay=60.0,
        errors=(
            RateLimitExceededException,
            PendingStatusException,
            httpx.HTTPStatusError,
        ),
    )
    async def get_video_status(self, video_id: uuid.UUID) -> str:
        """
        Makes an HTTP GET request to retrieve the video status.
        Raises exceptions based on the response.
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.server_url}/translate/status/{video_id}",
                headers={"X-Api-Key": self.api_key},
            )
            try:
                response.raise_for_status()
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code == 429:
                    rate_limit_reset = int(exc.response.headers.get("retry-after", 1))
                    print(f"Rate limit reset: {rate_limit_reset}")
                    raise RateLimitExceededException(rate_limit_reset) from exc
                else:
                    raise

            result = response.json()
            video_status = result.get("status")

            if video_status == "pending":
                raise PendingStatusException("Video translation is still pending.")

            return video_status

    async def translate_video(self, url: str) -> uuid.UUID:
        """
        Initiates the video translation by making an HTTP POST request.
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.server_url}/translate/",
                    json={"video_url": url},
                    headers={"X-Api-Key": self.api_key},
                )
                response.raise_for_status()
            except httpx.HTTPStatusError:
                raise

            result = response.json()
            video_id = uuid.UUID(result["id"])
            self.requested_videos[url] = video_id
            return video_id
