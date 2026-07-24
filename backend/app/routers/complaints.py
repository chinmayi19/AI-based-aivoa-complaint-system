import json
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/api/complaints", tags=["complaints"])


@router.get("", response_model=List[schemas.ComplaintOut])
def list_complaints(status: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(models.Complaint).order_by(desc(models.Complaint.created_at))
    if status:
        query = query.filter(models.Complaint.status == status)
    return query.all()


@router.get("/{complaint_id}", response_model=schemas.ComplaintOut)
def get_complaint(complaint_id: str, db: Session = Depends(get_db)):
    complaint = db.get(models.Complaint, complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return complaint


@router.post("", response_model=schemas.ComplaintOut, status_code=201)
def create_complaint(payload: schemas.ComplaintCreate, db: Session = Depends(get_db)):
    complaint = models.Complaint(**payload.model_dump())
    db.add(complaint)
    db.commit()
    db.refresh(complaint)
    return complaint


@router.put("/{complaint_id}", response_model=schemas.ComplaintOut)
def update_complaint(complaint_id: str, payload: schemas.ComplaintUpdate, db: Session = Depends(get_db)):
    complaint = db.get(models.Complaint, complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(complaint, key, value)
    db.commit()
    db.refresh(complaint)
    return complaint


@router.delete("/{complaint_id}", status_code=204)
def delete_complaint(complaint_id: str, db: Session = Depends(get_db)):
    complaint = db.get(models.Complaint, complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    db.delete(complaint)
    db.commit()
    return None


@router.get("/{complaint_id}/messages", response_model=List[schemas.ChatMessageOut])
def get_messages(complaint_id: str, db: Session = Depends(get_db)):
    return (
        db.query(models.ChatMessage)
        .filter(models.ChatMessage.complaint_id == complaint_id)
        .order_by(models.ChatMessage.created_at)
        .all()
    )
