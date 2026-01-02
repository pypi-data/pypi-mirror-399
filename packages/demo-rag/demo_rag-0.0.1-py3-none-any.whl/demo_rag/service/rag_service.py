from llama_index.storage.index_store.mongodb import MongoIndexStore
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core import StorageContext, SimpleDirectoryReader, VectorStoreIndex
from llama_index.core.schema import NodeWithScore
from qdrant_client import QdrantClient
from s3fs import S3FileSystem
from typing import List

from .rag_setting import RAGSetting
from .document_store_extend import MongoDocumentStoreExtend
from ..card.config import RAGConfig


class RAGService:
    def __init__(self, config: RAGConfig):
        self.config = config
        RAGSetting(self.config).adjust_default_settings()

        self.sync_fs = None
        self.storage_context = None
        self.index = None
        self.retriever = None
        self.query_engine = None

        self.__initialize_filestore()
        self.__initialize_storage_context()


    def __initialize_filestore(self):

        fs_config = self.config.storage.file_store
        self.sync_fs = S3FileSystem(
            key=fs_config.access_key,
            secret=fs_config.secret_key,
            client_kwargs={
                "endpoint_url": fs_config.endpoint_url,
                "region_name": fs_config.region,
                "verify": False,
                "use_ssl": False
            },
            config_kwargs={"s3": {"addressing_style": "path"}}
        )


    def __initialize_storage_context(self):

        doc_config = self.config.storage.doc_store
        doc_mongodb_uri = f"mongodb://{doc_config.user}:{doc_config.password}@{doc_config.host}:{doc_config.port}/{doc_config.database}?authSource=admin"
        document_store = MongoDocumentStoreExtend.from_uri(
            uri=doc_mongodb_uri,
            db_name=doc_config.database,
            namespace="docstore",
        )

        index_config = self.config.storage.index_store
        index_mongodb_uri = f"mongodb://{index_config.user}:{index_config.password}@{index_config.host}:{index_config.port}/{index_config.database}?authSource=admin"

        index_store = MongoIndexStore.from_uri(
            uri=index_mongodb_uri,
            db_name=index_config.database,
            namespace="indexstore"
        )

        vector_config = self.config.storage.vector_store
        vector_store = QdrantVectorStore(
            client=QdrantClient(
                host=vector_config.host, 
                port=vector_config.port
            ), 
            collection_name=vector_config.collection_name
        )

        # NOTE: VERY IMPORTANT FOR THE INDEX STUCTURE CONSISTENCY
        vector_store.stores_text = False

        self.storage_context = StorageContext.from_defaults(
            docstore=document_store,
            index_store=index_store,
            vector_store=vector_store
        )


    def __set_file_metadata(self, file_path: str) -> dict:
        metadata = {
            "file_path": file_path,
            "status": "processing",
        }
        return metadata


    def build(self):

        # step 1: load data from filestore
        reader = SimpleDirectoryReader(
            input_dir=self.config.storage.file_store.bucket,
            fs=self.sync_fs,
            recursive=True,
            file_metadata=self.__set_file_metadata
        )

        documents = reader.load_data()

        # step 2: build a new index
        self.index = VectorStoreIndex.from_documents(
            documents,
            storage_context=self.storage_context
        )
        self.retriever = self.index.as_retriever(similarity_top_k=1)
        self.query_engine = self.index.as_query_engine()

        # step 3: set status to active
        self.storage_context.docstore.set_status(
            [doc.doc_id for doc in documents],
            "active"
        )


    def clear(self, index=True):

        """
        clear all data in vector store, document store and index store
        """
        self.storage_context.vector_store.clear()
        
        ref_doc_infos = self.storage_context.docstore.get_all_ref_doc_info()
        for doc_id in ref_doc_infos.keys():
            self.storage_context.docstore.delete_ref_doc(doc_id)

        if index:
            index_structs = self.storage_context.index_store.index_structs()
            for struct in index_structs:
                self.storage_context.index_store.delete_index_struct(struct.index_id)


    def retrieve(self, text: str):

        # step 1: retrieve from index
        result = self.retriever.retrieve(text)

        # step 2: filter the documents with status "active"
        filtered_results = []
        for node_with_score in result:
            ref_doc_id = node_with_score.node.ref_doc_id
            ref_doc_info = self.storage_context.docstore.get_ref_doc_info(ref_doc_id)
            if ref_doc_info and ref_doc_info.metadata.get("status", "") == "active":
                filtered_results.append(node_with_score)

        return filtered_results
    
    def get_simple_result(self, result: List[NodeWithScore]):
        simple_results = []
        for node_with_score in result:
            simple_results.append({
                "content": node_with_score.node.get_content(),
                "score": node_with_score.score
            })
        return simple_results

    def upload_file(self, data, file_path: str):
        with self.sync_fs.open(file_path, 'wb') as f:
            f.write(data)


    def download_file(self, file_path: str):
        with self.sync_fs.open(file_path, 'rb') as f:
            data = f.read()
        return data
    

    def delete_file(self, file_path: str):
        self.sync_fs.rm(file_path)


    def add(self, file_path: str):

        # step 1: load the file
        reader = SimpleDirectoryReader(
            input_files=[file_path],
            fs=self.sync_fs,
            recursive=True,
            file_metadata=self.__set_file_metadata
        )

        documents = reader.load_data()

        # step 2: insert to index and storecontext
        for doc in documents:
            self.index.insert(document=doc)

        # step 3: set status to active
        self.storage_context.docstore.set_status(
            [doc.doc_id for doc in documents],
            "active"
        )

    def delete(self, file_path: str):

        # step 1: get the target docs
        target_docs = self.storage_context.docstore.get_all_doc(file_path=file_path)

        # step 2: set status to deleted
        self.storage_context.docstore.set_status(
            [doc_id for doc_id in target_docs.keys()],
            "deleted"
        )

        # step 3: delete from index
        for doc_id in target_docs.keys():
            self.index.delete_ref_doc(ref_doc_id=doc_id, delete_from_docstore=True)
