from fastapi import FastAPI

from app.logging_config import configure_logging
from app.middleware import RequestLoggingMiddleware
from app.routers import claims

# Configure structlog before anything else runs
configure_logging()

app = FastAPI(title="Claims App")

# Middleware is applied outside-in: this wraps every request, including /health
app.add_middleware(RequestLoggingMiddleware)

app.include_router(claims.router)


@app.get("/health")
def health():
    return {"status": "ok!"}
