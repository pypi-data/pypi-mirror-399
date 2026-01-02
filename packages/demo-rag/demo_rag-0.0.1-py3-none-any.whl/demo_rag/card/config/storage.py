from pydantic import BaseModel, Field
from typing import Optional


class AWSS3Config(BaseModel):
    endpoint_url: str = Field(description="AWS S3 Endpoint URL")
    access_key: str = Field(description="AWS S3 Access Key")
    secret_key: str = Field(description="AWS S3 Secret Key")
    bucket: str = Field(description="AWS S3 Bucket Name")
    region: Optional[str] = Field(default="cn-north-1", description="AWS S3 Region")

class SQLDBConfig(BaseModel):
    prefix: str = Field(default="postgresql+asyncpg", description="Database URL prefix")
    user: str = Field(description="Database user")
    password: str = Field(description="Database password")
    database: str = Field(description="Database name")
    host: str = Field(description="Database host")
    port: int = Field(description="Database port")


class MongoDBConfig(BaseModel):
    user: str = Field(description="MongoDB user")
    password: str = Field(description="MongoDB password")
    host: str = Field(description="MongoDB host")
    port: int = Field(description="MongoDB port")
    database: str = Field(description="MongoDB database name")


class VectorDBConfig(BaseModel):
    host: str = Field(description="Vector DB host")
    port: int = Field(description="Vector DB port")
    collection_name: str = Field(description="Vector DB collection name")


class StorageConfig(BaseModel):
    file_store: Optional[AWSS3Config] = Field(description="File Store Configuration", default=None)
    doc_store: Optional[MongoDBConfig] = Field(description="Document Store Configuration", default=None)
    index_store: Optional[MongoDBConfig] = Field(description="Index Store Configuration", default=None)
    vector_store: Optional[VectorDBConfig] = Field(description="Vector Store Configuration", default=None)
