from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ChatRequest(BaseModel):
    message: str
    sessionId: str


class ChatResponse(BaseModel):
    sessionId: str
    reply: str


class LeadCreateRequest(BaseModel):
    customer_name: str
    email: str
    phone: str | None = None
    company: str
    industry: str
    lead_source: str = "Chatbot"
    budget: int = Field(default=0, ge=0)
    interest_level: str = "Medium"
    status: str = "New"
    city: str | None = None

class LeadQualificationRequest(BaseModel):
    budget: int = Field(ge=0)
    interest_level: int = Field(ge=1, le=5)
    company_size: int = Field(ge=1)
    purchase_timeline: int = Field(ge=1)


class AppointmentRequest(BaseModel):
    customer_name: str
    scheduled_for: str
    type: str = "demo"
    reminder_enabled: bool = True


class CampaignCreateRequest(BaseModel):
    campaign_name: str
    campaign_type: str
    target_industry: str
    budget: int = Field(ge=0)
    clicks: int = Field(default=0, ge=0)
    impressions: int = Field(default=0, ge=0)
    conversions: int = Field(default=0, ge=0)
    conversion_rate: float = Field(default=0.0, ge=0.0)
    status: str = "Active"
    launch_date: str | None = None


class SupportTicketCreateRequest(BaseModel):
    customer_name: str
    email: str
    query_type: str
    issue_summary: str
    product: str
    priority: str = "Medium"
    status: str = "Open"
    assigned_department: str = "Support"
    response_time_hours: int = Field(default=0, ge=0)
    satisfaction_score: int = Field(default=3, ge=1, le=5)


class SeedRequest(BaseModel):
    leads: int = Field(default=25, ge=0, le=5000)
    campaigns: int = Field(default=10, ge=0, le=5000)
    tickets: int = Field(default=15, ge=0, le=5000)


class CRMOverviewResponse(BaseModel):
    module: str
    sections: list[str]
    independence: str


class GenericDictResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    data: dict[str, Any]

class LeadPredictionRequest(BaseModel):
    lead_source: str
    budget: float = Field(ge=0)
    interest_level : str
    industry: str

class LeadPredictionResponse(BaseModel):
    predicted_status:str
    confidence:float
    probabilities:dict[str,float]

    
class TicketPredictionRequest(BaseModel):
    query_type: str
    issue_summary: str
    product: str
    assigned_department: str

class TicketPredictionResponse(BaseModel):
    predicted_priority: str
    priority_confidence: float
    priority_probabilities: dict[str,float]
    predicted_response_time_hours: float

class CampaignPredictionRequest(BaseModel):
    campaign_type: str
    target_industry: str
    budget: float = Field(ge=0)
    clicks: float = Field(ge=0)


class CampaignPredictionResponse(BaseModel):
    predicted_conversions: int
    predicted_conversion_rate: float