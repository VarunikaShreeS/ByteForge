from social.social_analysis import (
    BrandDetails,
    RiskType,
    SocialProfile,
    analyse_profiles,
)
from pydantic import ValidationError


def test_detects_impersonation_and_scam_signals() -> None:
    result = analyse_profiles(
        BrandDetails(
            name="Acme Bank",
            official_handles=["acmebank"],
            official_domains=["acmebank.example"],
        ),
        [
            SocialProfile(
                platform="instagram",
                handle="acme_bank_support",
                display_name="Acme Bank Official Support",
                bio="Claim prize now. WhatsApp me for guaranteed returns.",
                website="https://acme-bank-help.example",
                logo_match=True,
            )
        ],
    )

    risk_types = {finding.risk_type for finding in result.findings}
    assert RiskType.BRAND_IMPERSONATION in risk_types
    assert RiskType.SCAM_PROFILE in risk_types
    assert RiskType.FAKE_COMPANY_PAGE in risk_types


def test_does_not_flag_known_official_profile() -> None:
    result = analyse_profiles(
        BrandDetails(
            name="Acme",
            official_handles=["acme"],
            official_domains=["acme.example"],
        ),
        [
            SocialProfile(
                platform="x",
                handle="acme",
                display_name="Acme",
                website="https://acme.example",
                has_verified_badge=True,
            )
        ],
    )

    assert result.findings == []


def _nova_brand() -> BrandDetails:
    return BrandDetails(
        name="NovaCorp",
        official_handles=["novacorp"],
        official_domains=["novacorp.example"],
    )


def test_exact_official_username_is_low_risk() -> None:
    result = analyse_profiles(
        _nova_brand(),
        [SocialProfile(platform="x", handle="novacorp", display_name="NovaCorp")],
    )

    assert result.risk_score == 0
    assert result.risk_category.value == "Low"
    assert result.findings == []


def test_zero_substitution_has_distinct_similarity_signal() -> None:
    result = analyse_profiles(
        _nova_brand(),
        [SocialProfile(platform="x", handle="n0vacorp", display_name="N0vaCorp")],
    )

    assert "suspicious_brand_name_similarity" in {
        signal.code for signal in result.detected_signals
    }
    assert result.risk_score > 0


def test_inserted_separators_have_distinct_similarity_signal() -> None:
    result = analyse_profiles(
        _nova_brand(),
        [SocialProfile(platform="x", handle="nova_corp")],
    )

    assert "suspicious_brand_name_similarity" in {
        signal.code for signal in result.detected_signals
    }


def test_similar_display_name_with_suffix_is_evidence_not_verdict() -> None:
    result = analyse_profiles(
        _nova_brand(),
        [SocialProfile(platform="x", handle="nova_news", display_name="NovaCorp Refund")],
    )

    assert "suspicious_brand_name_similarity" in {
        signal.code for signal in result.detected_signals
    }
    assert result.risk_score < 65


def test_lookalike_domain_is_scored_separately() -> None:
    result = analyse_profiles(
        _nova_brand(),
        [SocialProfile(platform="x", handle="novacorp-help", website="https://novacorp-support.example")],
    )

    signals = {signal.code for signal in result.detected_signals}
    assert "lookalike_domain" in signals
    assert "external_domain" not in signals


def test_exact_official_domain_is_not_a_domain_risk() -> None:
    result = analyse_profiles(
        _nova_brand(),
        [SocialProfile(platform="x", handle="news-account", website="https://www.novacorp.example")],
    )

    signals = {signal.code for signal in result.detected_signals}
    assert "lookalike_domain" not in signals
    assert "external_domain" not in signals


def test_unrelated_account_with_similar_word_stays_low_risk() -> None:
    result = analyse_profiles(
        BrandDetails(
            name="Orbit",
            official_handles=["orbit"],
            official_domains=["orbit.example"],
        ),
        [SocialProfile(platform="x", handle="orbiting_travel", display_name="Orbiting Travel")],
    )

    assert result.risk_score < 35
    assert RiskType.BRAND_IMPERSONATION not in {
        finding.risk_type for finding in result.findings
    }


def test_missing_and_invalid_fields_are_handled() -> None:
    try:
        SocialProfile(platform="x")  # type: ignore[call-arg]
    except ValidationError:
        pass
    else:
        raise AssertionError("missing handle should fail validation")

    result = analyse_profiles(
        _nova_brand(),
        [SocialProfile(platform="x", handle="unrelated", website="not a valid url")],
    )
    assert result.risk_score == 0
    assert any("invalid" in explanation.lower() for explanation in result.explanations)
