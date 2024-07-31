import os
import json
from enum import Enum, IntEnum
from typing import List
from crewai import Agent, Task, Crew, Process
from crewai_tools import tool
from langchain_openai import ChatOpenAI
# from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_anthropic import ChatAnthropic
from langchain.tools import Tool
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_milvus.vectorstores import Milvus
from langchain.tools.retriever import create_retriever_tool
from pydantic import BaseModel
from .custom_tools import create_exam_html_maker_tool, create_matrix_html_maker_tool


class KnowledgeLevelEnum(Enum):
    nhan_biet = "Nhận biết"
    thong_hieu = "Thông hiểu"
    van_dung = "Vận dụng"
    van_dung_cao = "Vận dụng cao"

    
class MatrixJSON(BaseModel):
    topic: str
    sub_topic: str
    knowledge_level: KnowledgeLevelEnum
    question_type: str
    number_of_questions: int
    total_points: int
        

class ExamJSON(BaseModel):
    #TODO
    pass


class CustomCrew:
    def __init__(self, creator_prompt, checker_prompt=None, html_creator_prompt=None):
        self.file_path: str = "."
        self.tools: List[Tool] = []
        self.llm = ChatOpenAI(
            model = "gpt-4o-mini",
            temperature = 0.5
        )
        self.crew: Crew = self._get_crew()
            
        self.creator_prompt = creator_prompt
        self.checker_prompt = checker_prompt
        self.html_creator_prompt = html_creator_prompt
        
    def _get_tools(self):
        """
        create all tools that will be available for all agents and crews
        """

        ### ADD RETRIEVER TOOL
        embedding_model = HuggingFaceEmbeddings(model_name='bkai-foundation-models/vietnamese-bi-encoder')
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
        # self.tools.append(create_matrix_html_maker_tool)

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

    def run(self):
        result = self.crew.kickoff(
            inputs={'topic': 'Môn vật lý lớp 9',
                    'range': '6 tuần',
                    'sub_topics': 'động học, độ dịch chuyển',
                    "students": "30 em học sinh giỏi, 15 em học sinh khá, và 5 em học sinh trung bình"})
        return result
    
    
class ExamCrew(CustomCrew):
    """
    This is a CustomCrew specific for creating an Exam file from
    Textbooks and other reference materials, such as Exam Matrix that is created
    by MatrixCrew
    """
    
    def __init__(self):
        super().__init__()
        self.project = "TẠO_ĐỀ_BÀI_THI"

    def _get_crew(self):
        """
        Create a crew for building Exam file
        """
        self._get_tools()

        ### Add Test Creator Agent, responsible for all "Tạo" task
        # TODO: change Agent args roal, goal, backstory to take in prompt.txt
        test_creator_role = self.creator_prompt.role
        test_creator_goal = self.creator_prompt.goal
        test_creator_backstory = self.creator_prompt.backstory
        test_creator = Agent(
            role=test_creator_role,
            goal=test_creator_goal,
            backstory=test_creator_backstory,
            allow_delegation=False,
            llm=self.llm,
            verbose=True,
            tools=self.tools
        )
        
        # TODO: change Task args description and expected_output to take in prompt.txt
        test_creator_task_description = self.creator_prompt.task_description
        test_creator_task_expected_output = self.creator_prompt.task_expected_output
        test_creator_task = Task(
            description=(test_creator_task_description),
            expected_output=test_creator_task_expected_output,
            agent=test_creator,
        )

        ### Add Test Checker Agent, responsible for all "Kiểm Tra Task"
        test_checker_role = self.checker_prompt.role
        test_checker_goal = self.checker_prompt.goal
        test_checker_backstory = self.checker_prompt.backstory
        
        test_checker = Agent(
            role=test_checker_role,
            goal=test_checker_goal,
            backstory=test_checker_backstory,
            allow_delegation=False,
            llm=self.llm,
            verbose=True,
            # tools=self.tools,
            max_iter=2
        )

        test_checker_task_description = self.checker_prompt.task_description
        test_checker_task_expected_output = self.checker_prompt.task_expected_output
        test_checker_task = Task(
            description=(test_checker_task_description),
            expected_output=(test_checker_task_expected_output),
            agent=test_checker,
            # output_json=MatrixJSON,
            # output_file="matrix.json",
            context=[test_creator_task],
        )

        ### ADD HTML Creator Agent (Thiết kế WEB)
        test_html_creator_role = self.html_creator_prompt.role
        test_html_creator_goal = self.html_creator_prompt.goal
        test_html_creator_backstory = self.html_creator_prompt.backstory
        html_creator = Agent(
            role=test_html_creator_role,
            goal=test_html_creator_goal,
            backstory=test_html_creator_backstory,
            allow_delegation=False,
            llm=self.llm, 
            verbose=True, 
            tools=[create_exam_html_maker_tool],
            max_iter=1
        )
        
        test_html_creator_task_description = self.html_creator_prompt.task_description
        test_html_creator_task_expected_output = self.html_creator_prompt.task_expected_output
        html_task = Task(
            description=(test_html_creator_task_description),
            # TODO: somehow the tool output is not passed back to Agent Output
            # SO expected_output is never met and the agent + the task fall into infinite loop
            expected_output=(test_html_creator_task_expected_output),
            # output_file="matrix.html"
            agent=html_creator,
            context=[test_creator_task, test_checker_task],
            
        )
        
        ### Finally, compose Crew
        return Crew(
                agents=[test_creator, test_checker, test_creator],
                tasks=[test_creator_task, test_checker_task, html_task],
                # manager_agent=orchestrator,
                memory=True,
                # process=Process.hierarchical,
                verbose=1
            )

    
