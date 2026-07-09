from fastapi import FastAPI
from app.routers import claims

app = FastAPI(title="Claims App")

app.include_router(claims.router)

@app.get("/health")
def health():
    return {"status": "ok"}
