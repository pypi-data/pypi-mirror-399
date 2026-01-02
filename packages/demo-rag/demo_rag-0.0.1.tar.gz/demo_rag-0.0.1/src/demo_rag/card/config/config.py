from .rag import RAGConfig
from pydantic import BaseModel, Field
from typing import List, Dict
import yaml


class ServerConfig(BaseModel):
    host: str = Field(description="Server host")
    port: int = Field(description="Server port")


class UserInfo(BaseModel):
    username: str = Field(description="Username")
    role: str = Field(description="User role")


class Config(BaseModel):
    server: ServerConfig = Field(description="Server Configuration")
    rag: RAGConfig = Field(description="RAG Configuration")
    user: Dict[str, UserInfo] = Field(description="User Information")

    @classmethod
    def from_yaml(cls, file_path: str) -> "Config":
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
        return cls(**data)
    
