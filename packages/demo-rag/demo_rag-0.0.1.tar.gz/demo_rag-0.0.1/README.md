# Readme

This is a demo project for Retrieval-Augmented Generation (RAG) service based on LlamaIndex and FastAPI.
It includes an example of how to set up and use the RAG service with a MinIO storage backend, MongoDB for metadata storage, and Qdrant for vector storage.

## Prerequisites
- Docker and Docker Compose installed on your machine.
- Python 3.13 or higher installed.
- Required Python packages listed in `pyproject.toml`.

## Setup
1. Clone the repository to your local machine.
2. Install the required Python packages using Pip:
   ```bash
   pip install .
   ```
   or if you are using uv:

   ```bash
    uv sync
   ```
3. Start the MinIO, MongoDB and Qdrant service using Docker Compose:
   ```bash
   cd example
   docker compose up
   ```

## Usage
1. Modify the configuration in `example/config.yaml` as needed, especially the LLM settings.

   Note: **we use the OpenAI-compatible models.**
   
   Here is an example configuration for the embedding and generation models:

   ```yaml
    rag:
        embedding_model:
            model_name: text-embedding-v4
            api_base: https://dashscope.aliyuncs.com/compatible-mode/v1
            api_key: <YOUR_API_KEY>


        generation_model:
            model_name: qwen3-next-80b-a3b-instruct
            api_base: https://dashscope.aliyuncs.com/compatible-mode/v1
            api_key: <YOUR_API_KEY>
            other_parameters:
                is_chat_model: true
   ```

2. Start the RAG service by running the `example/main.py` script:
   ```bash
   cd example
   python main.py
   ```

## Test

- The `test.py` file contains simple tests for the RAG service functionalities. You can run it:
   ```bash
    python test.py
    ```

- The `test_rag_service.py` file contains unit tests for the RAG service. You can run it using pytest:
   ```bash
    python test_rag_service.py
    ```