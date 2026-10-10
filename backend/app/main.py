from fastapi import FastAPI
<<<<<<< HEAD
from app.routers import apps

app = FastAPI(title="ByteForge DRP - App Store Monitor")

# Register your App Store endpoints
app.include_router(apps.router)

@app.get("/")
def root():
    return {"message": "ByteForge API is running"}
=======

from social.router import router as social_router

app = FastAPI(
    title="ByteForge API",
    description="Explainable security analysis for social media profiles.",
)

app.include_router(social_router, prefix="/api")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
>>>>>>> db0b2a33d221f76beac37d4420d0b9abcbdf2525
