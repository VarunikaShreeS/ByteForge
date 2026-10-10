from datetime import datetime

def generate_takedown_draft(official_brand: str, detected_target: str, platform: str, analysis_data: dict) -> str:
    """Generates an evidence-backed legal notice using the AI similarity scores."""
    
    date_str = datetime.utcnow().strftime("%Y-%m-%d")
    
    # Extract the AI evidence your engines already calculated
    name_score = analysis_data.get("breakdown", {}).get("name_match", 0)
    logo_score = analysis_data.get("breakdown", {}).get("logo_match", 0)
    
    draft = f"""NOTICE OF TRADEMARK/COPYRIGHT INFRINGEMENT
Date: {date_str}
To: {platform} Legal / Abuse Department

I am the authorized representative of {official_brand}. We have detected an unauthorized entity operating on your platform under the identity: "{detected_target}".

Our Digital Risk Protection AI has established severe cryptographic and textual impersonation:
- Trademark Name Impersonation: {name_score}% similarity (Jaro-Winkler analysis)
- Copyright Logo Theft: {logo_score}% structural pixel match (SSIM algorithm)

This entity is deploying deceptive phrasing indicating phishing or financial scam intent, posing a critical risk to consumers. 

We request the immediate suspension of this {platform} account/application to prevent further consumer fraud."""
    
    return draft.strip()