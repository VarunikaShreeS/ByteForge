from app.engine.text_sim import calculate_name_similarity, analyze_description
from app.engine.image_sim import calculate_logo_similarity

def calculate_app_risk(official_data: dict, detected_app: dict) -> dict:
    """Analyzes all mandatory app store parameters to output a final severity."""
    
    # 1. Check Similar App Names
    name_score = calculate_name_similarity(official_data["name"], detected_app["app_name"])
    
    # 2. Check Brand/Logo Impersonation
    logo_score = calculate_logo_similarity(official_data["logo_path"], detected_app["icon_path"])
    
    # 3. Check App Descriptions
    desc_score = analyze_description(detected_app["description"], official_data["name"])
    
    # 4. Check Different Developers/Publishers
    publisher_mismatch_risk = 0.0
    if official_data["official_publisher"].lower() != detected_app["publisher"].lower():
        publisher_mismatch_risk = 100.0 # Huge red flag if publishers don't match
        
    # Calculate Final Weighted Score (0-100)
    final_risk = (0.30 * logo_score) + (0.25 * name_score) + (0.25 * desc_score) + (0.20 * publisher_mismatch_risk)
    
    # Assign Label
    if final_risk >= 85:
        severity = "Critical"
    elif final_risk >= 70:
        severity = "High"
    elif final_risk >= 40:
        severity = "Medium"
    else:
        severity = "Low"
        
    return {
        "overall_score": round(final_risk, 2),
        "severity": severity,
        "breakdown": {
            "name_match": name_score,
            "logo_match": logo_score,
            "publisher_mismatch": publisher_mismatch_risk > 0
        }
    }