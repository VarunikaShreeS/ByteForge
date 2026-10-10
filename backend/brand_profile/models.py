from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import List, Optional, Dict, Any

class SocialAccount(BaseModel):
    model_config = ConfigDict(extra="allow")
    platform: str 
    handle: str
    profile_url: str
    verified_status: str = "WHITELISTED" 

class MobileApp(BaseModel):
    model_config = ConfigDict(extra="allow")
    store: str    
    app_name: str
    package_name: str
    verified_status: str = "WHITELISTED"  

class SubsidiaryBrand(BaseModel):
    model_config = ConfigDict(extra="allow")
    subsidiary_name: str
    relationship_type: str 
    official_domain: str
    whitelisting_status: str = "verified"  

class OfficialWorker(BaseModel):
    model_config = ConfigDict(extra="allow")
    name: str
    role: str       
    photo_url: str  
    similarity_score_threshold: float = 85.0  

class LookAlikeConfig(BaseModel):
    model_config = ConfigDict(extra="allow")
    allow_character_swaps: bool = True  
    allow_added_words: bool = True     
    phonetic_matching_threshold: int = 20  
    detection_sensitivity: int = 50       

class TrademarkConfig(BaseModel):
    model_config = ConfigDict(extra="allow")
    protected_trademarks: List[str] = []     
    false_positive_filters: List[str] = [] 
    trigger_category: str = "Phishing Intent Detection"  

class BrandProfileCreate(BaseModel):
    model_config = ConfigDict(extra="allow")
    
    company_name: str
    monitored_domain: str
    official_logo_url: str
    
   
    social_accounts: List[SocialAccount] = []
    mobile_apps: List[MobileApp] = []
    
   
    subsidiaries: List[SubsidiaryBrand] = []
    
   
    trademark_config: Optional[TrademarkConfig] = None
    
   
    look_alike_config: Optional[LookAlikeConfig] = None
    
   
    official_workers: List[OfficialWorker] = []

class BrandProfileResponse(BaseModel):
    success: bool = True
    message: str
    data: Optional[Dict[str, Any]] = None