class MatrixCrew(CustomCrew):
    """
    This is a CustomCrew specific for creating an Matrix file from
    Textbooks and other reference materials, such as Ministry of Education's instruction
    """
    def __init__(self):
        super().__init__()

    def _get_crew(self):
        """
        Create a crew for building Exam file
        """
        self._get_tools()

        ### Add Orchestrator (Người Giám Sát)
        orchestrator = Agent(
            role="Giám Sát",
            goal=("Bạn sẽ giao việc tạo $Ma_Trận_Đề_Bài cho matrix_creator và việc kiểm tra chất lượng của $Ma_Trận_Đề_Bài cho matrix_checker"),
            backstory="",
            allow_delegation=False,
            llm=self.llm,
            verbose=True,
            max_iter=5
        )

        orchestrator_task = Task(
            description=(
                "Đầu tiên, Bạn sẽ giao việc tạo $Ma_Trận_Đề_Bài cho matrix_creator và nhận lại kết quả từ matrix_creator."
                "Tiếp theo, hãy giao $Ma_Trận_Đề_Bài này cho matrix_checker và yêu cầu đánh giá. Cuối cùng, bạn sẽ nhận lại một đánh giá về từ matrix_checker."
                "Sau đó, dựa trên kết quả nhận tại từ matrix_checker, bạn sẽ chọn một trong hai quyết định:"
                "1. Yêu cầu matrix_creator sửa lại $Ma_Trận_Đề_Bài theo gợi ý từ matrix_checker"
                "2. Nhận định công việc đã hoàn thành trả lại kết quả $Ma_Trận_Đề_Bài"
            ),
            expected_output="Ma_Trận_Đề_Bài trả về từ matrix_creator",
            agent=orchestrator,
        )

        ### Add Matrix Creator Agent (Ngừoi Kiến Tạo), responsible for all "Tạo" task
        # TODO: change Agent args roal, goal, backstory to take in prompt.txt
        matrix_creator_role = self.creator_prompt.role
        matrix_creator_goal = self.creator_prompt.goal
        matrix_creator_backstory = self.creator_prompt.backstory
        
        matrix_creator = Agent(
            role=matrix_creator_role,
            goal=(matrix_creator_goal
            ), # TODO: COPY HƯỚNG DẪN
            backstory=matrix_creator_backstory,
            allow_delegation=False,
            llm=self.llm,
            verbose=True,
            tools=self.tools,
            max_iter=1
        )
        
        # TODO: change Task args description and expected_output to take in prompt.txt
        matrix_creator_task_description = self.creator_prompt.task_description
        matrix_creator_task_expected_output = self.creator_prompt.task_expected_output
        
        matrix_creator_task = Task(
            description=(matrix_creator_task_description),
            expected_output=matrix_creator_task_expected_output,
            agent=matrix_creator,
            output_json=MatrixJSON
            # context=[orchestrator_task]
        )

        ### Add Matrix Checker Agent (Nguời Kiểm Định), responsible for all "Kiểm Tra Task"
        matrix_checker_role = self.checker_prompt.role
        matrix_checker_goal = self.checker_prompt.goal
        matrix_checker_backstory = self.checker_prompt.backstory
        
        matrix_checker = Agent(
            role=matrix_checker_role,
            goal=matrix_checker_goal,
            backstory=matrix_checker_backstory,
            allow_delegation=False,
            llm=self.llm,
            verbose=True,
            # tools=self.tools,
            max_iter=2
        )

        matrix_checker_task_description = self.checker_prompt.task_description
        matrix_checker_task_expected_output = self.checker_prompt.task_expected_output
        matrix_checker_task = Task(
            description=(matrix_checker_task_description),
            expected_output=(matrix_checker_task_expected_output),
            agent=matrix_checker,
            # output_json=MatrixJSON,
            # output_file="matrix.json",
            context=[matrix_creator_task],
        )

        ### ADD HTML Creator Agent (Thiết kế WEB)
        matrix_html_creator_role = self.html_creator_prompt.role
        matrix_html_creator_goal = self.html_creator_prompt.goal
        matrix_html_creator_backstory = self.html_creator_prompt.backstory
        html_creator = Agent(
            role=matrix_html_creator_role,
            goal=matrix_html_creator_goal,
            backstory=matrix_html_creator_backstory,
            allow_delegation=False,
            llm=self.llm, 
            verbose=True, 
            tools=[create_matrix_html_maker_tool],
            max_iter=1
        )
        
        matrix_html_creator_task_description = self.html_creator_prompt.task_description
        matrix_html_creator_task_expected_output = self.html_creator_prompt.task_expected_output
        html_task = Task(
            description=(matrix_html_creator_task_description),
            # TODO: somehow the tool output is not passed back to Agent Output
            # SO expected_output is never met and the agent + the task fall into infinite loop
            expected_output=(matrix_html_creator_task_expected_output),
            # output_file="matrix.html"
            agent=html_creator,
            context=[matrix_creator_task, matrix_checker_task],
            
        )

        ### Finally, compose Crew
        return Crew(
                agents=[matrix_creator, matrix_checker, html_creator],
                tasks=[matrix_creator_task, matrix_checker_task, html_task],
                # manager_agent=orchestrator,
                memory=True,
                # process=Process.hierarchical,
                verbose=1
            )