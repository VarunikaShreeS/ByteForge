import uuid
from datetime import datetime
from typing import Dict, Any

BRAND_DB: Dict[str, Dict[str, Any]] = {}
AUDIT_LOGS: list = []

def save_brand_profile(data: dict) -> dict:
    brand_id = f"BRD-{uuid.uuid4().hex[:6].upper()}"
    version_hash = uuid.uuid4().hex
    
    data["brand_id"] = brand_id
    data["version_hash"] = version_hash
    data["created_at"] = datetime.utcnow().isoformat()
    
    BRAND_DB[brand_id] = data
    
   
    AUDIT_LOGS.append({
        "timestamp": data["created_at"],
        "action": "SAVE_COMPLETE_BRAND_PROFILE",
        "brand_id": brand_id,
        "version_hash": version_hash
    })
    
    return data

def get_brand_profile(brand_id: str) -> dict | None:
    return BRAND_DB.get(brand_id)

def get_audit_trail() -> list:
    return AUDIT_LOGS