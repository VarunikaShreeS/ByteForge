from social.social_analysis import (
    BrandDetails,
    RiskType,
    SocialProfile,
    analyse_profiles,
)


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
