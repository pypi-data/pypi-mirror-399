from functools import wraps
from flask import request, jsonify
from rate_limiter.rate_lmiter import RateLimiter

rate_limiter = RateLimiter()


def rate_limit(**rule):
    """
    Flask decorator to apply rate limiting on routes.

    Example:
        @rate_limit(
            algorithm="sliding_window",
            limit=3,
            window_seconds=60
        )

    Supported Parameters:
        algorithm (str): One of
            - "fixed_window"
            - "sliding_window"
            - "token_bucket"
            - "leaky_bucket"

        Fixed Window / Sliding Window:
            limit (int): Max requests allowed
            window_seconds (int): Time window in seconds

        Token Bucket:
            capacity (int): Max burst size
            refill_rate (int): Tokens added per second

        Leaky Bucket:
            capacity (int): Max queue size
            leak_rate (int): Requests processed per second
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Choose user identity strategy
            user_id = request.headers.get("X-User-ID") or request.remote_addr
            endpoint = request.path

            allowed, retry_after = rate_limiter.check(
                user_id=user_id,
                endpoint=endpoint,
                rule=rule
            )

            if not allowed:
                return jsonify({
                    "error": "Rate limit exceeded",
                    "retry_after_seconds": retry_after
                }), 429

            return func(*args, **kwargs)
        return wrapper
    return decorator
