from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime

class BloodTestBase(BaseModel):
    test_date: date = Field(default_factory=date.today)
    hemoglobin: Optional[float] = Field(None, ge=0, description="Hemoglobin in g/dL")
    vitamin_d: Optional[float] = Field(None, ge=0, description="Vitamin D in ng/mL")
    vitamin_b12: Optional[float] = Field(None, ge=0, description="Vitamin B12 in pg/mL")
    iron: Optional[float] = Field(None, ge=0, description="Iron in mcg/dL")
    calcium: Optional[float] = Field(None, ge=0, description="Calcium in mg/dL")
    report_file_reference: Optional[str] = Field(None, description="Future storage object reference")

class BloodTestCreate(BloodTestBase):
    pass

class BloodTestUpdate(BaseModel):
    test_date: Optional[date] = None
    hemoglobin: Optional[float] = None
    vitamin_d: Optional[float] = None
    vitamin_b12: Optional[float] = None
    iron: Optional[float] = None
    calcium: Optional[float] = None
    report_file_reference: Optional[str] = None

class BloodTestResponse(BloodTestBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
