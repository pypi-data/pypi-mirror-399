import time
from rate_limiter.config import RATE_LIMIT_RULES
from rate_limiter.strategies.fixed_window import FixedWindowLimiter
from rate_limiter.strategies.sliding_window import SlidingWindowLimiter
from rate_limiter.strategies.tocken_bucket import Token_bucket
from rate_limiter.strategies.leaky_bucket import LeakyBucketLimiter
from rate_limiter.metrics import MetricsStore

class RateLimiter:
    def __init__(self):
        self.metrics=MetricsStore()
        self.strategies = {
            "fixed_window": FixedWindowLimiter(),
            "sliding_window": SlidingWindowLimiter(),
            "token_bucket": Token_bucket(),
            "leaky_bucket": LeakyBucketLimiter()
        }

    def check(self, user_id: str, endpoint: str, rule: dict):
        # Normalize endpoint
        """
        Checks whether a request should be allowed.

        Args:
            user_id (str): Unique user identifier
            endpoint (str): API endpoint being accessed
            rule (dict): Rate limiting configuration

        Returns:
            Tuple[bool, Optional[int]]:
                - allowed (bool)
                - retry_after (int | None)
        """
        if not endpoint.startswith("/"):
            endpoint = "/" + endpoint

        algorithm = rule["algorithm"]
        strategy = self.strategies[algorithm]

        allowed, retry_after = strategy.allow_request(
            user_id=user_id,
            endpoint=endpoint,
            current_time=time.time(),
            rule=rule
        )

        self.metrics.record(endpoint, algorithm, allowed)
        return allowed, retry_after