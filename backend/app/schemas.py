from typing import Optional, List
from pydantic import BaseModel
import datetime as dt


class ComplaintBase(BaseModel):
    complaint_source: Optional[str] = None
    customer_name: Optional[str] = None

    product_name: Optional[str] = None
    product_strength: Optional[str] = None
    batch_number: Optional[str] = None
    manufacturing_date: Optional[str] = None
    expiry_date: Optional[str] = None
    quantity_affected: Optional[str] = None

    complaint_type: Optional[str] = None
    complaint_date: Optional[str] = None
    complaint_description: Optional[str] = None

    initial_severity: Optional[str] = None
    priority: Optional[str] = None


class ComplaintCreate(ComplaintBase):
    pass


class ComplaintUpdate(ComplaintBase):
    status: Optional[str] = None


class ComplaintOut(ComplaintBase):
    id: str
    status: str
    completeness_score: Optional[int] = None
    completeness_missing_fields: Optional[str] = None
    risk_classification: Optional[str] = None
    risk_rationale: Optional[str] = None
    ai_summary: Optional[str] = None
    root_cause_suggestion: Optional[str] = None
    capa_recommendation: Optional[str] = None
    duplicate_of_id: Optional[str] = None
    duplicate_score: Optional[float] = None
    source_document_name: Optional[str] = None
    created_at: dt.datetime
    updated_at: dt.datetime

    class Config:
        from_attributes = True


class ChatMessageOut(BaseModel):
    id: str
    role: str
    content: str
    created_at: dt.datetime

    class Config:
        from_attributes = True


class ExtractionResponse(BaseModel):
    session_id: str
    extracted_fields: dict
    progress_log: List[str]
    assistant_message: str
    completeness_score: Optional[int] = None
    missing_fields: List[str] = []
    risk_classification: Optional[str] = None
    risk_rationale: Optional[str] = None
    ai_summary: Optional[str] = None
    root_cause_suggestion: Optional[str] = None
    capa_recommendation: Optional[str] = None
    duplicate_warning: Optional[dict] = None


class ChatRequest(BaseModel):
    session_id: str
    message: str
    current_fields: Optional[dict] = None


class ChatResponse(BaseModel):
    session_id: str
    assistant_message: str
    updated_fields: Optional[dict] = None
