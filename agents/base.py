import os
from typing import List
from crewai import Crew
from langchain_openai import ChatOpenAI
from langchain.tools import Tool
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_milvus.vectorstores import Milvus
from langchain.tools.retriever import create_retriever_tool
from .custom_tools import create_matrix_html_maker_tool

MODEL_NAME='bkai-foundation-models/vietnamese-bi-encoder'

class CustomCrew:
    def __init__(self):
        self.file_path: str = "."
        self.tools: List[Tool] = []
        self.llm = ChatOpenAI(
            model = "gpt-4o-mini",
            temperature = 0.5
        )
        self.crew: Crew = self._get_crew()
        
    def _get_tools(self):
        """
        create all tools that will be available for all agents and crews
        """

        ### ADD RETRIEVER TOOL
        embedding_model = HuggingFaceEmbeddings(model_name=MODEL_NAME)
        retriever = Milvus(
            embedding_function=embedding_model,
            collection_name="s4v_python_oh_bkai",
            connection_args={"uri": os.environ.get("DATABSE_PUBLIC_ENDPOINT"),
                            "token": os.environ.get("DATABASE_API_KEY"),
                            "secure": True
            },
        ).as_retriever(search_params={
                "k":20
            })
        
        retriever_tool = create_retriever_tool(
            retriever=retriever,
            name="LessonRetrieverTool",
            description="Use this tool to retrieve contents from Textbook"
        )
        self.tools.append(retriever_tool)

        ### ADD JSONParserTool


        ### ADD HTMLMakerTool
        # self.tools.append(create_exam_html_maker_tool)
        self.tools.append(create_matrix_html_maker_tool)

        ### ADD PDFSearchTool

    def _get_llm(self):
        """
        Depend on configs `genai` in config.yaml, init an LLM service
        """
        pass

    def _get_crew(self) -> Crew:
        """
        depend on project (Tạo Ma trận or Tạo bài kiểm tra), put
        together a crew
        """
        raise NotImplementedError

    def run(self, inputs: any):
        result = self.crew.kickoff(inputs=inputs)
        return result
    
    