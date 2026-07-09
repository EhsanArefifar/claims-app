import uuid
from datetime import datetime, date
from pydantic import BaseModel


class ClaimCreate(BaseModel):
  policy_id : uuid.UUID
  description: str | None = None
  incident_date: date
  


class ClaimRead(BaseModel):
  id: uuid.UUID
  policy_id : uuid.UUID
  reference_number: str
  status: str
  description: str | None = None
  incident_date: date
  filed_at: datetime
  updated_at: datetime

  model_config = {"from_attributes": True}