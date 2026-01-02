from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from rate_limiter.rate_lmiter import RateLimiter


app = FastAPI(title="Rate Limiter Service")

rate_limiter = RateLimiter()


class UserRequest(BaseModel):
    user_id: str
    endpoint: str


@app.post("/rate-limit/check")
def check_rate_limit(request: UserRequest):
    """
    This endpoint checks whether a request should be allowed
    based on rate-limiting rules.
    """
    allowed, retry_after = rate_limiter.check(
        user_id=request.user_id,
        endpoint=request.endpoint
    )

    if allowed:
        return {
            "allowed": True,
            "message": "Request allowed"
        }

    # Request rejected due to rate limiting
    raise HTTPException(
        status_code=429,
        detail={
            "message": "Rate limit exceeded",
            "retry_after_seconds": retry_after
        }
    )


@app.get("/health")
def health_check():
    """
    Health check endpoint (useful for hosting & monitoring)
    """
    return {"status": "ok"}

@app.get("/metrics")
def get_metrics():
    return rate_limiter.metrics.snapshot()
