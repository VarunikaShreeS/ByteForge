from fastapi import FastAPI

from social.router import router as social_router

app = FastAPI(
    title="ByteForge API",
    description="Explainable security analysis for social media profiles.",
)

app.include_router(social_router, prefix="/api")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}