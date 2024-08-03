
import os
from langchain.tools import tool
from tools.vector_store import VectorStore

class ExamTool:
    @tool("Get Chapter Tool")
    def get_chapter(query: str, subject: str="vat_ly") -> str:
        """Search Milvus for relevant Chapter information based on a query."""
        uri = os.getenv("DATABSE_PUBLIC_ENDPOINT")
        token = os.getenv("DATABASE_API_KEY")
        vector_store = VectorStore(uri, token)
        clean_subject = subject.replace(" ","_").lower()
        expression = f"filename like '%{clean_subject}%'"
        search_results = vector_store.search(query, expr=expression)
        
        return search_results
    
    @tool("Get Appendix Tool")
    def get_appendix(query: str, subject: str="vat_ly") -> str:
        """Search Milvus for relevant Appendix information based on a query."""
        uri = os.getenv("DATABSE_PUBLIC_ENDPOINT")
        token = os.getenv("DATABASE_API_KEY")
        vector_store = VectorStore(uri, token)
        clean_subject = subject.replace(" ","_").lower()
        expression = f"filename like '%{clean_subject}%' && filename like 'muc_luc%'"
        search_results = vector_store.search(query, expr=expression)
        return search_results