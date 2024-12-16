import random
import time
import functools

from typing import Callable, Type, Tuple
from httpx import HTTPStatusError
from exceptions.RateLimitExceededException import RateLimitExceededException
from exceptions.PendingStatusException import PendingStatusException


def custom_retry_with_exponential_backoff(
    initial_delay: float = 0.2,  # Initial delay in seconds
    exponential_base: float = 2.0,  # Base for exponential growth
    jitter: bool = True,  # Whether to add jitter
    max_retries: int = 10,  # Maximum number of retries
    max_delay: float = 60.0,  # Maximum delay between retries
    errors: Tuple[Type[Exception], ...] = (
        RateLimitExceededException,
        PendingStatusException,
        HTTPStatusError,
    ),  # Exceptions to catch and retry on
) -> Callable:
    """
    Asynchronous decorator to retry a function with exponential backoff.

    If a RateLimitExceededException is raised, waits for the rate_limit_reset time or the current delay, whichever is longer.

    Args:
        initial_delay (float): Initial delay before the first retry.
        exponential_base (float): Base for exponential backoff calculation.
        jitter (bool): Whether to apply jitter to the backoff delay.
        max_retries (int): Maximum number of retry attempts.
        max_delay (float): Maximum delay between retries.
        errors (Tuple[Type[Exception], ...]): Exceptions that should trigger a retry.

    Returns:
        Callable: The decorated function with retry logic.
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            attempt = 0
            delay = initial_delay

            while attempt < max_retries:
                try:
                    return await func(*args, **kwargs)
                except errors as e:
                    attempt += 1

                    # If maximum retries exceeded, raise the exception
                    if attempt >= max_retries:
                        raise Exception(
                            f"Maximum number of retries ({max_retries}) exceeded."
                        ) from e

                    # Determine the wait time based on exception type
                    if isinstance(e, RateLimitExceededException):
                        print("Capped wait time to rate limit reset time.")
                        wait_time = min(delay, e.rate_limit_reset)
                    else:
                        # Exponential backoff calculation
                        wait_time = delay * (exponential_base ** (attempt - 1))
                    if jitter:
                        wait_time *= 1 + random.random()  # Apply jitter

                    # Cap the wait time to max_delay
                    wait_time = min(wait_time, max_delay)

                    # Optional: Print or log the retry attempt and wait time
                    print(
                        f"Attempt {attempt} failed with {e}. Retrying in {wait_time:.2f} seconds..."
                    )

                    time.sleep(wait_time)

            raise Exception(
                f"Failed to execute {func.__name__} after {max_retries} retries."
            )

        return wrapper

    return decorator
