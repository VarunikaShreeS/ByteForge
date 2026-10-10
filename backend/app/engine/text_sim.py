from rapidfuzz import fuzz

def calculate_name_similarity(official_name: str, detected_name: str) -> float:
    """Returns a score from 0 to 100 based on typosquatting similarity."""
    # Uses Jaro-Winkler/Levenshtein ratio to catch tricks like "F1ntechXYZ" or "Fintech_Support"
    return fuzz.WRatio(official_name.lower(), detected_name.lower())

def analyze_description(description: str, brand_name: str) -> float:
    """Scores the risk of the description resembling the brand maliciously."""
    risk_score = 0.0
    desc_lower = description.lower()
    
    # Penalize if it mimics the brand but includes scam keywords
    scam_keywords = ["claim free reward", "dm for support", "urgent kyc", "seed phrase"]
    
    if brand_name.lower() in desc_lower:
        risk_score += 40.0  # High baseline if they use the trademark
        
    for word in scam_keywords:
        if word in desc_lower:
            risk_score += 30.0  # Add risk for deceptive phrasing
            
    return min(risk_score, 100.0)