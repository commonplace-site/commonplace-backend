from uuid import UUID
from fastapi import APIRouter, Depends, Form
from requests import Session
from app.db.dependencies import get_db
from app.models.users import UserConsent

router=APIRouter(tags=["Students"])

@router.post("/student/consent")
def student_consent(
    user_id: UUID = Form(...),
    consent: bool = Form(...),
    db: Session = Depends(get_db)
):
    existing = db.query(UserConsent).filter(UserConsent.user_id == user_id).first()
    if existing:
        existing.consent_given = consent
    else:
        db.add(UserConsent(user_id=user_id, consent_given=consent))
    db.commit()
    return {"message": f"Consent updated to {consent}"}
