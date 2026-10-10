from __future__ import annotations

import re
from difflib import SequenceMatcher
from enum import Enum
from urllib.parse import urlparse

from pydantic import BaseModel, Field


class RiskType(str, Enum):
    BRAND_IMPERSONATION = "brand_impersonation"
    FAKE_COMPANY_PAGE = "fake_company_page"
    SCAM_PROFILE = "scam_profile"
    BRAND_SIMILARITY = "brand_similarity"


class BrandDetails(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    official_handles: list[str] = Field(default_factory=list)
    official_domains: list[str] = Field(default_factory=list)
    logo_url: str | None = None


class SocialProfile(BaseModel):
    platform: str = Field(min_length=1, max_length=50)
    handle: str = Field(min_length=1, max_length=200)
    display_name: str = Field(default="", max_length=200)
    bio: str = Field(default="", max_length=2_000)
    profile_url: str | None = None
    website: str | None = None
    has_verified_badge: bool = False
    logo_match: bool | None = None


class Finding(BaseModel):
    profile: str
    risk_type: RiskType
    severity: str
    confidence: float = Field(ge=0, le=1)
    reasons: list[str]


class AnalysisResult(BaseModel):
    findings: list[Finding]
    analysed_profiles: int
    summary: dict[str, int]


_SCAM_TERMS = {
    "claim prize",
    "claim your prize",
    "giveaway",
    "guaranteed returns",
    "investment opportunity",
    "limited time offer",
    "send crypto",
    "send money",
    "whatsapp me",
    "telegram me",
    "double your money",
}
_COMPANY_TERMS = {
    "official",
    "customer support",
    "support",
    "help desk",
    "customer care",
    "careers",
    "human resources",
    "investor relations",
}
_SEVERITY_ORDER = {"low": 0, "medium": 1, "high": 2, "critical": 3}


def _normalise(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.casefold())


def _domain(value: str | None) -> str:
    if not value:
        return ""
    parsed = urlparse(value if "://" in value else f"https://{value}")
    return parsed.netloc.casefold().removeprefix("www.")


def _similarity(left: str, right: str) -> float:
    return SequenceMatcher(None, _normalise(left), _normalise(right)).ratio()


def _is_official(profile: SocialProfile, brand: BrandDetails) -> bool:
    handle = _normalise(profile.handle).removeprefix("at")
    official_handles = {
        _normalise(item).removeprefix("at") for item in brand.official_handles
    }
    profile_domain = _domain(profile.website)
    official_domains = {_domain(item) for item in brand.official_domains}
    return (
        handle in official_handles
        or bool(profile_domain and profile_domain in official_domains)
    )


def analyse_profiles(
    brand: BrandDetails, profiles: list[SocialProfile]
) -> AnalysisResult:
    findings: list[Finding] = []
    for profile in profiles:
        if _is_official(profile, brand):
            continue

        name_similarity = max(
            _similarity(profile.handle, brand.name),
            _similarity(profile.display_name, brand.name),
        )
        branding_reasons: list[str] = []
        if name_similarity >= 0.72:
            branding_reasons.append(
                f"profile name or handle is {name_similarity:.0%} similar to the brand name"
            )
        if profile.logo_match is True:
            branding_reasons.append("profile logo matches the supplied brand logo")

        if branding_reasons:
            findings.append(
                Finding(
                    profile=profile.handle,
                    risk_type=RiskType.BRAND_SIMILARITY,
                    severity="high" if profile.logo_match else "medium",
                    confidence=min(
                        0.99,
                        name_similarity + (0.2 if profile.logo_match else 0),
                    ),
                    reasons=branding_reasons,
                )
            )

        text = f"{profile.display_name} {profile.bio}".casefold()
        scam_terms = sorted(term for term in _SCAM_TERMS if term in text)
        if scam_terms:
            findings.append(
                Finding(
                    profile=profile.handle,
                    risk_type=RiskType.SCAM_PROFILE,
                    severity="high" if len(scam_terms) > 1 else "medium",
                    confidence=min(0.95, 0.55 + len(scam_terms) * 0.12),
                    reasons=[f"contains scam indicator: {term}" for term in scam_terms],
                )
            )

        company_terms = sorted(term for term in _COMPANY_TERMS if term in text)
        profile_domain = _domain(profile.website)
        official_domains = {_domain(item) for item in brand.official_domains}
        uses_untrusted_domain = bool(
            profile_domain
            and official_domains
            and profile_domain not in official_domains
        )
        if company_terms and (uses_untrusted_domain or not profile.has_verified_badge):
            reasons = [f"uses company-style wording: {term}" for term in company_terms]
            if uses_untrusted_domain:
                reasons.append(f"website domain is not an official domain: {profile_domain}")
            if not profile.has_verified_badge:
                reasons.append("profile is not verified")
            findings.append(
                Finding(
                    profile=profile.handle,
                    risk_type=RiskType.FAKE_COMPANY_PAGE,
                    severity="high" if uses_untrusted_domain else "medium",
                    confidence=min(0.94, 0.62 + (0.15 if uses_untrusted_domain else 0)),
                    reasons=reasons,
                )
            )

        if branding_reasons and (
            not profile.has_verified_badge or uses_untrusted_domain
        ):
            reasons = [
                "brand-like account is not the known official handle or domain",
                *branding_reasons,
            ]
            if not profile.has_verified_badge:
                reasons.append("profile is not verified")
            if uses_untrusted_domain:
                reasons.append("website domain does not match an official domain")
            findings.append(
                Finding(
                    profile=profile.handle,
                    risk_type=RiskType.BRAND_IMPERSONATION,
                    severity="critical" if profile.logo_match else "high",
                    confidence=min(
                        0.98,
                        0.7
                        + (0.15 if profile.logo_match else 0)
                        + (0.1 if uses_untrusted_domain else 0),
                    ),
                    reasons=reasons,
                )
            )

    summary = {severity: 0 for severity in _SEVERITY_ORDER}
    for finding in findings:
        summary[finding.severity] += 1
    findings.sort(
        key=lambda finding: (
            -_SEVERITY_ORDER[finding.severity],
            -finding.confidence,
            finding.profile.casefold(),
        )
    )
    return AnalysisResult(
        findings=findings,
        analysed_profiles=len(profiles),
        summary=summary,
    )
