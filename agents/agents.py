from typing import List
import json
from crewai import Agent, Task, Crew, Process
from crewai_tools import tool
from langchain_openai import ChatOpenAI
# from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_anthropic import ChatAnthropic
from langchain.tools import Tool
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_milvus.vectorstores import Milvus
from langchain.tools.retriever import create_retriever_tool
import os


class CustomCrew:
    def __init__(self):
        self.file_path: str = "."
        self.tools: List[Tool] = []
        self.llm = ChatOpenAI(
            model = "gpt-4o-mini",
            temperature = 0.5
        )
        self.crew: Crew = self._get_crew()
        

    def compile_questions(self, question_sets, is_answer_key=False):
        """
        Trích câu hỏi, số điểm, và câu trả lời ra từ dữ liệu trong `question_sets`
        Nếu đang tạo file pdf cho bộ đề, để giá trị của is_answer_key = False
        Nếu đang tạo file pdf cho bài giải, để giá trị của is_answer_key = True
        """
        list_of_questions = ""
        list_of_tl = ""

        for key, value in question_sets.items():
            question_items = value.get('đề_bài').get('Nội dung').replace("\\n", "\n").replace("- A.", "A.").replace("- B.", "B.").replace("- C.", "C.").replace("- D.", "D.").split('\n')
            answer_choices = ""
            for ans in question_items[1:]:
                if ans:
                    answer_choices += fr"""<li><div class="marginLeft2">{ans}</div></li>"""


            question = fr"""<!-- A question: -->
                <article class="QuestionItem marginBottom2">
                <h3>
                    <strong><u>Câu {key.replace('câu ', '')}</u></strong>
                    <span>({value.get('đề_bài').get('Số điểm')} điểm): </span>
                    <span>{question_items[0]}</span>

                </h3>
                <ul class="QuestionItem-options columnNumbers4">
                {answer_choices}
                </ul>
                </article>
                <!-- /A question -->
                """.replace('\x08', '\\b')

            if is_answer_key:
                if value.get("thông_tin_nội_bộ_(học_sinh_không_thấy)").get("Loại câu hỏi") == "Trắc nghiệm":
                    answer_key = fr"""<strong>Đáp Án: {value.get('đáp_án').get('Kết quả')}</strong>"""
                else:
                    trinh_bay = value.get('đáp_án').get('Trình bày').replace("\\n", "\n").replace(' \\\n ', ' \\\\\n ').replace(' \\\\ ', ' \\\\\n ').replace(' \\\\\ ', ' \\\\\n ').replace(' \\\ ', ' \\\\\n ')
                    answer_key = fr"""<strong>Đáp Án:</strong>""" + fr"""{trinh_bay}</strong>"""
                question += answer_key

            if value.get("thông_tin_nội_bộ_(học_sinh_không_thấy)").get("Loại câu hỏi") == "Trắc nghiệm":
                list_of_questions += question
            elif value.get("thông_tin_nội_bộ_(học_sinh_không_thấy)").get("Loại câu hỏi") == "Tự luận":
                list_of_tl += question

        return list_of_questions, list_of_tl

    def merge_all_sections(self, list_of_questions, list_of_tl):
        TEST_TMPL = """
        <!DOCTYPE html>
        <html>
            <head>
            <meta charset="utf-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1" />
            <title></title>
            <script type="text/javascript" id="MathJax-script" async
                src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js">
            </script>
            <style>
                * {
                    box-sizing: border-box;
                }
                html {
                font-size: 10px;
                }
                body {
                font-family: 'Times New Roman', Times, serif;
                font-size: 1.6rem;
                }
                h1 {
                font-size: 2rem;
                text-align: center;
                margin: 0 0 .5rem;
                }
                h2, h3 {
                font-size: 1.6rem;
                font-weight: normal;
                margin-bottom: 0;
                }
                .container {
                width: 100%;
                max-width: 80rem;
                margin: 0 auto;
                padding: 2.4rem 1.6rem;
                }
                .marginLeft1 {
                margin-left: .25rem;
                }
                .marginLeft2 {
                margin-left: .5rem;
                }
                .marginBottom1 {
                margin-bottom: .5rem;
                }
                .marginBottom1 {
                margin-bottom: 1rem;
                }
                .marginBottom2 {
                margin-bottom: 1.5rem;
                }
                .marginBottom3 {
                margin-bottom: 3rem;
                }

                footer {
                text-align: center;
                }


                table {
                width: 100%;
                border-width: 0;
                border-spacing: 0px;
                }
                td {
                padding: .25rem .5rem;
                text-align: center;
                }

                .QuestionItem {}
                .QuestionItem-options {
                list-style-type: none;
                padding-left: 4.5rem;
                margin: 0;
                display: flex;
                flex-wrap: wrap;
                }
                .QuestionItem-options li {
                padding-right: 1.5rem;
                margin-top: 1rem;
                display: flex;
                }
                .QuestionItem-options li.isCorrectAnswer > strong {
                color: red;
                }

                .QuestionItem-options.columnNumbers1 li {
                width: 100%;
                }
                .QuestionItem-options.columnNumbers2 li {
                width: 50%;
                }
                .QuestionItem-options.columnNumbers3 li {
                width: 33.33%;
                }
                .QuestionItem-options.columnNumbers4 li {
                width: 25%;
                }


            </style>
            <meta name="description" content="" />
            </head>"""

        title = f"""<body>
            <div class="container">
                <header class="marginBottom3">
                    <table>
                        <tr>
                            <td>
                                <div>{province}</div>
                                <div><strong>{school}</strong></div>
                                <br>
                                <div><strong>Đề chính thức</strong></div>
                                <div><em>(Đề gồm 01 trang)</em></div>
                            </td>
                            <td>
                                <h1>{exam_name}</h1>
                                <div>
                                    <strong>Năm học: {year}</strong><br>
                                    <strong>Môn: {subject}</strong><br>
                                    <strong>Lớp: {class_year}</strong><br>
                                    <strong>Thời gian: {total_time} phút</strong>&nbsp;<em>(Không kể thời gian giao đề)</em>
                                </div>
                            </td>
                        </tr>
                    </table>
                </header>
        """

        part_1 = fr"""
                <main>
                    <!-- PART 1: TRẮC NGHIỆM -->
                    <section class="marginBottom3">
                        <h2>
                            <strong><u>I. Trắc nghiệm:</u></strong>
                            <strong class="marginLeft1"><em>Chọn câu trả lời đúng nhất trong các câu sau:</em></strong>
                        </h2>

                        {list_of_questions}

                    </section>"""
        part_2 = fr"""
                    <!-- PART 2: TỰ LUẬN -->
                    <section class="marginBottom3">
                        <h2>
                            <strong><u>II. Tự luận:</u></strong>
                        </h2>

                        {list_of_tl}

                    </section>
                </main>"""

        footer = """
                <footer>
                    <div><em>.............................Hết................................</em></div>
                    <div><em>Cán bộ coi thi không giải thích gì thêm!</em></div>
                </footer>
            </div>
        </html>"""
        return TEST_TMPL+title+part_1+part_2+footer

    def exam_generation(self, question_sets, is_answer_key=False):
        list_of_questions, list_of_tl = self.compile_questions(question_sets, is_answer_key)
        html_content = self.merge_all_sections(list_of_questions, list_of_tl)
        return html_content
    
    @tool("HTMLMakerTool")
    def create_html_maker_tool(self, json_output):
        """
        This tool creates an html file from the JSON file
        """
        print("DỮ LIỆU JSON TRẢ LẠI")
        print("===============")
        print(json_output)
        # exam_json_file = os.path.join(self.file_path, "./exam-in-progress.json")
        # exam_html_file = os.path.join(self.file_path, "./exam.html")
        # with open(exam_json_file, "r", encoding="utf-8") as file:
        #     question_sets = json.load(file)
        #     question_html = self.exam_generation(question_sets=question_sets)
        #     with open(exam_html_file, "w", encoding="utf-8") as exam:
        #         exam.write(question_html)
        
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
        self.tools.append(self.create_html_maker_tool)

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
            "Sau đó, hãy sử dụng các thông tin đã được như Input để bạn tạo file HTML. Dùng tool HTMLMakerTool để hoàn thành",
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

        ### Add Matrix Creator Agent (Ngừoi Kiến Tạo), responsible for all "Tạo" task
        # TODO: change Agent args roal, goal, backstory to take in prompt.txt
        matrix_creator = Agent(
            role="Giáo viên tạo Ma Trận Bài Kiểm Tra và Bài Tập Vật Lý",
            goal=("Bạn sẽ giúp tôi tạo Ma_Trận_Đề_Bài phục vụ cho việc kiểm tra, đánh giá và nhận xét học sinh trong môn Vật Lý Lớp 9"
            ), # TODO: COPY HƯỚNG DẪN
            backstory="Bạn là một giáo viên dạy Vật Lý ở một trường trung học phổ thông tại nội thành Hà Nội",
            allow_delegation=False,
            llm=self.llm,
            verbose=True,
            tools=self.tools,
            max_iter=2
        )
        
        # TODO: change Task args description and expected_output to take in prompt.txt
        matrix_creator_task = Task(
            description=(
                "Bạn tạo Ma_Trận_Đề_Bài Kiểm tra phù hợp với với các Chương và Bài học trong Sách Giáo khoa Vật Lý Lớp 10 của Nhà xuất bản Giáo dục Việt Nam thoả mãn các bước sau:"
                "1. Hãy dùng tool LessonRetrieverTool để tìm các tên các chương và bài học trích từ Mục lục của Sách Giáo khoa"
                "2. Lập các Ma_Trận_Đề_Bài Kiểm tra theo một cấu trúc dữ liệu JSON giống với cấu trúc sau:\n"
                """[
                    {
                        "Chương hoặc Chủ đề": "...",
                        "Nội dung hoặc Đơn vị Kiến thức": "...",
                        "Mức độ Nhận thức": "...",
                        "Loại câu hỏi": "...",
                        "Số câu hỏi": "...",
                        "Tổng số điểm": "..."
                    }
                    ]
                """
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
        )

        ### Add Matrix Checker Agent (Nguời Kiểm Định), responsible for all "Kiểm Tra Task"
        matrix_checker = Agent(
            role="Giáo viên Kiểm Tra Ma Trận Bài Kiểm Tra",
            goal="Bạn sẽ giúp tôi kiểm tra và đánh giá Ma_Trận_Đề_Bài cho môn Vật Lý Lớp 9",
            backstory="Bạn là một giáo viên dạy Vật Lý ở một trường trung học phổ thông tại nội thành Hà Nội",
            allow_delegation=False,
            llm=self.llm,
            verbose=True,
            tools=self.tools,
            max_iter=2
        )

        matrix_checker_task = Task(
            description=(
                "Kiểm tra và đánh giá lại cho tôi Ma_Trận_Đề_Bài đã được tạo ở matrix_creator_task theo các tiêu chí sau:\n"
                "1. Một một item trong Ma_Trận_Đề_Bài có cấu trúc chính xác như sau:\n"
                """
                    {
                        "Chương hoặc Chủ đề": "...",
                        "Nội dung hoặc Đơn vị Kiến thức": "...",
                        "Mức độ Nhận thức": "...",
                        "Loại câu hỏi": "...",
                        "Số câu hỏi": "...",
                        "Tổng số điểm": "..."
                    }
                """
                "2. Cả 4 giá trị nhận thức 'Nhận biết', 'Thông hiểu', 'Vận dụng' hoặc 'Vận dụng cao' đều xuất hiện trong Ma_Trận_Đề_Bài\n"
                "3. 'Tổng số điểm' của các items có 'Mức độ Nhận thức' là 'Nhận biết', sau khi cộng lại phải là 40\n"
                "4. 'Tổng số điểm' của các items có 'Mức độ Nhận thức' là 'Thông hiểu' sau khi cộng lại phải là 30\n"
                "5. 'Tổng số điểm' của các items có 'Mức độ Nhận thức' là 'Vận dụng' sau khi cộng lại phải là 20\n"
                "6. 'Tổng số điểm' của các items có 'Mức độ Nhận thức' là 'Vận dụng cao' sau khi cộng lại phải là 10\n"
                "7. Mỗi trường thông tin 'Chương hoặc Chủ đề' cần được điền với tên chương trong Sách Giáo khoa chứa nội dung kiến thức tương ứng"
            ),
            expected_output=("Một đánh giá ngắn gọn và hướng dẫn chỉnh sửa cần thiết để Ma_Trận_Đề_Bài đúng với tiêu chí đề ra. No Yapping"),
            agent=matrix_checker,
            context=[matrix_creator_task],
        )

        ### Add Orchestrator (Người Giám Sát)
        orchestrator = Agent(
            role="Một người giám sát, hướng dẫn cho matrix_creator và matrix_checker các bước tiếp theo",
            goal=("Bạn sẽ giao việc tạo $Ma_Trận_Đề_Bài cho matrix_creator, và sẽ nhận lại một đánh giá về $Ma_Trận_Đề_Bài từ matrix_checker."
            "Sau đó, dựa trên kết quả nhận tại từ matrix_checker, bạn sẽ chọn một trong hai quyết định:"
            "1. Yêu cầu matrix_creator sửa lại $Ma_Trận_Đề_Bài theo gợi ý từ matrix_checker"
            "2. Nhận định công việc đã hoàn thành và tiến hành bước tiếp theo, là tạo file HTML bằng tool HTMLMakerTool"),
            backstory="",
            allow_delegation=True,
            llm=self.llm,
            verbose=True,
            tools=self.tools,
            max_iter=2
        )

        orchestrator_task = Task(
            description=(
                "1. Xác định các khái niệm và kỹ năng cần kiểm tra cho từng chủ đề {sub_topics}\n"
                "2. Tạo các câu hỏi trắc nghiệm và tự luận để đánh giá sự hiểu biết của học sinh về từng chủ đề trong {sub_topics}.\n"
                "3. Phát triển các bài tập để học sinh thực hành và củng cố kiến thức.\n"
                "4. Bao gồm các câu hỏi và bài tập ở nhiều mức độ khó khác nhau để phù hợp với trình độ của học sinh, đi từ dễ đến khó, bao gồm các bài kiểm tra 15 phút và một tiết (45 phút).\n"
                "5. Đảm bảo các câu hỏi và bài tập phù hợp với tiêu chuẩn chương trình học.\n"
                "6. Cung cấp hướng dẫn chấm điểm và đáp án cho các câu hỏi và bài tập."
                "7. Tất cả các output bằng tiếng Việt."
            ),
            expected_output="",
            agent=orchestrator,
            context=[matrix_creator_task, matrix_checker_task],
            # output_file
        )

        ### Finally, compose Crew
        self.crew = Crew(
                agents=[matrix_creator, matrix_checker],
                tasks=[matrix_creator_task, matrix_checker_task],
                manager_agent=orchestrator,
                memory=True,
                process=Process.hierarchical,
                verbose=2
            )