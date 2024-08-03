
from crewai import Agent, Task, Crew, Process
from agents.base import CustomCrew
from tools.exam import ExamTool

class ExamCrew(CustomCrew):
    def __init__(self):
        super().__init__()
        self.project = "TẠO_ĐỀ_BÀI_THI"

    def _get_crew(self):
        orchestrator = self._create_orchestrator_agent()
        exam_generator = self._create_exam_generator_agent()
        checker = self._create_checker_agent()

        orchestrator_task = self._create_orchestrator_task(orchestrator)
        exam_generator_task = self._create_exam_generator_task(exam_generator)
        checker_task = self._create_checker_task(checker)

        return Crew(
            agents=[orchestrator, exam_generator, checker],
            tasks=[orchestrator_task, exam_generator_task, checker_task],
            verbose=2
        )

    def _create_orchestrator_agent(self):
        return Agent(
            role="Người Điều Phối",
            goal="Điều phối quá trình tạo đề thi và đưa ra quyết định cuối cùng",
            backstory="Bạn là một điều phối viên giáo dục giàu kinh nghiệm, chịu trách nhiệm giám sát quá trình tạo đề thi.",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=self.tools
        )

    def _create_exam_generator_agent(self):
        return Agent(
            role="Người Tạo Đề Thi theo môn {topic}",
            goal="Tạo ra các đề thi và đáp án chất lượng cao dựa trên nội dung được cung cấp",
            backstory="Bạn là một chuyên gia trong việc tạo ra các bài kiểm tra thử thách và toàn diện cho học sinh.",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )

    def _create_checker_agent(self):
        return Agent(
            role="Người Kiểm Tra Đề Thi môn {topic}",
            goal="Xác minh và đánh giá chất lượng của đề thi và đáp án được tạo ra",
            backstory="Bạn là một người đánh giá tỉ mỉ với nhiều năm kinh nghiệm trong việc đánh giá chất lượng đề thi.",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )

    def _create_orchestrator_task(self, agent):
        return Task(
            description=(
                "1. Sử dụng ExamTool tìm dữ liệu từ {chapter}. Chỉ tìm trong phạm vi liên quan, không tìm lan man.\n"
                "2. Cấu trúc đề thi bao gồm {input}\n"
                "2. Chuyển dữ liệu vừa tìm được cho Người tạo đề thi tạo ra đề thi\n"
                "3. Tất cả output đều bằng tiếng Việt\n"
                "4. Sau khi có phản hồi từ Người Kiểm Tra Đề Thi, sẽ dựa trên bản đánh giá và ra quyết định\n"
                "5. Nếu đánh gía phản hồi tích cực, sẽ khởi tạo đề thi và câu trả lời theo dạng markdown, de-thi.md, cau-tra-loi.md\n"
                "6. Nếu đánh giá chưa tốt, yêu cầu Người tạo đề thi xem xét thử lại việc tạo đề thi (tối đa là 3 lần thử)"
            ),
            expected_output="dữ liệu có được từ kết quả tìm kiếm",
            agent=agent,
            output_file="dulieu-de-thi.md",
            tools=[ExamTool.get_chapter]
        )

    def _create_exam_generator_task(self, agent):
        return Task(
            description=(
                "1. Nhận thông tin nội dung cho một chương cụ thể từ Người Điều Phối.\n"
                "2. Tạo một đề thi toàn diện dựa trên nội dung đã cung cấp. Không tạo đề thi cho môn học khác\n"
                "3. Tạo một đáp án riêng cho đề thi đã tạo.\n"
                "4. Đảm bảo đề thi bao gồm các mức độ khó khác nhau và các loại câu hỏi đa dạng.\n"
                "5. Trả lại cả đề thi và đáp án cho Người Kiểm Tra Đề Thi.\n"
                "6. Lưu đề thi và câu trả lời vào markdown file, de-thi.md, dap-an.md\n"
                "7. Tất cả output đều bằng tiếng Việt"
            ),
            expected_output="Đề Thi và đáp án theo yều cầu của người điều phối",
            output_file="de-thi.md, dap-an.md",
            agent=agent
        )

    def _create_checker_task(self, agent):
        return Task(
            description=(
                "1. Nhận đề thi và đáp án đã tạo từ Người Điều Phối.\n"
                "2. Xem xét kỹ lưỡng đề thi về số lượng câu hỏi, chất lượng đề thi, độ rõ ràng và tính phù hợp.\n"
                "3. Nếu tổng số lượng câu hỏi không chính xác so với {input}. Gửi yêu cầu tạo lại đề thi cho Người Điều Phối.\n"
                "4. Kiểm tra đáp án về độ chính xác và đầy đủ.\n"
                "5. Cung cấp phản hồi chi tiết về đề thi và đáp án, bao gồm cả đề xuất cải thiện nếu cần thiết.\n"
                "6. Trả lại đánh giá của bạn cho Người Điều Phối.\n"
                "7. Tất cả output đều bằng tiếng Việt"
            ),
            expected_output="Một bản đánh giá chi tiết việc tạo đề thi",
            output_file="danh-gia.md",
            agent=agent
        )

    def run(self, topic: str, chapter: str):
        input = """Đề thi bao gồm\n
                    2 câu trắc nghiệm cho phần động năng. Mỗi câu 10 điểm\n
                    3 câu trắc nghiệm cho phần áp suất. Mỗi câu 10 điểm\n
                    5 câu tự luận cho phần áp suất. Mỗi câu 20 điểm"""
        result = self.crew.kickoff({"topic": topic, "chapter": chapter, "input":input})
        return result

