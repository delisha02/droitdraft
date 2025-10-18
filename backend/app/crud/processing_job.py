'''
This file contains CRUD operations for the ProcessingJob model.
'''

from app.crud.base import CRUDBase
from app.models.models import ProcessingJob
from app.schemas.processing_job import ProcessingJobCreate, ProcessingJobUpdate


class CRUDProcessingJob(CRUDBase[ProcessingJob, ProcessingJobCreate, ProcessingJobUpdate]):
    pass


processing_job = CRUDProcessingJob(ProcessingJob)
