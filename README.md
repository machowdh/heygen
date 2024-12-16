# HeyGen Video Translation Client Library and Server Simulation

## Overview

This project simulates a video translation server using FastAPI. The client library uses `httpx` and a custom retry with backoff implementation to promote retrying based on rate limits set in the server.

### Problem Statement

The server simulates a backend status API for video translation, which can return one of the following statuses:
- `pending` - Default state of the video.
- `completed` - Returns when randomized delay in the `GET` endpoint is bigger than the one associated with the video in the database.
- `error` - I decided to make this trigger/be synonymous with HTTP errors like authorization or requesting a video id not in the databse.

---
## Installation

1. Ensure `install.sh` is executable.
2. Run using `./install.sh`
3. Activate the virtual environment: `source .venv/bin/activate`
4. To run the FastAPI server from root: `uvicorn app.main:app --reload`
5. View docs at `/docs` or `/redoc`

---
## Implementation

The problem statement discussed the backend returning `pending` until a configurable time has passed. 

I decided to implement this as storing a randomized integer delay generated during the `POST` request, and initially storing the status of the video's completion as 'pending'. This 'pending' remains the default behavior until the get status rolls for an `elapsed_time` that is higher than this saved delay.

### Authorization

Authorization is handled as injected FastAPI Security dependency across endpoints using APIKeyHeader. For simplicity, it is retrieved from the local repo `.env` and compared across an in-memory database of valid users. There is one valid key for the client and one valid key for the test client.

To test, change the `VideoTranslator.__init__()` to use a different key.

### Retries

To simplify status retrieval for the end-user, I used two approaches:

1. On the server, I added rate limiting using `fastapi-limiter` and Redis. The default callback of the limiter is used to confer information from the `x-Retry-After` header to the client systematically update the backoff calculation using a few custom exceptions.

2. On the client, I implemented a custom retry decorator that will wait until the rate limit has been reset, rather than naively trying on all exceptions similarly. See `client/utils/retry.py`. This is a semi greedy but cautious approach as backoff will still apply in the event our rate limit is not 
exceeded, but will still try to get the video status as soon as the rate limits are reset + some jitter.

3. The rate limits and retry numbers used in the endpoints are for demonstration purposes rather than simulating real time; often the random roll will complete the video status given a small enough `randint(start, end)` range. To see the backoff mechanism at play, one can modify the `GET /status{video_id}` endpoint and reduce the likelihood of rolling relative to the range defined in the `POST` endpoint.


### Client

Beyond the above retry mechanisms, the client uses an in-memory set to keep track of requested video urls and their IDs, preempting a use case where the client erroneously or intentionally triggers a POST request on the same video URL. 

---

## Testing

### Unit Tests

There are a few unit test for auth, rate limits, and the routes, which can be run using `pytest app/tests`.

### Integration Test

To see the server and client be used together, run `uv run integration_test.py` if using uv, or `python integration_test.py` from your activated virtual environment. This spins up the server in a subprocess and the client to request translation for an example video, and then tries to get the status of the video until it returns completed.

---

## Project Structure

```plaintext
├── README.md
├── app                                     # FastAPI backend
│   ├── api         
│   │   └── routes
│   │       └── translate.py                # Endpoints for generating video jobs and querying status
│   ├── auth.py                             # Header-based api auth
│   ├── db.py                               # SQLite DB dependency
│   ├── main.py                             # Initialize FastAPI app
│   ├── models.py                           # Video and response models
│   ├── tests                               # Tests for routes, auth, and rate limits
│   │   ├── api
│   │   │   └── routes
│   │   │       └── test_translate.py
│   │   ├── conftest.py                     # Test config
│   │   ├── test_auth.py
│   │   └── test_limit.py
├── client
│   ├── utils
│   │   └── retry.py                        # Custom backoff with rate limit consideration
│   └── video_translator.py                 # Client library to consume API
├── exceptions
│   ├── PendingStatusException.py
│   └── RateLimitExceededException.py
├── heygen.db                               # "prod" db
├── install.sh                              # installation script
├── integration_test.py                     # Demos the client lib and server
├── pyproject.toml                         
├── test.db                                 # "test" db
└── uv.lock