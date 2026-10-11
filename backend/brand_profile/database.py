"""Database-backed persistence for brand profiles.

Analysis persistence remains in-memory until the analysis migration is implemented.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from brand_profile.base import Base
from brand_profile.orm_models import (
    BrandDetectionConfig,
    BrandMobileApp,
    BrandOfficialWorker,
    BrandProfile,
    BrandSocialAccount,
    BrandSubsidiary,
)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 1. Setup the local database engine (We will swap the URL to Neon Postgres for deployment)
SQLALCHEMY_DATABASE_URL = "sqlite:///./byteforge.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 2. Define the missing get_db function
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

ANALYSIS_DB: dict[str, dict[str, Any]] = {}


def _isoformat(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.isoformat()


def _load_brand_statement():
    return select(BrandProfile).options(
        selectinload(BrandProfile.social_accounts),
        selectinload(BrandProfile.mobile_apps),
        selectinload(BrandProfile.subsidiaries),
        selectinload(BrandProfile.official_workers),
        selectinload(BrandProfile.detection_config),
    )


def _brand_dict(brand: BrandProfile) -> dict[str, Any]:
    reference = brand.reference_data or {}
    handles = [account.handle for account in brand.social_accounts]
    domains = [subsidiary.official_domain for subsidiary in brand.subsidiaries]
    if brand.monitored_domain:
        domains.insert(0, brand.monitored_domain)

    data: dict[str, Any] = {
        "company_name": brand.company_name,
        "monitored_domain": brand.monitored_domain,
        "official_logo_url": brand.official_logo_url,
        "social_accounts": [
            {
                "platform": account.platform,
                "handle": account.handle,
                "profile_url": account.profile_url,
            }
            for account in brand.social_accounts
        ],
        "mobile_apps": [
            {
                "store": app.store,
                "app_name": app.app_name,
                "package_name": app.package_name,
                "publisher": app.publisher,
            }
            for app in brand.mobile_apps
        ],
        "subsidiaries": [
            {
                "subsidiary_name": subsidiary.subsidiary_name,
                "relationship_type": subsidiary.relationship_type,
                "official_domain": subsidiary.official_domain,
            }
            for subsidiary in brand.subsidiaries
        ],
        "trademark_config": None,
        "look_alike_config": None,
        "official_workers": [
            {
                "name": worker.name,
                "role": worker.role,
                "photo_url": worker.photo_url,
            }
            for worker in brand.official_workers
        ],
        "brand_id": brand.brand_id,
        "created_at": _isoformat(brand.created_at),
    }
    if brand.detection_config:
        config = brand.detection_config
        data["trademark_config"] = {
            "protected_trademarks": list(config.protected_trademarks or []),
            "false_positive_filters": list(config.false_positive_filters or []),
            "trigger_category": config.trigger_category,
        }
        data["look_alike_config"] = {
            "allow_character_swaps": config.allow_character_swaps,
            "allow_added_words": config.allow_added_words,
            "phonetic_matching_threshold": config.phonetic_matching_threshold,
            "detection_sensitivity": config.detection_sensitivity,
        }

    if reference:
        data.update(reference)
    return data


def _child_records(data: dict[str, Any]) -> tuple[list[BrandSocialAccount], ...]:
    social_accounts = [
        BrandSocialAccount(
            platform=item["platform"],
            handle=item["handle"],
            profile_url=item["profile_url"],
        )
        for item in data.get("social_accounts", [])
    ]
    mobile_apps = [
        BrandMobileApp(
            store=item["store"],
            app_name=item["app_name"],
            package_name=item["package_name"],
            publisher=item["publisher"],
        )
        for item in data.get("mobile_apps", [])
    ]
    subsidiaries = [
        BrandSubsidiary(
            subsidiary_name=item["subsidiary_name"],
            relationship_type=item["relationship_type"],
            official_domain=item["official_domain"],
        )
        for item in data.get("subsidiaries", [])
    ]
    workers = [
        BrandOfficialWorker(
            name=item["name"],
            role=item["role"],
            photo_url=item["photo_url"],
        )
        for item in data.get("official_workers", [])
    ]
    return social_accounts, mobile_apps, subsidiaries, workers


def _set_brand_values(brand: BrandProfile, data: dict[str, Any]) -> None:
    brand.company_name = data["company_name"]
    brand.monitored_domain = data["monitored_domain"]
    brand.official_logo_url = data["official_logo_url"]
    brand.reference_data = {
        key: data[key]
        for key in (
            "name",
            "official_username",
            "official_handles",
            "official_domain",
            "official_domains",
            "official_website",
            "logo_url",
        )
        if key in data
    }
    social_accounts, mobile_apps, subsidiaries, workers = _child_records(data)
    brand.social_accounts = social_accounts
    brand.mobile_apps = mobile_apps
    brand.subsidiaries = subsidiaries
    brand.official_workers = workers

    trademark = data.get("trademark_config")
    look_alike = data.get("look_alike_config")
    if trademark is None and look_alike is None:
        brand.detection_config = None
    else:
        trademark = trademark or {}
        look_alike = look_alike or {}
        config = brand.detection_config
        if config is None:
            config = BrandDetectionConfig()
            brand.detection_config = config
        config.allow_character_swaps = look_alike.get("allow_character_swaps", True)
        config.allow_added_words = look_alike.get("allow_added_words", True)
        config.phonetic_matching_threshold = look_alike.get("phonetic_matching_threshold", 20)
        config.detection_sensitivity = look_alike.get("detection_sensitivity", 50)
        config.protected_trademarks = list(trademark.get("protected_trademarks", []))
        config.false_positive_filters = list(trademark.get("false_positive_filters", []))
        config.trigger_category = trademark.get("trigger_category", "Phishing Intent Detection")


def save_brand_profile(data: dict, db: Session) -> dict:
    brand_id = data.get("brand_id") or f"BRD-{uuid.uuid4().hex[:6].upper()}"
    if db.scalar(select(BrandProfile).where(BrandProfile.brand_id == brand_id)):
        raise ValueError(f"Brand profile '{brand_id}' already exists.")

    brand = BrandProfile(brand_id=brand_id)
    _set_brand_values(brand, data)
    db.add(brand)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ValueError(f"Brand profile '{brand_id}' already exists.") from exc
    db.refresh(brand)
    return _brand_dict(brand)


def get_brand_profile(brand_id: str, db: Session) -> dict[str, Any] | None:
    brand = db.scalar(_load_brand_statement().where(BrandProfile.brand_id == brand_id))
    return _brand_dict(brand) if brand else None


def get_all_brands(db: Session) -> list[dict[str, Any]]:
    brands = db.scalars(_load_brand_statement().order_by(BrandProfile.created_at)).all()
    return [_brand_dict(brand) for brand in brands]


def update_brand_profile(brand_id: str, data: dict, db: Session) -> dict[str, Any] | None:
    brand = db.scalar(_load_brand_statement().where(BrandProfile.brand_id == brand_id))
    if not brand:
        return None
    brand.social_accounts.clear()
    brand.mobile_apps.clear()
    brand.subsidiaries.clear()
    brand.official_workers.clear()
    db.flush()
    _set_brand_values(brand, data)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ValueError(f"Brand profile '{brand_id}' could not be updated.") from exc
    db.refresh(brand)
    return _brand_dict(brand)


def delete_brand_profile(brand_id: str, db: Session) -> bool:
    brand = db.scalar(select(BrandProfile).where(BrandProfile.brand_id == brand_id))
    if not brand:
        return False
    db.delete(brand)
    db.commit()
    return True


def save_analysis(data: dict) -> dict:
    ANALYSIS_DB[data["analysis_id"]] = data
    return data


def get_analysis(analysis_id: str) -> dict | None:
    return ANALYSIS_DB.get(analysis_id)


