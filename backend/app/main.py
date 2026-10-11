from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.apps import router as apps_router
from brand_profile.router import router as brand_profile_router

app = FastAPI(
    title="Sentinel AI API",
    description="Digital Risk Protection Platform",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(apps_router)
app.include_router(brand_profile_router)


@app.get("/")
def home():
    return {"message": "Sentinel AI API is running"}


@app.get("/health")
def health():
    return {"status": "healthy"}
