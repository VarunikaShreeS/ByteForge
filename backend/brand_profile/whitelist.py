import hashlib
from brand_profile.database import get_brand_profile

def generate_official_whitelist(brand_id: str) -> dict:
    brand = get_brand_profile(brand_id)
    if not brand:
        return {"error": "Brand profile configuration not found."}

   
    raw_signature = f"{brand['brand_id']}-{brand['monitored_domain']}-{brand.get('version_hash', '')}"
    trust_passport_token = hashlib.sha256(raw_signature.encode()).hexdigest()

   
    whitelist_package = {
        "brand_id": brand["brand_id"],
        "trust_passport_token": trust_passport_token,
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
                "photo_url": worker["photo_url"],
                "similarity_score_threshold": worker["similarity_score_threshold"]
            }
            for worker in brand.get("official_workers", [])
        ],
        "false_positive_filters": brand.get("trademark_config", {}).get("false_positive_filters", []),
        "look_alike_rules": brand.get("look_alike_config", {})
    }
    return whitelist_package