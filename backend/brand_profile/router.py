from fastapi import APIRouter, HTTPException, status
from brand_profile.models import BrandProfileCreate, BrandProfileResponse
from brand_profile import database, whitelist

router = APIRouter(prefix="/api/brands", tags=["Brand Profile & Security Engine"])

@router.post("/", response_model=BrandProfileResponse, status_code=status.HTTP_201_CREATED)
def save_complete_brand_profile(profile: BrandProfileCreate):
    """
    Saves complete brand profile data dynamically, handling all 7 security features 
    and ensuring compatibility with any future frontend form expansions.
    """
    try:
        profile_dict = profile.model_dump()
        saved_data = database.save_brand_profile(profile_dict)
        return {
            "success": True,
            "message": "COMPLETE BRAND PROFILE & ALL OFFICIAL WORKERS SUCCESSFULLY EXEMPTED.",
            "data": saved_data
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Secure validation error: {str(e)}"
        )

@router.get("/{brand_id}", response_model=BrandProfileResponse)
def get_brand_profile(brand_id: str):
    """Retrieves full brand configurations for dynamic frontend rendering."""
    profile = database.get_brand_profile(brand_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Brand profile not found.")
    return {
        "success": True,
        "message": "Brand profile retrieved successfully.",
        "data": profile
    }

@router.get("/{brand_id}/whitelist", response_model=BrandProfileResponse)
def get_security_whitelist(brand_id: str):
    """
    Exports the cryptographic Trust Passport and exemption package 
    used by the DRPP detection engine to block false positives.
    """
    result = whitelist.generate_official_whitelist(brand_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return {
        "success": True,
        "message": "Cryptographic Trust Passport and Exemption Package generated.",
        "data": result
    }

@router.get("/audit/logs", response_model=BrandProfileResponse)
def get_audit_trail():
    """Provides enterprise compliance audit logs for security oversight."""
    return {
        "success": True,
        "message": "Audit trail retrieved successfully.",
        "data": {"audit_logs": database.get_audit_trail()}
    }