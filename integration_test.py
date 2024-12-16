import asyncio
import subprocess
import time
from client.video_translator import VideoTranslator, PendingStatusException

SERVER_START_DELAY = 2


async def main():
    # Start the FastAPI server
    server_process = subprocess.Popen(
        [
            "uvicorn",
            "app.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            "8000",
            "--reload",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    try:
        print("Starting FastAPI server...")
        print(f"Waiting for {SERVER_START_DELAY} seconds")
        time.sleep(SERVER_START_DELAY)

        translator = VideoTranslator(server_url="http://127.0.0.1:8000")

        # Translate a video
        video_url = "https://example.com/video.mp4"
        video_id = await translator.translate_video(video_url)
        print(f"Translation job ID: {video_id}")

        # Test retry logic with a status check
        print("Testing retry logic for status checks...")
        try:
            status = await translator.get_video_status(video_id)
            print(f"Status was {status}")
        except PendingStatusException:
            print("Retry logic handled 'pending' status correctly.")

    finally:
        # Terminate the server
        print("Stopping FastAPI server...")
        server_process.terminate()
        server_process.wait()


if __name__ == "__main__":
    asyncio.run(main())
