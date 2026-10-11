from fastapi import FastAPI

from routers.auth import router as auth_router
from brand_profile.base import Base
from brand_profile.database import engine
from fastapi.middleware.cors import CORSMiddleware
from social.router import router as social_router

app = FastAPI(
    title="ByteForge API",
    description="Explainable security analysis for social media profiles.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(social_router, prefix="/api")
app.include_router(auth_router, prefix="/api")


@app.on_event("startup")
def initialize_database() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}