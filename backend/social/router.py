from fastapi import APIRouter
from pydantic import BaseModel, Field

from social.social_analysis import (
    AnalysisResult,
    BrandDetails,
    SocialProfile,
    analyse_profiles,
)

router = APIRouter(prefix="/social", tags=["social analysis"])


class SocialAnalysisRequest(BaseModel):
    brand: BrandDetails
    profiles: list[SocialProfile] = Field(max_length=500)


@router.post("/analyse", response_model=AnalysisResult)
def analyse_social_profiles(request: SocialAnalysisRequest) -> AnalysisResult:
    return analyse_profiles(request.brand, request.profiles)
