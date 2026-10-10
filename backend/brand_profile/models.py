from pydantic import BaseModel, Field
from typing import List, Optional

class SocialAccount(BaseModel):
    platform: str  
    handle: str    
    profile_url: str

class MobileApp(BaseModel):
    store: str    
    app_name: str
    package_name: str
    publisher: str

class SubsidiaryBrand(BaseModel):
    subsidiary_name: str
    relationship_type: str  
    official_domain: str

class OfficialWorker(BaseModel):
    name: str
    role: str       
    photo_url: str  

class LookAlikeConfig(BaseModel):
    allow_character_swaps: bool = True
    allow_added_words: bool = True
    phonetic_matching_threshold: int = 20 
    detection_sensitivity: int = 50        

class TrademarkConfig(BaseModel):
    protected_trademarks: List[str] = []
    false_positive_filters: List[str] = []  
    trigger_category: str = "Phishing Intent Detection"

class BrandProfileCreate(BaseModel):
   
    company_name: str
    monitored_domain: str
    official_logo_url: str
    
   
    social_accounts: List[SocialAccount] = []
    mobile_apps: List[MobileApp] = []
    
    
    subsidiaries: List[SubsidiaryBrand] = []
    
    
    trademark_config: Optional[TrademarkConfig] = None
    
   
    look_alike_config: Optional[LookAlikeConfig] = None
    
    
    official_workers: List[OfficialWorker] = []

class BrandProfileResponse(BrandProfileCreate):
    brand_id: str
    created_at: str