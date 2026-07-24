"""
Small deterministic helper tools used by the LangGraph agent that don't need an
LLM call. Kept separate from the graph so they're easy to unit test.
"""
from difflib import SequenceMatcher
from sqlalchemy.orm import Session

from app.models import Complaint


def find_possible_duplicate(db: Session, fields: dict, exclude_id: str | None = None) -> dict | None:
    """Very lightweight duplicate detector for the demo: flags an existing complaint
    as a likely duplicate when it shares the same product + batch number and has a
    highly similar description. A production system would use embeddings + a vector
    store instead of SequenceMatcher, but this keeps the demo dependency-free."""
    product = (fields.get("product_name") or "").strip().lower()
    batch = (fields.get("batch_number") or "").strip().lower()
    description = (fields.get("complaint_description") or "").strip().lower()

    if not product or not batch:
        return None

    query = db.query(Complaint).filter(
        Complaint.product_name.isnot(None),
        Complaint.batch_number.isnot(None),
    )
    if exclude_id:
        query = query.filter(Complaint.id != exclude_id)

    best_match = None
    best_score = 0.0

    for existing in query.all():
        if (existing.product_name or "").strip().lower() != product:
            continue
        if (existing.batch_number or "").strip().lower() != batch:
            continue
        existing_desc = (existing.complaint_description or "").strip().lower()
        score = SequenceMatcher(None, description, existing_desc).ratio() if description and existing_desc else 0.5
        if score > best_score:
            best_score = score
            best_match = existing

    if best_match and best_score >= 0.35:
        return {
            "duplicate_of_id": best_match.id,
            "duplicate_score": round(best_score, 2),
            "duplicate_summary": f"Similar to existing complaint for {best_match.product_name} "
                                  f"(batch {best_match.batch_number}) logged on "
                                  f"{best_match.created_at.strftime('%Y-%m-%d') if best_match.created_at else 'unknown date'}.",
        }
    return None
