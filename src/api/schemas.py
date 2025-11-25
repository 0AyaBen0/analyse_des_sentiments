from pydantic import BaseModel
from typing import List

class BatchRequest(BaseModel):
    comments: List[str]
