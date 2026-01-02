from ..card import Config, RetrievalData, UserInfo
from ..service import RAGService
from .deps import authenticate, authorize

import uvicorn
from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager


class DEMORAG:
    def __init__(self, config_path: str):
        self.config = Config.from_yaml(config_path)

        self.app = self.__get_app()
        self.rag_service = None

    @asynccontextmanager
    async def lifespan(self, app: FastAPI):

        # Startup actions
        self.rag_service = RAGService(self.config.rag)
        self.rag_service.build()

        app.state.user_db = self.config.user

        yield

        # Shutdown actions
        print("Shutting down DEMORAG application.")

    
    def __get_app(self) -> FastAPI:

        app = FastAPI(title="Demo RAG Service API", lifespan=self.lifespan)


        @app.post("/retrieve")
        def retrieval(
            data: RetrievalData,
            user_info: UserInfo = Depends(authenticate), 
        ):
            """
            Retrieve relevant information based on the input text.
            """

            # step 1: get retrieval result
            result = self.rag_service.retrieve(data.text)

            # step 2: create response
            simple_result = self.rag_service.get_simple_result(result)

            return {"results": simple_result}
        
        @app.delete("/admin/clear")
        def clear(
            authorize: bool = Depends(authorize)
        ):
            """
            Clear all data in vector store, document store and index store.
            """
            self.rag_service.clear()
            return {"detail": "All data cleared successfully."}

        return app


    def run(self):
        uvicorn.run(
            app=self.app,
            host=self.config.server.host,
            port=self.config.server.port
        )