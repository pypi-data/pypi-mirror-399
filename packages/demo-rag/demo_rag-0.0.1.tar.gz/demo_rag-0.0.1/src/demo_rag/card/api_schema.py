from pydantic import BaseModel, Field
from typing import Optional


class RetrievalData(BaseModel):
    text: str = Field(description="The retrieved text content")

    