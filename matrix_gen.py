from dotenv import load_dotenv
load_dotenv()
from agents.matrix import MatrixCrew

topic= "Vật Lý Lớp 10"
sub_topics = "chuyển động tròn"

matrix_crew = MatrixCrew()
inputs = {
    "topic": topic,
    "sub_topics": sub_topics
}
matrix_crew.run(inputs)
