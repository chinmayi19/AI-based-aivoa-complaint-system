import uuid
import datetime as dt

from sqlalchemy import Column, String, Text, DateTime, Float, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


def gen_uuid():
    return str(uuid.uuid4())


class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    status = Column(String(30), default="pending_triage")  # pending_triage, in_review, closed

    # 1. Origin & customer details
    complaint_source = Column(String(120))
    customer_name = Column(String(200))

    # 2. Product & batch identification
    product_name = Column(String(200))
    product_strength = Column(String(120))
    batch_number = Column(String(120))
    manufacturing_date = Column(String(20))
    expiry_date = Column(String(20))
    quantity_affected = Column(String(60))

    # 3. Complaint details
    complaint_type = Column(String(120))
    complaint_date = Column(String(20))
    complaint_description = Column(Text)

    # 4. Initial assessment & priority
    initial_severity = Column(String(30))
    priority = Column(String(30))

    # AI-derived fields (bonus features)
    completeness_score = Column(Integer, nullable=True)
    completeness_missing_fields = Column(Text, nullable=True)  # JSON string list
    risk_classification = Column(String(30), nullable=True)
    risk_rationale = Column(Text, nullable=True)
    ai_summary = Column(Text, nullable=True)
    root_cause_suggestion = Column(Text, nullable=True)
    capa_recommendation = Column(Text, nullable=True)
    duplicate_of_id = Column(String(36), nullable=True)
    duplicate_score = Column(Float, nullable=True)

    source_document_name = Column(String(300), nullable=True)
    extraction_raw = Column(Text, nullable=True)  # JSON string of raw AI extraction

    created_at = Column(DateTime, default=dt.datetime.utcnow)
    updated_at = Column(DateTime, default=dt.datetime.utcnow, onupdate=dt.datetime.utcnow)

    messages = relationship("ChatMessage", back_populates="complaint", cascade="all, delete-orphan")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    complaint_id = Column(String(36), ForeignKey("complaints.id"), nullable=True)
    session_id = Column(String(36), index=True)
    role = Column(String(20))  # user | assistant | system
    content = Column(Text)
    created_at = Column(DateTime, default=dt.datetime.utcnow)

    complaint = relationship("Complaint", back_populates="messages")
