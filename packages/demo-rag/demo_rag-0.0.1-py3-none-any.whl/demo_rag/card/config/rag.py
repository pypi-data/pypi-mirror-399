from .storage import StorageConfig
from pydantic import BaseModel, Field
from typing import Optional

class LLMModelConfig(BaseModel):
    """
    for openai
    """
    model_name: str = Field(description="LLM model name")
    api_base: str = Field(description="API base URL for the LLM model")
    api_key: str = Field(description="API key for the LLM model")
    other_parameters: Optional[dict] = Field(default_factory=dict, description="Other parameters for the LLM model")


class RAGConfig(BaseModel):
    
    embedding_model: LLMModelConfig = Field(description="Embedding Model Configuration")
    generation_model: LLMModelConfig = Field(description="Generation Model Configuration")
    storage: StorageConfig = Field(description="Storage Configuration", default_factory=StorageConfig)