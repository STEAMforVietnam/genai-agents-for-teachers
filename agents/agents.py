from typing import List
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_anthropic import ChatAnthropic
from langchain.tools import Tool
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_milvus.vectorstores import Milvus
from langchain.tools.retriever import create_retriever_tool
import os


class CustomCrew:
    def __init__(self):
        self.file_path: str = "."
        self.tools: List[Tool] = []
        self.crew: Crew = self._get_crew()

    def _get_tools(self):
        """
        create all tools that will be available for all agents and crews
        """

        ### ADD RETRIEVER TOOL
        embedding_model = HuggingFaceEmbeddings(model_name='keepitreal/vietnamese-sbert')
        retriever = Milvus(
            embedding_function=embedding_model,
            collection_name="s4v_python_oh",
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

        ### Add Test Creator Agent, responsible for all "Tạo" task
        # TODO: change Agent args roal, goal, backstory to take in prompt.txt
        test_creator = Agent(
            role="Giáo viên tạo Bài Kiểm Tra và Bài Tập Vật Lý",
            goal="Tạo các bài kiểm tra và bài tập chính xác và phù hợp cho từng chủ đề của môn Vật Lý 9 ",
            backstory="Bạn chịu trách nhiệm tạo các bài kiểm tra và bài tập cho môn Vật Lý 9. "
                    "Bạn dựa vào công việc của Giáo viên Lập Kế Hoạch Nội Dung và Giáo viên Thiết Kế Bài Học, "
                    "những người cung cấp dàn ý và ngữ cảnh liên quan đến chủ đề. "
                    "Bạn tạo các bài kiểm tra và bài tập nhằm đánh giá sự hiểu biết của học sinh "
                    "và củng cố kiến thức đã học. "
                    "Bạn đảm bảo các bài kiểm tra và bài tập phù hợp với tiêu chuẩn chương trình học "
                    "và trình độ của học sinh.",
            allow_delegation=False,
            llm=self.llm,
            verbose=True,
            tools=self.tools
        )
        
        # TODO: change Task args description and expected_output to take in prompt.txt
        test_assignment_task = Task(
            description=(
                "1. Xác định các khái niệm và kỹ năng cần kiểm tra cho từng chủ đề {sub_topics}\n"
                "2. Tạo các câu hỏi trắc nghiệm và tự luận để đánh giá sự hiểu biết của học sinh về từng chủ đề trong {sub_topics}.\n"
                "3. Phát triển các bài tập để học sinh thực hành và củng cố kiến thức.\n"
                "4. Bao gồm các câu hỏi và bài tập ở nhiều mức độ khó khác nhau để phù hợp với trình độ của học sinh, đi từ dễ đến khó, bao gồm các bài kiểm tra 15 phút và một tiết (45 phút).\n"
                "5. Đảm bảo các câu hỏi và bài tập phù hợp với tiêu chuẩn chương trình học.\n"
                "6. Cung cấp hướng dẫn chấm điểm và đáp án cho các câu hỏi và bài tập."
                "7. Tất cả các output bằng tiếng Việt."
            ),
            expected_output="Một bộ đề kiểm tra và bài tập chi tiết cho chủ đề {topic} và theo từng {sub_topics}"
                "bao gồm câu hỏi trắc nghiệm, câu hỏi tự luận, bài tập, hướng dẫn chấm điểm và đáp án. Trả lại output theo dạng Markdown",
            agent=test_creator,
        )

        ### Add Test Checker Agent, responsible for all "Kiểm Tra Task"


        ### Finally, compose Crew
        self.crew = Crew(
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

        ### Add Matrix Creator Agent, responsible for all "Tạo" task
        # TODO: change Agent args roal, goal, backstory to take in prompt.txt
        matrix_creator = Agent(
            role="Giáo viên tạo Bài Kiểm Tra và Bài Tập Vật Lý",
            goal="Tạo các bài kiểm tra và bài tập chính xác và phù hợp cho từng chủ đề của môn Vật Lý 9 ",
            backstory="Bạn chịu trách nhiệm tạo các bài kiểm tra và bài tập cho môn Vật Lý 9. "
                    "Bạn dựa vào công việc của Giáo viên Lập Kế Hoạch Nội Dung và Giáo viên Thiết Kế Bài Học, "
                    "những người cung cấp dàn ý và ngữ cảnh liên quan đến chủ đề. "
                    "Bạn tạo các bài kiểm tra và bài tập nhằm đánh giá sự hiểu biết của học sinh "
                    "và củng cố kiến thức đã học. "
                    "Bạn đảm bảo các bài kiểm tra và bài tập phù hợp với tiêu chuẩn chương trình học "
                    "và trình độ của học sinh.",
            allow_delegation=False,
            llm=self.llm,
            verbose=True,
            tools=self.tools
        )
        
        # TODO: change Task args description and expected_output to take in prompt.txt
        matrix_creator_task = Task(
            description=(
                "1. Xác định các khái niệm và kỹ năng cần kiểm tra cho từng chủ đề {sub_topics}\n"
                "2. Tạo các câu hỏi trắc nghiệm và tự luận để đánh giá sự hiểu biết của học sinh về từng chủ đề trong {sub_topics}.\n"
                "3. Phát triển các bài tập để học sinh thực hành và củng cố kiến thức.\n"
                "4. Bao gồm các câu hỏi và bài tập ở nhiều mức độ khó khác nhau để phù hợp với trình độ của học sinh, đi từ dễ đến khó, bao gồm các bài kiểm tra 15 phút và một tiết (45 phút).\n"
                "5. Đảm bảo các câu hỏi và bài tập phù hợp với tiêu chuẩn chương trình học.\n"
                "6. Cung cấp hướng dẫn chấm điểm và đáp án cho các câu hỏi và bài tập."
                "7. Tất cả các output bằng tiếng Việt."
            ),
            expected_output="Một bộ đề kiểm tra và bài tập chi tiết cho chủ đề {topic} và theo từng {sub_topics}"
                "bao gồm câu hỏi trắc nghiệm, câu hỏi tự luận, bài tập, hướng dẫn chấm điểm và đáp án. Trả lại output theo dạng Markdown",
            agent=matrix_creator,
        )

        ### Add Matrix Checker Agent, responsible for all "Kiểm Tra Task"


        ### Finally, compose Crew
        self.crew = Crew(
                agents=[matrix_creator],
                tasks=[matrix_creator_task],
                verbose=2
            )