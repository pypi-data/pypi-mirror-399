from llama_index.storage.docstore.mongodb import MongoDocumentStore
from llama_index.core.storage.docstore.types import RefDocInfo
from typing import Optional, Dict
from dataclasses import asdict

class MongoDocumentStoreExtend(MongoDocumentStore):


    def get_all_doc(self, file_path: Optional[str] = None)  -> Optional[Dict[str, RefDocInfo]]:
        all_docs = self.get_all_ref_doc_info()
        if file_path is None:
            return all_docs

        target_docs = {}
        for doc_id, doc in all_docs.items():
            if doc.metadata.get("file_path", None) == file_path:
                target_docs[doc_id] = doc

        return target_docs
    
    
    def set_document_status(self, doc_id: str, status: str) -> None:
        ref_doc_info = self.get_ref_doc_info(doc_id)
        if ref_doc_info is None:
            raise ValueError(f"Document with id {doc_id} not found.")
        
        ref_doc_info.metadata["status"] = status
        
        self._kvstore.put(
            key=doc_id,
            val=asdict(ref_doc_info),
            collection=self._ref_doc_collection
        )

        pass


    def set_status(self, doc_ids: list[str], status: str) -> None:
        for doc_id in doc_ids:
            self.set_document_status( doc_id, status)
