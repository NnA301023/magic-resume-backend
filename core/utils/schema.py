from typing import List
from pydantic import BaseModel

class ResponseSchema(BaseModel):
    message: str = "success"
    result: List = []