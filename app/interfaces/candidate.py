from typing import List
from pydantic import BaseModel

class Candidate(BaseModel):
    id: str
    name: str
    classified_job_ids: dict