from fastapi import APIRouter, Depends, HTTPException
from brand_profile.models import BrandProfileCreate, BrandProfileResponse
from brand_profile import database, whitelist
from database import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/brands", tags=["Brand Profile & Monitoring Settings"])

@router.post("/", response_model=BrandProfileResponse, status_code=201)
def create_brand_profile(profile: BrandProfileCreate, db: Session = Depends(get_db)):
    """
    Saves the complete enterprise brand profile including identity, 
    social handles, apps, subsidiaries, look-alike rules, and official workers.
    """
    profile_dict = profile.model_dump()
    try:
        saved_data = database.save_brand_profile(profile_dict, db)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return saved_data

@router.get("/{brand_id}", response_model=BrandProfileResponse)
def get_brand_profile(brand_id: str, db: Session = Depends(get_db)):
    """Retrieve full configuration settings for a registered brand."""
    profile = database.get_brand_profile(brand_id, db)
    if not profile:
        raise HTTPException(status_code=404, detail="Brand profile configuration not found.")
    return profile

@router.get("/{brand_id}/whitelist", summary="Exemption Package for AI Engines")
def get_brand_whitelist(brand_id: str, db: Session = Depends(get_db)):
    """
    Generates the strict whitelist package used by detection engines 
    to guarantee official accounts, subsidiaries, and workers are never flagged.
    """
    result = whitelist.generate_official_whitelist(brand_id, db)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result