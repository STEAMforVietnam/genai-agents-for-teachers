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

        orchestrator_task = Task(
            description=(orchestrator_task_description),
            expected_output=orchestrator_task_expected_output,
            agent=orchestrator,
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
            max_iter=1
        )
        
        # TODO: change Task args description and expected_output to take in prompt.txt
        matrix_creator_task = Task(
<<<<<<< HEAD
            description=(matrix_creator_task_description),
            expected_output=matrix_creator_task_expected_output,
            agent=[matrix_creator, matrix_checker],
=======
            description=(
                "Tạo Ma_Trận_Đề_Bài Kiểm tra phù hợp với các Chương và Bài học trong Sách Giáo khoa Vật Lý Lớp 10 của Nhà xuất bản Giáo dục Việt Nam thoả mãn các bước sau:"
                "1. Hãy dùng tool LessonRetrieverTool để tìm các tên các chương và bài học trích từ trích từ file mục_lục.pdf"
                "2. Lập các Ma_Trận_Đề_Bài Kiểm tra theo một cấu trúc dữ liệu MatrixJSON:\n"
                "[{{'topic': '...', 'sub_topic': '...', 'knowledge_level': '...', 'question_type': '...', 'number_of_questions': '...', 'total_points': '...'}}]\n"
                "3. Tất cả các output bằng tiếng Việt.\n"
                # "4. Nội dung trường thông tin 'Chương hoặc Chủ đề' cần tương ứng với tên các Chương của Sách Giáo khoa mà tôi nói ở trên đây\n"
                "5. Nội dung trường thông tin 'knowledge_level' là một trong 4 giá trị: 'Nhận biết', 'Thông hiểu', 'Vận dụng' hoặc 'Vận dụng cao' - thể hiện mức hiểu kiến thức từ thấp tới cao."
                "Dưới đây là các định nghĩa cho từng giá trị:\n"
                "5.1 Mức độ 'Nhận biết' thường được dùng cho các câu hỏi Trắc nghiệm đơn giản, có 2 câu trả lời ĐÚNG vs. SAI\n"
                "5.2 Mức độ 'Thông hiểu' thường được dùng cho các câu hỏi Trắc nghiệm khó hơn, có 4 phương án trả lời trong đó có 1 phương án đúng\n"
                "5.3 Các mức độ 'Vận dụng' và 'Vận dụng cao' thường được dùng cho các câu hỏi Tự luận\n"
                "6. Nội dung trường thông tin 'question_type' là một trong 2 giá trị: 'Trắc nghiệm' hoặc 'Tự luận'\n"
                "7. Nội dung trường thông tin 'Số câu hỏi' là một số nguyên từ 1 tới 2\n"
                "8. Nội dung trường thông tin 'Tổng số điểm' là một số nguyên từ 1 tới 10\n"
                "9. Các bài ở knowledge_level 'Nhận biết' có tổng số điểm bằng 40, và mỗi bài ở mức này tương đương với 4 điểm\n"
                "10. Các bài ở knowledge_level 'Thông hiểu' có tổng số điểm bằng 30, và mỗi bài ở mức này tương đương với 5 điểm\n"
                "11. Các bài ở knowledge_level 'Vận dụng' có tổng số điểm bằng 20, và mỗi bài ở mức này tương đương với 5 điểm\n"
                "12. Các bài ở knowledge_level 'Vận dụng cao' có tổng số điểm bằng 10, và mỗi bài ở mức này tương đương với 10 điểm\n"
            ),
            expected_output="Một $Ma_Trận_Đề_Bài theo cấu trúc JSON nêu trên.",
            agent=matrix_creator,
            output_json=MatrixJSON
>>>>>>> 3d10ea5a2795457459bc2845b59073ea4b9b9514
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
            # tools=self.tools,
            max_iter=2
        )

        matrix_checker_task = Task(
<<<<<<< HEAD
            description=(matrix_checker_task_description),
            expected_output=(matrix_checker_task_expected_output),
=======
            description=(
                "Kiểm tra và sủa lại cho tôi $Ma_Trận_Đề_Bài đã được tạo ở matrix_creator_task theo các tiêu chí sau:\n"
                "1. Ma_Trận_Đề_Bài có cấu trúc chính xác như cấu trúc MatrixJSON:\n"
                "[{{'topic': '...', 'sub_topic': '...', 'knowledge_level': '...', 'question_type': '...', 'number_of_questions': '...', 'total_points': '...'}}]\n"
                "2. Cả 4 giá trị nhận thức 'Nhận biết', 'Thông hiểu', 'Vận dụng' hoặc 'Vận dụng cao' đều xuất hiện trong Ma_Trận_Đề_Bài\n"
                "3. 'Tổng số điểm' của các items có 'knowledge_level' là 'Nhận biết', sau khi cộng lại phải là 40\n"
                "4. 'Tổng số điểm' của các items có 'knowledge_level' là 'Thông hiểu' sau khi cộng lại phải là 30\n"
                "5. 'Tổng số điểm' của các items có 'knowledge_level' là 'Vận dụng' sau khi cộng lại phải là 20\n"
                "6. 'Tổng số điểm' của các items có 'knowledge_level' là 'Vận dụng cao' sau khi cộng lại phải là 10\n"
                # "7. Mỗi trường thông tin 'Chương hoặc Chủ đề' cần được điền với tên chương hoặc bài học từ file mục_lục.pdf"
                "Chỉnh sửa lại $Ma_Trận_Đề_Bài nếu chưa chính xác"
                "Nếu không có gì cần phải chỉnh sửa, thì trả lại dữ liệu đầu vào $Ma_Trận_Đề_Bài như ban đầu"
                
            ),
            expected_output=("một $Ma_Trận_Đề_Bài theo cấu trúc MatrixJSON"),
>>>>>>> 3d10ea5a2795457459bc2845b59073ea4b9b9514
            agent=matrix_checker,
            # output_json=MatrixJSON,
            # output_file="matrix.json",
            context=[matrix_creator_task],
        )

        ### ADD HTML Creator Agent (Thiết kế WEB)
        html_creator = Agent(
            role="html_creator",
            goal="Bạn sẽ giúp tôi tạo HTML từ input data $Ma_Trận_Đề_Bài bạn sẽ nhận được",
            backstory="Bạn là web developer có kinh nghiệm hơn 10 năm.",
            allow_delegation=False,
            llm=self.llm, 
            verbose=True, 
            tools=[create_matrix_html_maker_tool],
            max_iter=1
        )
        
        html_task = Task(
            description=(
                "pass input data $Ma_Trận_Đề_Bài cho tool MatrixHTMLMakerTool để tạo 1 file HTML."
                "You should invoke MatrixHTMLMakerTool with argument `input = $Ma_Trận_Đề_Bài`. For example:"
                "input = [{{'topic': 'test', 'sub_topic': 'example', 'knowledge_level': 'Nhận biết', 'question_type': 'Trắc nghiệm', 'number_of_questions': '4', 'total_points': '40'}}, {{'topic': 'Cơ học', 'sub_topic': 'Động lực học', 'knowledge_level': 'Thông hiểu', 'question_type': 'Tự luận', 'number_of_questions': '3', 'total_points': '30'}}]\n"
                "Sau đó, trả lại kết quả từ tool MatrixHTMLMakerTool"
            ),
            # TODO: somehow the tool output is not passed back to Agent Output
            # SO expected_output is never met and the agent + the task fall into infinite loop
            expected_output=(
                "một filepath dẫn đến file HTML được tạo từ tool, có đuôi `.html`"
            ),
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