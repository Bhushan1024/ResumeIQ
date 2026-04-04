from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date

class Experience(BaseModel):
    company: str
    role: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    duration_years: Optional[float] = None
    responsibilities: List[str] = Field(default_factory=list)

class Education(BaseModel):
    institution: str
    degree: str
    field_of_study: Optional[str] = None
    graduation_year: Optional[int] = None

class ResumeData(BaseModel):
    model_config = {"extra": "forbid"}
    full_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin: Optional[str] = None
    summary: Optional[str] = None
    
    skills: List[str] = Field(default_factory=list)
    experience: List[Experience] = Field(default_factory=list)
    education: List[Education] = Field(default_factory=list)
    projects: List[str] = Field(default_factory=list)
    
    total_experience_years: Optional[float] = None
    experience_level: str = "Junior"  # Junior / Mid-level / Senior