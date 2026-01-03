"""
LTFI-WSAP Data Models
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field


class DisclosureLevel(str, Enum):
    """Information disclosure levels"""
    BASIC = "basic"
    STANDARD = "standard"
    DETAILED = "detailed"
    COMPLETE = "complete"


class VerificationStatus(str, Enum):
    """Verification status"""
    PENDING = "pending"
    VERIFIED = "verified"
    FAILED = "failed"
    EXPIRED = "expired"


class EntityType(str, Enum):
    """Entity types"""
    # Commercial entities
    COMPANY = "company"
    SOLE_PROP = "sole_prop"
    PARTNERSHIP = "partnership"
    FRANCHISE = "franchise"
    SUBSIDIARY = "subsidiary"
    
    # Non-commercial entities
    NONPROFIT = "nonprofit"
    GOVERNMENT = "government"
    EDUCATION = "education"
    HEALTHCARE = "healthcare"
    RELIGIOUS = "religious"
    ASSOCIATION = "association"
    COMMUNITY = "community"
    
    # Digital/Individual entities
    PERSONAL = "personal"
    CREATOR = "creator"
    OPENSOURCE = "opensource"
    ONLINE_COMMUNITY = "online_community"
    SAAS = "saas"
    DAO = "dao"
    AI_AGENT = "ai_agent"
    
    # Special entities
    PORTFOLIO = "portfolio"
    MARKETPLACE = "marketplace"
    PLATFORM = "platform"
    EVENT = "event"
    CAMPAIGN = "campaign"
    PROJECT = "project"
    OTHER = "other"


class Entity(BaseModel):
    """Entity model"""
    id: int
    entity_id: str  # UUID field
    entity_type: str
    legal_name: Optional[str] = None
    display_name: str
    slug: str  # 16-char unique identifier
    parent_entity: Optional[int] = None
    created_by: int
    is_active: bool = True
    is_published: bool = False
    is_verified: bool = False
    template_id: Optional[str] = None
    inherits_from_parent: bool = False
    wsap_data: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime


class Domain(BaseModel):
    """Domain model"""
    domain: str
    is_verified: bool = False
    is_primary: bool = False
    verified_at: Optional[datetime] = None


class Verification(BaseModel):
    """DNS Verification details"""
    id: Optional[str] = None  # UUID
    entity: Optional[int] = None
    domain: str
    verification_token: str
    txt_record_name: str  # _wsap-verify
    txt_record_value: str  # wsap-verify=token
    verification_method: str = "dns"  # dns, html_meta, file, any
    status: VerificationStatus = VerificationStatus.PENDING
    verified_at: Optional[datetime] = None
    attempts: int = 0
    max_attempts: int = 3


class WSAPData(BaseModel):
    """WSAP data structure"""
    version: str = "2.0"
    entity: Entity
    domains: List[Domain]
    verification: Verification
    disclosure_level: DisclosureLevel
    generated_at: datetime
    
    # Optional protocol sections
    basic_info: Optional[Dict[str, Any]] = None
    contact_info: Optional[Dict[str, Any]] = None
    legal_info: Optional[Dict[str, Any]] = None
    business_info: Optional[Dict[str, Any]] = None


class CreateEntityRequest(BaseModel):
    """Create entity request"""
    entity_type: str
    legal_name: Optional[str] = None
    display_name: str
    domains: List[str] = Field(default_factory=list)
    description: Optional[str] = None


class UpdateEntityRequest(BaseModel):
    """Update entity request"""
    legal_name: Optional[str] = None
    display_name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    is_published: Optional[bool] = None