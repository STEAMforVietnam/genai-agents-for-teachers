from enum import Enum
from pydantic import BaseModel



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