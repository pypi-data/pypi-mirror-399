from ..card.config import RAGConfig, LLMModelConfig

from llama_index.llms.openai_like import OpenAILike
from llama_index.embeddings.openai_like import OpenAILikeEmbedding
from llama_index.core import Settings
from llama_index.core.node_parser import SentenceSplitter

class RAGSetting:
    def __init__(self, config: RAGConfig):
        self.config = config


    def set_default_models(self):
        if self.config.embedding_model is not None:
            config: LLMModelConfig = self.config.embedding_model
            Settings.embed_model = OpenAILikeEmbedding(
                model_name=config.model_name,
                api_base=config.api_base,
                api_key=config.api_key,
                **config.other_parameters
            )

        if self.config.generation_model is not None:
            # MOST LIKELY NEED TO SETUP: is_chat_model=True
            config: LLMModelConfig = self.config.generation_model
            Settings.llm = OpenAILike(
                model_name=config.model_name,
                api_base=config.api_base,
                api_key=config.api_key,
                **config.other_parameters
            )


    def set_default_transformations(self):
        Settings.transformations = [
            SentenceSplitter(),
            Settings.embed_model
        ]

    def adjust_default_settings(self):
        self.set_default_models()
        self.set_default_transformations()