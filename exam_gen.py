

from dotenv import load_dotenv
load_dotenv()
from agents.exam import ExamCrew

topic= "Vật Lý Lớp 10"
chapter = "chương 6, chương 8"

exam_crew = ExamCrew()
inputs = {
    "topic": topic,
    "chapter": chapter
}
result = exam_crew.run(topic=topic, chapter=chapter)
if isinstance(result, dict) and 'exam' in result and 'answer_key' in result:
    print("Đề thi và đáp án đã được tạo và lưu.")
else:
    print("Quá trình tạo đề thi đã hoàn thành, nhưng định dạng đầu ra không như mong đợi.")
    print(result)