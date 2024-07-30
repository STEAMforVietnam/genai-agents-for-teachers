import os
import json
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
from .custom_tools import create_exam_html_maker_tool, create_matrix_html_maker_tool



class CustomCrew:
    def __init__(self, arg):
        self.file_path: str = "."
        self.tools: List[Tool] = []
        self.llm = ChatOpenAI(
            model = "gpt-4o-mini",
            temperature = 0.5
        )
        self.crew: Crew = self._get_crew()
        self.arg = arg
        
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

        ### ADD ImageReaderTool

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
        ### Get prompt
        parms = self.arg

        topic = parms.topic
        rnge = parms.rnge
        sub_topics = parms.sub_topics
        students = parms.students

        result = self.crew.kickoff(
            inputs={'topic': topic,
                    'range': rnge,
                    'sub_topics': sub_topics,
                    "students": students})
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
        
        ### Get prompt
        parms = self.arg
        
        test_creator_role = parms.test_creator_role
        test_creator_goal = parms.test_creator_goal
        test_creator_backstory = parms.test_creator_backstory

        test_assignment_task_description = parms.test_assignment_task_description
        test_assignment_task_expected_output = parms.test_assignment_task_expected_output

        ### Add Test Creator Agent, responsible for all "Tạo" task
        # TODO: change Agent args roal, goal, backstory to take in prompt.txt
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
        test_assignment_task = Task(
            description=(test_assignment_task_description),
            expected_output=test_assignment_task_expected_output,
            agent=test_creator,
        )

        ### Add Test Checker Agent, responsible for all "Kiểm Tra Task"


        ### Finally, compose Crew
        return Crew(
            agents=[test_creator],
            tasks=[test_assignment_task],
            verbose=2
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
        
        ### Get prompt
        parms = self.arg
        
        orchestrator_role = parms.orchestrator_role
        orchestrator_goal = parms.orchestrator_goal
        orchestrator_backstory = parms.orchestrator_backstory

        orchestrator_task_description = parms.orchestrator_task_description
        orchestrator_task_expected_output = parms.orchestrator_task_expected_output

        matrix_creator_role = parms.matrix_creator_role
        matrix_creator_goal = parms.matrix_creator_goal
        matrix_creator_backstory = parms.matrix_creator_backstory

        matrix_creator_task_description = parms.matrix_creator_task_description
        matrix_creator_task_expected_output = parms.matrix_creator_task_expected_output

        matrix_checker_role = parms.matrix_checker_role
        matrix_checker_goal = parms.matrix_checker_goal
        matrix_checker_backstory = parms.matrix_checker_backstory

        matrix_checker_task_description = parms.matrix_checker_task_description
        matrix_checker_task_expected_output = parms.matrix_checker_task_expected_output

        ### Add Orchestrator (Người Giám Sát)
        orchestrator = Agent(
            role=orchestrator_role,
            goal=(orchestrator_goal),
            backstory=orchestrator_backstory,
            allow_delegation=False,
            llm=self.llm,
            verbose=True,
            max_iter=5
        )

        # html_maker = Agent()
        orchestrator_task = Task(
            description=(orchestrator_task_description),
            expected_output=orchestrator_task_expected_output,
            agent=orchestrator,
            # output_file
        )

        ### Add Matrix Creator Agent (Ngừoi Kiến Tạo), responsible for all "Tạo" task
        # TODO: change Agent args roal, goal, backstory to take in prompt.txt
        matrix_creator = Agent(
            role=matrix_creator_role,
            goal=(matrix_creator_goal), # TODO: COPY HƯỚNG DẪN
            backstory=matrix_creator_backstory,
            allow_delegation=False,
            llm=self.llm,
            verbose=True,
            tools=self.tools,
            max_iter=5
        )
        
        # TODO: change Task args description and expected_output to take in prompt.txt
        matrix_creator_task = Task(
            description=(matrix_creator_task_description),
            expected_output=matrix_creator_task_expected_output,
            agent=[matrix_creator, matrix_checker],
            # context=[orchestrator_task]
        )

        ### Add Matrix Checker Agent (Nguời Kiểm Định), responsible for all "Kiểm Tra Task"
        matrix_checker = Agent(
            role=matrix_checker_role,
            goal=matrix_checker_goal,
            backstory=matrix_checker_backstory,
            allow_delegation=False,
            llm=self.llm,
            verbose=True,
            tools=self.tools,
            max_iter=5
        )

        matrix_checker_task = Task(
            description=(matrix_checker_task_description),
            expected_output=(matrix_checker_task_expected_output),
            agent=matrix_checker,
            context=[matrix_creator_task],
        )

        ### Finally, compose Crew
        return Crew(
                agents=[matrix_creator, matrix_checker],
                tasks=[matrix_creator_task],
                manager_agent=orchestrator,
                memory=True,
                process=Process.hierarchical,
                verbose=1
            )