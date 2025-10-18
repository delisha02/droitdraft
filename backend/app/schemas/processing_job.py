'''
This file contains the Pydantic schemas for the ProcessingJob model.
'''

from pydantic import BaseModel


class ProcessingJobBase(BaseModel):
    document_id: int
    status: str
    result: str | None = None


class ProcessingJobCreate(ProcessingJobBase):
    pass


class ProcessingJobUpdate(ProcessingJobBase):
    pass


class ProcessingJobInDBBase(ProcessingJobBase):
    id: int

    class Config:
        from_attributes = True


class ProcessingJob(ProcessingJobInDBBase):
    pass
