
import os
from langchain.tools import tool
from tools.vector_store import VectorStore

class ExamTool:
    @tool("Get Chapter Tool")
    def get_chapter(query: str) -> str:
        """Search Milvus for relevant Chapter information based on a query."""
        uri = os.getenv("DATABSE_PUBLIC_ENDPOINT")
        token = os.getenv("DATABASE_API_KEY")
        vector_store = VectorStore(uri, token)
        search_results = vector_store.search(query)
        
        return search_results