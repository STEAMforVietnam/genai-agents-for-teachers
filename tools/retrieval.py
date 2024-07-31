from langchain.tools import Tool, tool
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_milvus.vectorstores import Milvus
from pydantic import BaseModel

class RetrievalConfig(BaseModel):
    embedding_model: str
    milvus_collection: str
    milvus_connection_args: dict

class RetrievalTools:
    def __init__(self, config: RetrievalConfig):
        self.config = config
        self.retriever = self._create_retriever()

    def _create_retriever(self):
        embedding_model = HuggingFaceEmbeddings(model_name=self.config.embedding_model)
        return Milvus(
            embedding_function=embedding_model,
            collection_name=self.config.milvus_collection,
            connection_args=self.config.milvus_connection_args,
        ).as_retriever(search_params={"k": 20})

    @tool("Retrieve lesson content")
    def retrieve_lesson_content(self, query: str) -> str:
        """
        Use this tool to retrieve contents from Textbook based on the given query.
        
        Args:
            query (str): The search query to retrieve relevant lesson content.
        
        Returns:
            str: Retrieved lesson content related to the query.
        """
        results = self.retriever.get_relevant_documents(query)
        print(f"Test {query} at tool: retrieve_lesson_content")
        # Process and format the results as needed
        formatted_results = "\n\n".join([doc.page_content for doc in results])
        return formatted_results

    def get_tools(self) -> list[Tool]:
        """
        Returns a list of all available tools in this class.
        """
        return [
            Tool.from_function(
                func=self.retrieve_lesson_content,
                name="LessonRetrieverTool",
                description="Use this tool to retrieve contents from Textbook"
            )
        ]
