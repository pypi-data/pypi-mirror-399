from collections import defaultdict
from threading import Lock


class MetricsStore:
    def __init__(self):
        self.lock = Lock()

        self.total_requests = 0
        self.allowed_requests = 0
        self.blocked_requests = 0

        self.per_algorithm = defaultdict(int)
        self.per_endpoint = defaultdict(lambda: {
            "allowed": 0,
            "blocked": 0
        })

    def record(self, endpoint: str, algorithm: str, allowed: bool):
        with self.lock:
            self.total_requests += 1

            if allowed:
                self.allowed_requests += 1
                self.per_endpoint[endpoint]["allowed"] += 1
            else:
                self.blocked_requests += 1
                self.per_endpoint[endpoint]["blocked"] += 1

            self.per_algorithm[algorithm] += 1

    def snapshot(self):
        with self.lock:
            return {
                "total_requests": self.total_requests,
                "allowed_requests": self.allowed_requests,
                "blocked_requests": self.blocked_requests,
                "per_algorithm": dict(self.per_algorithm),
                "per_endpoint": dict(self.per_endpoint)
            }
