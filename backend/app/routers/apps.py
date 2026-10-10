from fastapi import APIRouter
from app.engine.threat_scorer import calculate_app_risk
from brand_profile.whitelist import generate_official_whitelist
from app.engine.takedown import generate_takedown_draft

router = APIRouter(prefix="/app-scans", tags=["App Store Monitoring"])

@router.post("/scan")
async def run_app_store_scan(brand_id: str, detected_app_name: str, detected_publisher: str, detected_desc: str, detected_icon_path: str):
    # 1. Fetch the official brand whitelist to prevent false positives
    whitelist = generate_official_whitelist(brand_id)
    if "error" in whitelist:
        return {"status": "error", "message": "Brand not found. Cannot perform scan."}
        
    official_data = {
        "name": whitelist["company_name"],
        "official_publisher": whitelist["company_name"], 
        "logo_path": "logo.png" # Assuming default logo for hackathon test
    }
    
    detected_app = {
        "app_name": detected_app_name,
        "publisher": detected_publisher,
        "description": detected_desc,
        "icon_path": detected_icon_path
    }

    # 2. Whitelist Check: Ensure we NEVER flag official assets
    if detected_app_name in whitelist.get("whitelisted_packages", []):
        return {
            "status": "scan_complete",
            "detected_app": detected_app_name,
            "threat_analysis": {
                "overall_score": 0,
                "severity": "Safe (Official App)",
                "breakdown": {}
            }
        }

    # 3. Run the AI Threat Scorer for unknown apps
    analysis_result = calculate_app_risk(official_data, detected_app)
    
    # 4. Generate the takedown draft dynamically if risk is critical
    takedown_draft = None
    if analysis_result["severity"] == "Critical":
        takedown_draft = generate_takedown_draft(
            official_brand=official_data["name"], 
            detected_target=detected_app["app_name"], 
            platform="App Store", 
            analysis_data=analysis_result
        )
    
    return {
        "status": "scan_complete",
        "detected_app": detected_app["app_name"],
        "threat_analysis": analysis_result,
        "actionable_intel": {
            "legal_takedown_draft": takedown_draft
        }
    }