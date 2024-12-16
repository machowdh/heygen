from fastapi.testclient import TestClient


def test_invalid_api_key(client: TestClient):
    """
    Test accessing the API with an invalid API key.
    """
    invalid_headers = {"X-Api-Key": "invalid-api-key"}
    video_url = "https://example.com/video.mp4"

    # Attempt to access the /translate/ endpoint with an invalid API key
    response = client.post(
        "/translate/", json={"video_url": video_url}, headers=invalid_headers
    )

    # Assert the response is 401 Unauthorized
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid API Key"}
