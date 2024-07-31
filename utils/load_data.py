import os
from llama_index.core import (
   SimpleDirectoryReader,
   VectorStoreIndex,
   StorageContext
)
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.vector_stores.milvus import MilvusVectorStore

uri = os.getenv("DATABSE_PUBLIC_ENDPOINT")
token = os.getenv("DATABASE_API_KEY")

geology_docs = SimpleDirectoryReader(
   input_files=["./data/sgk_dialy_10.pdf"]
).load_data()
vector_store = MilvusVectorStore(uri=uri, token=token,
    dim=1536, collection_name="geology_10", overwrite=True)

storage_context_geology = StorageContext.from_defaults(vector_store=vector_store)

geology_index = VectorStoreIndex.from_documents(geology_docs, storage_context=storage_context_geology)

# persist index
geology_index.storage_context.persist(persist_dir="./storage/geology")

geology_engine = geology_index.as_query_engine(similarity_top_k=3)