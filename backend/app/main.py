from fastapi import FastAPI
from app.routers import apps

app = FastAPI(title="ByteForge DRP - App Store Monitor")

# Register your App Store endpoints
app.include_router(apps.router)

@app.get("/")
def root():
    return {"message": "ByteForge API is running"}