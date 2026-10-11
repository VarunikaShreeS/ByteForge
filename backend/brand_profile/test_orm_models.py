from datetime import timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from auth.models import BusinessAccount
from brand_profile.orm_models import (
    BrandDetectionConfig,
    BrandMobileApp,
    BrandOfficialWorker,
    BrandProfile,
    BrandSocialAccount,
    BrandSubsidiary,
    SocialAnalysis,
)
from database import Base
from social.social_analysis import AnalysisResult, BrandDetails, DetectionSignal, SocialProfile


def _session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, expire_on_commit=False)()


def test_brand_profile_relationships_and_detection_config() -> None:
    db = _session()
    account = BusinessAccount(
        email="owner@example.com",
        business_name="Example",
        password_hash="argon2$placeholder",
    )
    brand = BrandProfile(
        brand_id="BRD-ABC123",
        business_account=account,
        company_name="Example",
        monitored_domain="example.com",
        official_logo_url="https://example.com/logo.png",
        reference_data={},
        social_accounts=[
            BrandSocialAccount(platform="x", handle="@example", profile_url="https://x.com/example")
        ],
        mobile_apps=[
            BrandMobileApp(
                store="google_play",
                app_name="Example",
                package_name="com.example.app",
                publisher="Example",
            )
        ],
        subsidiaries=[
            BrandSubsidiary(
                subsidiary_name="Example Labs",
                relationship_type="subsidiary",
                official_domain="labs.example.com",
            )
        ],
        official_workers=[
            BrandOfficialWorker(name="Owner", role="Founder", photo_url="https://example.com/owner.png")
        ],
        detection_config=BrandDetectionConfig(
            protected_trademarks=["Example"],
            false_positive_filters=["example news"],
        ),
    )
    db.add(brand)
    db.commit()

    loaded = db.query(BrandProfile).filter_by(brand_id="BRD-ABC123").one()
    assert loaded.business_account_id == account.id
    assert loaded.social_accounts[0].handle == "@example"
    assert loaded.mobile_apps[0].package_name == "com.example.app"
    assert loaded.subsidiaries[0].official_domain == "labs.example.com"
    assert loaded.official_workers[0].role == "Founder"
    assert loaded.detection_config is not None
    assert loaded.detection_config.protected_trademarks == ["Example"]
    assert loaded.created_at.tzinfo in (None, timezone.utc)
    db.close()


def test_social_analysis_serializes_nested_analysis_result() -> None:
    db = _session()
    brand = BrandProfile(
        brand_id="BRD-XYZ789",
        company_name="NovaCorp",
        monitored_domain="novacorp.example",
        official_logo_url="",
    )
    result = AnalysisResult(
        analysis_id="ANL-ABC1234567",
        profile=SocialProfile(platform="x", handle="nova_support"),
        matched_brand=BrandDetails(
            name="NovaCorp",
            official_handles=["novacorp"],
            official_domains=["novacorp.example"],
        ),
        risk_score=42,
        detected_signals=[
            DetectionSignal(
                code="scam_language",
                weight=35,
                explanation="Scam language detected.",
            )
        ],
        explanations=["Review this account."],
        findings=[],
        analysed_profiles=1,
        summary={"medium": 1},
    )
    analysis = SocialAnalysis(
        analysis_id=result.analysis_id,
        brand=brand,
        risk_score=result.risk_score,
        risk_category=result.risk_category.value,
        heuristic=result.heuristic,
        analysed_profiles=result.analysed_profiles,
        profile=result.profile.model_dump(mode="json"),
        matched_brand=result.matched_brand.model_dump(mode="json"),
        detected_signals=[
            signal.model_dump(mode="json") for signal in result.detected_signals
        ],
        explanations=result.explanations,
        findings=result.findings,
        summary=result.summary,
    )
    db.add(analysis)
    db.commit()

    loaded = db.query(SocialAnalysis).filter_by(analysis_id="ANL-ABC1234567").one()
    assert loaded.brand.brand_id == "BRD-XYZ789"
    assert loaded.profile["handle"] == "nova_support"
    assert loaded.matched_brand["name"] == "NovaCorp"
    assert loaded.detected_signals[0]["code"] == "scam_language"
    assert loaded.summary == {"medium": 1}
    db.close()
