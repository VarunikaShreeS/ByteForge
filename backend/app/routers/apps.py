from fastapi import APIRouter
from app.engine.threat_scorer import calculate_app_risk
from app.engine.simulator import generate_mock_app_store

router = APIRouter(prefix="/app-scans", tags=["App Store Monitoring"])

@router.post("/scan")
async def run_app_store_scan(brand_name: str, official_publisher: str, official_logo_path: str):
    official_data = {
        "name": brand_name,
        "official_publisher": official_publisher,
        "logo_path": official_logo_path
    }
    
    # 1. Generate the list of mock apps found in the wild
    apps_in_wild = generate_mock_app_store(brand_name, official_publisher)
    
    # 2. Scan each app and store the results
    scan_results = []
    for detected_app in apps_in_wild:
        analysis_result = calculate_app_risk(official_data, detected_app)
        scan_results.append({
            "detected_app": detected_app["app_name"],
            "publisher": detected_app["publisher"],
            "threat_analysis": analysis_result
        })
    
    # 3. Return the full report
    return {
        "status": "scan_complete",
        "total_apps_scanned": len(apps_in_wild),
        "results": scan_results
    }