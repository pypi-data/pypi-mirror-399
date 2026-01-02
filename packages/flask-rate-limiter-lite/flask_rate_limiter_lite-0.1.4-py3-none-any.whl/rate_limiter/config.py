RATE_LIMIT_RULES = {
    "/login": {
        "algorithm": "sliding_window",
        "limit": 5,
        "window_seconds": 300
    },
    "/otp/resend": {
        "algorithm": "fixed_window",
        "limit": 1,
        "window_seconds": 30
    },
    "/search": {
        "algorithm": "token_bucket",
        "capacity": 10,
        "refill_rate": 1
    },
    "/payments": {
        "algorithm": "leaky_bucket",
        "queue_size": 5,
        "leak_rate": 1
    }
}
