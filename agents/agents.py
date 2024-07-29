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
        self.tools.append(create_exam_html_maker_tool)
        self.tools.append(create_matrix_html_maker_tool)

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
        test_creator = Agent(
            role="Giáo viên tạo Bài Kiểm Tra và Bài Tập Vật Lý",
            goal="Tạo các bài kiểm tra và bài tập chính xác và phù hợp cho từng chủ đề của môn Vật Lý 9."
            "Sau đó, hãy sử dụng các thông tin đã được như Input để bạn tạo file HTML. Dùng tool ExamHTMLMakerTool để hoàn thành",
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
                "2. Tạo 2 câu hỏi trắc nghiệm để đánh giá sự hiểu biết của học sinh về từng chủ đề trong {sub_topics}.\n"
                "3. Phát triển các bài tập để học sinh thực hành và củng cố kiến thức.\n"
                "4. Bao gồm các câu hỏi và bài tập ở nhiều mức độ khó khác nhau để phù hợp với trình độ của học sinh, đi từ dễ đến khó, bao gồm các bài kiểm tra 15 phút và một tiết (45 phút).\n"
                "5. Đảm bảo các câu hỏi và bài tập phù hợp với tiêu chuẩn chương trình học.\n"
                "6. Tất cả các output bằng tiếng Việt."
            ),
            expected_output="Một bộ đề kiểm tra và bài tập chi tiết cho chủ đề {topic} và theo từng {sub_topics}"
                "bao gồm câu hỏi trắc nghiệm, câu hỏi tự luận, bài tập, hướng dẫn chấm điểm và đáp án. Trả lại output theo dạng Markdown",
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

        ### Add Orchestrator (Người Giám Sát)
        orchestrator = Agent(
            role="Một người giám sát, hướng dẫn cho matrix_creator các bước tiếp theo",
            goal=("Bạn sẽ giao việc tạo $Ma_Trận_Đề_Bài cho matrix_creator."
            "Tiếp theo, hãy giao $Ma_Trận_Đề_Bài này cho matrix_checker và yêu cầu đánh giá. Cuối cùng, bạn sẽ nhận lại một đánh giá về từ matrix_checker."
            "Sau đó, dựa trên kết quả nhận tại từ matrix_checker, bạn sẽ chọn một trong hai quyết định:"
            "1. Yêu cầu matrix_creator sửa lại $Ma_Trận_Đề_Bài theo gợi ý từ matrix_checker"
            "2. Nhận định công việc đã hoàn thành trả lại kết quả $Ma_Trận_Đề_Bài"),
            backstory="",
            allow_delegation=False,
            llm=self.llm,
            verbose=True,
            max_iter=2
        )

        # html_maker = Agent()
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
            # output_file
        )

        ### Add Matrix Creator Agent (Ngừoi Kiến Tạo), responsible for all "Tạo" task
        # TODO: change Agent args roal, goal, backstory to take in prompt.txt
        matrix_creator = Agent(
            role="matrix_creator",
            goal=("Bạn sẽ giúp tôi tạo Ma_Trận_Đề_Bài phục vụ cho việc kiểm tra, đánh giá và nhận xét học sinh trong môn Vật Lý Lớp 9"
            ), # TODO: COPY HƯỚNG DẪN
            backstory="Bạn là một giáo viên dạy Vật Lý ở một trường trung học phổ thông tại nội thành Hà Nội",
            allow_delegation=False,
            llm=self.llm,
            verbose=True,
            tools=self.tools,
            max_iter=1
        )
        
        # TODO: change Task args description and expected_output to take in prompt.txt
        matrix_creator_task = Task(
            description=(
                "Bạn tạo Ma_Trận_Đề_Bài Kiểm tra phù hợp với các Chương và Bài học trong Sách Giáo khoa Vật Lý Lớp 10 của Nhà xuất bản Giáo dục Việt Nam thoả mãn các bước sau:"
                "1. Hãy dùng tool LessonRetrieverTool để tìm các tên các chương và bài học trích từ trích từ file mục_lục.pdf"
                "2. Lập các Ma_Trận_Đề_Bài Kiểm tra theo một cấu trúc dữ liệu JSON giống với cấu trúc sau:\n"
                "[{{'Chương hoặc Chủ đề': '...', 'Nội dung hoặc Đơn vị Kiến thức': '...', 'Mức độ Nhận thức': '...', 'Loại câu hỏi': '...', 'Số câu hỏi': '...', 'Tổng số điểm': '...'}}]\n"
                "3. Tất cả các output bằng tiếng Việt.\n"
                "4. Nội dung trường thông tin 'Chương hoặc Chủ đề' cần tương ứng với tên các Chương của Sách Giáo khoa mà tôi nói ở trên đây\n"
                "5. Nội dung trường thông tin 'Mức độ Nhận thức' là một trong 4 giá trị: 'Nhận biết', 'Thông hiểu', 'Vận dụng' hoặc 'Vận dụng cao' - thể hiện mức hiểu kiến thức từ thấp tới cao."
                "Dưới đây là các định nghĩa cho từng giá trị:\n"
                "5.1 Mức độ 'Nhận biết' thường được dùng cho các câu hỏi Trắc nghiệm đơn giản, có 2 câu trả lời ĐÚNG vs. SAI\n"
                "5.2 Mức độ 'Thông hiểu' thường được dùng cho các câu hỏi Trắc nghiệm khó hơn, có 4 phương án trả lời trong đó có 1 phương án đúng\n"
                "5.3 Các mức độ 'Vận dụng' và 'Vận dụng cao' thường được dùng cho các câu hỏi Tự luận\n"
                "6. Nội dung trường thông tin 'Loại câu hỏi' là một trong 2 giá trị: 'Trắc nghiệm' hoặc 'Tự luận'\n"
                "7. Nội dung trường thông tin 'Số câu hỏi' là một số nguyên từ 1 tới 2\n"
                "8. Nội dung trường thông tin 'Tổng số điểm' là một số nguyên từ 1 tới 10\n"
                "9. Các bài ở mức độ nhận thức 'Nhận biết' có tổng số điểm bằng 40, và mỗi bài ở mức này tương đương với 4 điểm\n"
                "10. Các bài ở mức độ nhận thức 'Thông hiểu' có tổng số điểm bằng 30, và mỗi bài ở mức này tương đương với 5 điểm\n"
                "11. Các bài ở mức độ nhận thức 'Vận dụng' có tổng số điểm bằng 20, và mỗi bài ở mức này tương đương với 5 điểm\n"
                "12. Các bài ở mức độ nhận thức 'Vận dụng cao' có tổng số điểm bằng 10, và mỗi bài ở mức này tương đương với 10 điểm\n"
            ),
            expected_output="Một Ma_Trận_Đề_Bài theo cấu trúc JSON nêu trên.",
            agent=matrix_creator,
            context=[orchestrator_task]
        )

        ### Add Matrix Checker Agent (Nguời Kiểm Định), responsible for all "Kiểm Tra Task"
        matrix_checker = Agent(
            role="matrix_checker",
            goal="Bạn sẽ giúp tôi kiểm tra và đánh giá Ma_Trận_Đề_Bài cho môn Vật Lý Lớp 9",
            backstory="Bạn là một giáo viên dạy Vật Lý ở một trường trung học phổ thông tại nội thành Hà Nội",
            allow_delegation=False,
            llm=self.llm,
            verbose=True,
            tools=self.tools,
            max_iter=1
        )

        matrix_checker_task = Task(
            description=(
                "Kiểm tra và đánh giá lại cho tôi Ma_Trận_Đề_Bài đã được tạo ở matrix_creator_task theo các tiêu chí sau:\n"
                "1. Một một item trong Ma_Trận_Đề_Bài có cấu trúc chính xác như sau:\n"
                "[{{'Chương hoặc Chủ đề': '...', 'Nội dung hoặc Đơn vị Kiến thức': '...', 'Mức độ Nhận thức': '...', 'Loại câu hỏi': '...', 'Số câu hỏi': '...', 'Tổng số điểm': '...'}}]\n"
                "2. Cả 4 giá trị nhận thức 'Nhận biết', 'Thông hiểu', 'Vận dụng' hoặc 'Vận dụng cao' đều xuất hiện trong Ma_Trận_Đề_Bài\n"
                "3. 'Tổng số điểm' của các items có 'Mức độ Nhận thức' là 'Nhận biết', sau khi cộng lại phải là 40\n"
                "4. 'Tổng số điểm' của các items có 'Mức độ Nhận thức' là 'Thông hiểu' sau khi cộng lại phải là 30\n"
                "5. 'Tổng số điểm' của các items có 'Mức độ Nhận thức' là 'Vận dụng' sau khi cộng lại phải là 20\n"
                "6. 'Tổng số điểm' của các items có 'Mức độ Nhận thức' là 'Vận dụng cao' sau khi cộng lại phải là 10\n"
                "7. Mỗi trường thông tin 'Chương hoặc Chủ đề' cần được điền với tên chương hoặc bài học từ file mục_lục.pdf"
            ),
            expected_output=("Một đánh giá ngắn gọn và hướng dẫn chỉnh sửa cần thiết để Ma_Trận_Đề_Bài đúng với tiêu chí đề ra. No Yapping"),
            agent=orchestrator,
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