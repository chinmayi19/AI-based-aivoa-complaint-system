import json
import uuid

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.services.document_parser import extract_text
from app.agents.langgraph_agent import run_intake_pipeline, run_chat_turn
from app.agents.tools import find_possible_duplicate

router = APIRouter(prefix="/api/ai", tags=["ai"])

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB, matches the UI's "Max File Size: 10MB"
SUPPORTED_EXTENSIONS = (".pdf", ".docx", ".txt", ".eml")


@router.post("/extract", response_model=schemas.ExtractionResponse)
async def extract_complaint(
    db: Session = Depends(get_db),
    file: UploadFile | None = File(None),
    text: str | None = Form(None),
    session_id: str | None = Form(None),
):
    if not file and not text:
        raise HTTPException(status_code=400, detail="Provide either a file or pasted text.")

    source_name = "Pasted text"
    if file:
        if not file.filename.lower().endswith(SUPPORTED_EXTENSIONS):
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported format. Supported: PDF, DOCX, TXT, EML",
            )
        raw_bytes = await file.read()
        if len(raw_bytes) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="File exceeds 10MB limit.")
        raw_text = extract_text(file.filename, raw_bytes)
        source_name = file.filename
    else:
        raw_text = text

    if not raw_text or not raw_text.strip():
        raise HTTPException(status_code=400, detail="Could not read any text from the input.")

    session_id = session_id or str(uuid.uuid4())

    result = run_intake_pipeline(raw_text)
    fields = result.get("fields", {})

    duplicate = find_possible_duplicate(db, fields)

    # persist the chat trail for this session (not tied to a saved complaint yet)
    db.add(models.ChatMessage(session_id=session_id, role="user", content=f"[Uploaded document: {source_name}]"))
    assistant_msg = (
        f"I've extracted the complaint details from \"{source_name}\". "
        f"Completeness: {result.get('completeness_score', 0)}%. "
        f"Risk classification: {result.get('risk_classification', 'N/A')}. "
        "Please review the populated form and correct anything that looks off."
    )
    if duplicate:
        assistant_msg += f" ⚠️ Possible duplicate detected: {duplicate['duplicate_summary']}"

    db.add(models.ChatMessage(session_id=session_id, role="assistant", content=assistant_msg))
    db.commit()

    return schemas.ExtractionResponse(
        session_id=session_id,
        extracted_fields=fields,
        progress_log=result.get("progress_log", []),
        assistant_message=assistant_msg,
        completeness_score=result.get("completeness_score"),
        missing_fields=result.get("missing_fields", []),
        risk_classification=result.get("risk_classification"),
        risk_rationale=result.get("risk_rationale"),
        ai_summary=result.get("ai_summary"),
        root_cause_suggestion=result.get("root_cause_suggestion"),
        capa_recommendation=result.get("capa_recommendation"),
        duplicate_warning=duplicate,
    )



@router.post("/chat", response_model=schemas.ChatResponse)
def chat(payload: schemas.ChatRequest, db: Session = Depends(get_db)):
    db.add(models.ChatMessage(session_id=payload.session_id, role="user", content=payload.message))
    db.commit()

    result = run_chat_turn(payload.message, payload.current_fields)

    db.add(models.ChatMessage(session_id=payload.session_id, role="assistant", content=result["reply"]))
    db.commit()

    return schemas.ChatResponse(
        session_id=payload.session_id,
        assistant_message=result["reply"],
        updated_fields=result.get("field_updates") or None,
    )


@router.post("/save-with-ai/{complaint_id}", response_model=schemas.ComplaintOut)
def attach_ai_results(complaint_id: str, payload: schemas.ExtractionResponse, db: Session = Depends(get_db)):
    """Attach the last AI extraction/analysis results onto a saved complaint record."""
    complaint = db.get(models.Complaint, complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    complaint.completeness_score = payload.completeness_score
    complaint.completeness_missing_fields = json.dumps(payload.missing_fields or [])
    complaint.risk_classification = payload.risk_classification
    complaint.risk_rationale = payload.risk_rationale
    complaint.ai_summary = payload.ai_summary
    complaint.root_cause_suggestion = payload.root_cause_suggestion
    complaint.capa_recommendation = payload.capa_recommendation
    if payload.duplicate_warning:
        complaint.duplicate_of_id = payload.duplicate_warning.get("duplicate_of_id")
        complaint.duplicate_score = payload.duplicate_warning.get("duplicate_score")
    complaint.extraction_raw = json.dumps(payload.extracted_fields or {})

    db.commit()
    db.refresh(complaint)
    return complaint
