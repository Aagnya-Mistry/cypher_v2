"""FastAPI entry point. Run from the backend/ folder:  uvicorn app.main:app --reload"""

from fastapi import FastAPI

app = FastAPI(title="cypher-v2")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
