from pydantic import BaseModel


class LinkedinJob(BaseModel):
    id: str
    title: str
    company: str
    location: str
    description: str
