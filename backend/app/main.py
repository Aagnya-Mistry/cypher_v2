"""FastAPI entry point. Run from the backend/ folder:  uvicorn app.main:app --reload"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(title="cypher-v2")

# Only our own frontend may call this API from a browser. Logins travel in the Authorization
# header, not cookies, so credentials mode stays off (v1 had CORS "*" with credentials).
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(auth.router, prefix="/api")


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}
