from enum import Enum
from pydantic import BaseModel
from typing import List, Optional


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

class EvaluationJSON(BaseModel):
    result: str
    evaluation: str
    data: List[Optional[MatrixJSON]]

###### MODELS FOR EXAM
class Question(BaseModel):
    desc: str
    points: float

class Answer(BaseModel):
    result: str
    explain: str

class Internal(BaseModel):
    topic: str
    sub_topic: str
    knowledge_level: KnowledgeLevelEnum
    question_type: str

class QuestionJSON(BaseModel):
    question: Question
    answer: Answer
    internal_stuff: Internal
        
class ExamJSON(BaseModel):
    question_nbr: int
    question_json: QuestionJSON
    
