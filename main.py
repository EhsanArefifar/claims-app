from fastapi import FastAPI

app = FastAPI(title="Claims App")

@app.get("/health")
def health():
    return {"status": "ok"}
