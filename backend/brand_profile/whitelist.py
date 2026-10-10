from brand_profile.database import get_brand_profile

def generate_official_whitelist(brand_id: str) -> dict:
    brand = get_brand_profile(brand_id)
    if not brand:
        return {"error": "Brand not found"}

    whitelist = {
        "brand_id": brand["brand_id"],
        "company_name": brand["company_name"],
        "whitelisted_domains": [brand["monitored_domain"]] + [sub["official_domain"] for sub in brand.get("subsidiaries", [])],
        "whitelisted_handles": {
            acc["platform"].lower(): acc["handle"].lower().strip("@")
            for acc in brand.get("social_accounts", [])
        },
        "whitelisted_packages": [
            app["package_name"] for app in brand.get("mobile_apps", [])
        ],
        "exempt_worker_identities": [
            {
                "name": worker["name"],
                "role": worker["role"],
                "photo_url": worker["photo_url"]
            }
            for worker in brand.get("official_workers", [])
        ],
        "false_positive_filters": brand.get("trademark_config", {}).get("false_positive_filters", [])
    }
    return whitelist