from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, List
import datetime

class DrivingLicense(BaseModel):
    """Schema for extracting data from a Driving License."""
    name: str = Field(..., description="Full name as shown on the license")
    date_of_birth: Optional[str] = Field(None, description="Date of birth of the license holder in MM/DD/YYYY format. If not visible, set to null.")
    license_number: str = Field(..., description="The driver's license or ID card number.")
    issuing_state: str = Field(..., description="The state or jurisdiction that issued the license.")
    expiry_date: Optional[str] = Field(None, description="The date the license expires in MM/DD/YYYY format. If not visible, set to null.")

    @field_validator("date_of_birth", "expiry_date", mode="before")
    @classmethod
    def validate_date(cls, v):
        if v is None or v == "None":
            return None
        try:
            datetime.datetime.strptime(v, "%m/%d/%Y")
        except (ValueError, TypeError):
            raise ValueError(f"Date '{v}' must be in MM/DD/YYYY format")
        return v
    
    @model_validator(mode='after')
    def validate_dates(self) -> 'DrivingLicense':
        if self.date_of_birth and self.expiry_date:
            dob = datetime.datetime.strptime(self.date_of_birth, "%m/%d/%Y")
            exp = datetime.datetime.strptime(self.expiry_date, "%m/%d/%Y")
            if dob >= exp:
                raise ValueError("Date of birth must be before the expiry date.")
        return self

class LineItem(BaseModel):
    """Schema for a single item on a shop receipt."""
    ItemName: str = Field(..., description="The name of the purchased item.")
    Quantity: Optional[float] = Field(1.0, description="The quantity of the item purchased.")
    Price: Optional[float] = Field(None, description="The price of the single item.")

class ShopReceipt(BaseModel):
    """Schema for extracting data from a Shop Receipt."""
    MerchantName: Optional[str] = Field(None, description="The name of the store or merchant.")
    TotalAmount: Optional[float] = Field(None, description="The final total amount of the purchase.")
    DateOfPurchase: Optional[str] = Field(None, description="The date of the transaction, ideally in YYYY-MM-DD format.")
    PaymentMethod: Optional[str] = Field(None, description="How payment was made (e.g., Credit Card, Cash).")
    LineItems: Optional[List[LineItem]] = Field(None, description="A list of all items purchased.")

    @field_validator("DateOfPurchase", mode="before")
    @classmethod
    def validate_date(cls, v):
        if v is None or v == "None":
            return None
        try:
            datetime.datetime.strptime(v, "%m/%d/%Y")
        except (ValueError, TypeError):
            raise ValueError(f"Date '{v}' must be in MM/DD/YYYY format")
        return v
    
class WorkExperience(BaseModel):
    """Schema for a single work experience on a resume."""
    company: str = Field(..., description="The name of the company.")
    role: str = Field(..., description="The role of the candidate in the company.")
    dates: Optional[str] = Field(None, description="The dates of the work experience in MM/DD/YYYY format.")

class Education(BaseModel):
    """Schema for a single education on a resume."""
    institution: str = Field(..., description="The name of the institution.")
    degree: str = Field(..., description="The degree of the candidate.")
    graduation_year: Optional[str] = Field(None, description="The graduation year of the candidate in YYYY format.")

class Resume(BaseModel):
    """Schema for extracting data from a Resume."""
    full_name: Optional[str] = Field(None, description="The full name of the candidate.")
    email: Optional[str] = Field(None, description="The email address of the candidate.")
    phone_number: Optional[str] = Field(None, description="The phone number of the candidate.")
    skills: Optional[List[str]] = Field(None, description="The list of skills of the candidate. If not visible, set to empty list [].")
    work_experience: Optional[List[WorkExperience]] = Field(None, description="The list of work experience of the candidate. If not visible, set to empty list [].")
    education: Optional[List[Education]] = Field(None, description="The list of education of the candidate. If not visible, set to empty list [].")