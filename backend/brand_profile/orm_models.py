"""SQLAlchemy models for persistent brand profiles and social analyses."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from brand_profile.base import Base
if TYPE_CHECKING:
    from auth.models import BusinessAccount


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class BrandProfile(Base):
    __tablename__ = "brand_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    brand_id: Mapped[str] = mapped_column(String(32), unique=True, index=True, nullable=False)
    business_account_id: Mapped[int | None] = mapped_column(
        ForeignKey("business_accounts.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    company_name: Mapped[str] = mapped_column(String(200), nullable=False)
    monitored_domain: Mapped[str] = mapped_column(String(253), nullable=False)
    official_logo_url: Mapped[str] = mapped_column(String(2_000), nullable=False)
    reference_data: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )

    business_account: Mapped[BusinessAccount | None] = relationship("BusinessAccount")
    social_accounts: Mapped[list[BrandSocialAccount]] = relationship(
        back_populates="brand", cascade="all, delete-orphan"
    )
    mobile_apps: Mapped[list[BrandMobileApp]] = relationship(
        back_populates="brand", cascade="all, delete-orphan"
    )
    subsidiaries: Mapped[list[BrandSubsidiary]] = relationship(
        back_populates="brand", cascade="all, delete-orphan"
    )
    official_workers: Mapped[list[BrandOfficialWorker]] = relationship(
        back_populates="brand", cascade="all, delete-orphan"
    )
    detection_config: Mapped[BrandDetectionConfig | None] = relationship(
        back_populates="brand", cascade="all, delete-orphan", uselist=False
    )
    analyses: Mapped[list[SocialAnalysis]] = relationship(back_populates="brand")


class BrandSocialAccount(Base):
    __tablename__ = "brand_social_accounts"
    __table_args__ = (
        UniqueConstraint("brand_profile_id", "platform", "handle", name="uq_brand_social_account"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    brand_profile_id: Mapped[int] = mapped_column(
        ForeignKey("brand_profiles.id", ondelete="CASCADE"), index=True, nullable=False
    )
    platform: Mapped[str] = mapped_column(String(50), nullable=False)
    handle: Mapped[str] = mapped_column(String(200), nullable=False)
    profile_url: Mapped[str] = mapped_column(String(2_000), nullable=False)

    brand: Mapped[BrandProfile] = relationship(back_populates="social_accounts")


class BrandMobileApp(Base):
    __tablename__ = "brand_mobile_apps"
    __table_args__ = (
        UniqueConstraint("brand_profile_id", "store", "package_name", name="uq_brand_mobile_app"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    brand_profile_id: Mapped[int] = mapped_column(
        ForeignKey("brand_profiles.id", ondelete="CASCADE"), index=True, nullable=False
    )
    store: Mapped[str] = mapped_column(String(100), nullable=False)
    app_name: Mapped[str] = mapped_column(String(200), nullable=False)
    package_name: Mapped[str] = mapped_column(String(300), nullable=False)
    publisher: Mapped[str] = mapped_column(String(200), nullable=False)

    brand: Mapped[BrandProfile] = relationship(back_populates="mobile_apps")


class BrandSubsidiary(Base):
    __tablename__ = "brand_subsidiaries"

    id: Mapped[int] = mapped_column(primary_key=True)
    brand_profile_id: Mapped[int] = mapped_column(
        ForeignKey("brand_profiles.id", ondelete="CASCADE"), index=True, nullable=False
    )
    subsidiary_name: Mapped[str] = mapped_column(String(200), nullable=False)
    relationship_type: Mapped[str] = mapped_column(String(100), nullable=False)
    official_domain: Mapped[str] = mapped_column(String(253), nullable=False)

    brand: Mapped[BrandProfile] = relationship(back_populates="subsidiaries")


class BrandOfficialWorker(Base):
    __tablename__ = "brand_official_workers"

    id: Mapped[int] = mapped_column(primary_key=True)
    brand_profile_id: Mapped[int] = mapped_column(
        ForeignKey("brand_profiles.id", ondelete="CASCADE"), index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    role: Mapped[str] = mapped_column(String(200), nullable=False)
    photo_url: Mapped[str] = mapped_column(String(2_000), nullable=False)

    brand: Mapped[BrandProfile] = relationship(back_populates="official_workers")


class BrandDetectionConfig(Base):
    __tablename__ = "brand_detection_configs"

    id: Mapped[int] = mapped_column(primary_key=True)
    brand_profile_id: Mapped[int] = mapped_column(
        ForeignKey("brand_profiles.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    allow_character_swaps: Mapped[bool] = mapped_column(nullable=False, default=True)
    allow_added_words: Mapped[bool] = mapped_column(nullable=False, default=True)
    phonetic_matching_threshold: Mapped[int] = mapped_column(Integer, nullable=False, default=20)
    detection_sensitivity: Mapped[int] = mapped_column(Integer, nullable=False, default=50)
    protected_trademarks: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    false_positive_filters: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    trigger_category: Mapped[str] = mapped_column(
        String(200), nullable=False, default="Phishing Intent Detection"
    )

    brand: Mapped[BrandProfile] = relationship(back_populates="detection_config")


class SocialAnalysis(Base):
    __tablename__ = "social_analyses"

    id: Mapped[int] = mapped_column(primary_key=True)
    analysis_id: Mapped[str] = mapped_column(String(32), unique=True, index=True, nullable=False)
    brand_profile_id: Mapped[int | None] = mapped_column(
        ForeignKey("brand_profiles.id", ondelete="SET NULL"), index=True, nullable=True
    )
    risk_score: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    risk_category: Mapped[str] = mapped_column(String(32), nullable=False, default="Low")
    heuristic: Mapped[bool] = mapped_column(nullable=False, default=True)
    analysed_profiles: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    profile: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    matched_brand: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    detected_signals: Mapped[list[dict[str, Any]]] = mapped_column(JSON, nullable=False, default=list)
    explanations: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    findings: Mapped[list[dict[str, Any]]] = mapped_column(JSON, nullable=False, default=list)
    summary: Mapped[dict[str, int]] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    brand: Mapped[BrandProfile | None] = relationship(back_populates="analyses")
