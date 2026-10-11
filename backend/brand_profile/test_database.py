import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from brand_profile import database
from database import Base


def _sessions():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    return factory(), factory


def _profile(**overrides):
    data = {
        "company_name": "Example",
        "monitored_domain": "example.com",
        "official_logo_url": "https://example.com/logo.png",
        "social_accounts": [
            {"platform": "x", "handle": "@example", "profile_url": "https://x.com/example"}
        ],
        "mobile_apps": [
            {
                "store": "google_play",
                "app_name": "Example",
                "package_name": "com.example.app",
                "publisher": "Example",
            }
        ],
        "subsidiaries": [
            {
                "subsidiary_name": "Example Labs",
                "relationship_type": "subsidiary",
                "official_domain": "labs.example.com",
            }
        ],
        "official_workers": [
            {"name": "Owner", "role": "Founder", "photo_url": "https://example.com/owner.png"}
        ],
        "trademark_config": {
            "protected_trademarks": ["Example"],
            "false_positive_filters": ["example news"],
            "trigger_category": "Phishing Intent Detection",
        },
        "look_alike_config": {
            "allow_character_swaps": True,
            "allow_added_words": False,
            "phonetic_matching_threshold": 20,
            "detection_sensitivity": 50,
        },
    }
    data.update(overrides)
    return data


def test_brand_crud_and_persistence_across_sessions() -> None:
    db, factory = _sessions()
    created = database.save_brand_profile(_profile(), db)
    brand_id = created["brand_id"]
    db.close()

    separate_session = factory()
    loaded = database.get_brand_profile(brand_id, separate_session)
    assert loaded is not None
    assert loaded["company_name"] == "Example"
    assert loaded["social_accounts"][0]["handle"] == "@example"
    assert loaded["mobile_apps"][0]["package_name"] == "com.example.app"
    assert loaded["trademark_config"]["protected_trademarks"] == ["Example"]
    assert [item["brand_id"] for item in database.get_all_brands(separate_session)] == [brand_id]

    updated = database.update_brand_profile(
        brand_id,
        _profile(company_name="Updated Example", social_accounts=[]),
        separate_session,
    )
    assert updated is not None
    assert updated["company_name"] == "Updated Example"
    assert updated["social_accounts"] == []
    separate_session.close()

    delete_session = factory()
    assert database.delete_brand_profile(brand_id, delete_session) is True
    assert database.get_brand_profile(brand_id, delete_session) is None
    assert database.delete_brand_profile(brand_id, delete_session) is False
    delete_session.close()


def test_duplicate_brand_id_is_rejected() -> None:
    db, _ = _sessions()
    database.save_brand_profile(_profile(brand_id="BRD-FIXED1"), db)
    with pytest.raises(ValueError, match="already exists"):
        database.save_brand_profile(_profile(brand_id="BRD-FIXED1"), db)
    db.close()
