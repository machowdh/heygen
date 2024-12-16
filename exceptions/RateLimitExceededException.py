class RateLimitExceededException(Exception):
    def __init__(self, rate_limit_reset: int):
        super().__init__(
            f"Rate limit exceeded. Retry after {rate_limit_reset} seconds."
        )
        self.rate_limit_reset = rate_limit_reset
