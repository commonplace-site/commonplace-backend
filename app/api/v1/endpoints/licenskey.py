from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.dependencies import get_db
from app.models.licenskey import License
from app.schemas.licens import LicenseCreate, RenewLicense

router = APIRouter(tags=['Licens Key'])

@router.post("/license/create")
def create_license(data: LicenseCreate, db: Session = Depends(get_db)):
    db_license = License(
        business_name=data.business_name,
        established_date=data.established_date,
        renewal_due_date=data.renewal_due_date
    )
    db.add(db_license)
    db.commit()
    return {"message": "License created", "next_renewal": data.renewal_due_date}


@router.get("/license/upcoming")
def get_upcoming_renewals(db: Session = Depends(get_db)):
    today = datetime.utcnow().date()
    upcoming = today + timedelta(days=30)
    licenses = db.query(License).filter(License.renewal_due_date <= upcoming).all()
    return licenses

@router.put("/license/renew")
def renew_license(data: RenewLicense, db: Session = Depends(get_db)):
    license = db.query(License).filter(License.id == data.license_id).first()
    if not license:
        return {"error": "License not found"}
    license.renewal_due_date = data.new_renewal_date
    db.commit()
    return {"message": "Renewal updated"}