from fastapi import APIRouter
from app.engine.threat_scorer import calculate_app_risk

router = APIRouter(prefix="/app-scans", tags=["App Store Monitoring"])

@router.post("/scan")
async def run_app_store_scan(brand_name: str, official_publisher: str, official_logo_path: str):
    official_data = {
        "name": brand_name,
        "official_publisher": official_publisher,
        "logo_path": official_logo_path
    }
    
    # For the hackathon, we simulate a detected malicious app
    mock_detected_app = {
        "app_name": f"{brand_name} Support Wallet",
        "publisher": "Unknown Hacker Team",
        "description": f"Urgent KYC verification for {brand_name}. DM for support.",
        "icon_path": official_logo_path # Simulating a 100% stolen icon
    }
    
    analysis_result = calculate_app_risk(official_data, mock_detected_app)
    
    return {
        "status": "scan_complete",
        "detected_app": mock_detected_app["app_name"],
        "threat_analysis": analysis_result
    }