from pydantic import BaseModel
from typing import List

class JsonChoice(BaseModel):
    text: str

class JsonResponse(BaseModel):
    choices: List[JsonChoice]
