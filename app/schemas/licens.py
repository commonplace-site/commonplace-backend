from pydantic import BaseModel


class LicenseCreate(BaseModel):
    business_name: str
    established_date: str  # YYYY-MM-DD
    renewal_due_date: str  # YYYY-MM-DD


class RenewLicense(BaseModel):
    license_id: int
    new_renewal_date: str   