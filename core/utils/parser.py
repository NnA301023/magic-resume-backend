from typing import List
from pydantic import BaseModel, Field

class PersonalInfo(BaseModel):
    skill_extracted: List[str] = Field(..., description="Skill is a set of related knowledge that can be learned through experience. A skill is not an action or an activity. A skill is a set of knowledge that can be learned through experience.")
    location: str = Field(..., description="Location specific into city name is enough without country.")
    year_of_experience: int = Field(..., description="Year of experience is a numerical value that represents the number of years of experience.")
    job_title_relevan: str = Field(..., description="Job title relevan is a general representation of title based on text provided.")