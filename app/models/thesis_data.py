from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from pymongo import ASCENDING, IndexModel

from app.models.base import RootModel


class ThesisStudentData(BaseModel):
    student_name: str
    student_id: str


class ThesisDataInput(BaseModel):
    semester: str
    title: str
    title_vector: Optional[List]
    category: str
    category_vector: Optional[List]
    expected_result: str
    expected_result_vector: Optional[List]
    problem_solve: str
    problem_solve_vector: Optional[List]
    student_data: ThesisStudentData
    

class ThesisData(RootModel, ThesisDataInput):
    class Collection:
        name = "thesis_data"
        indexes = [
            IndexModel(
                [
                    ("semester", ASCENDING),
                ],
                unique=False,
            ),
            IndexModel(
                [
                    ("semester", ASCENDING),
                    ("student_data.student_id", ASCENDING),
                ],
                unique=True,
            )
        ]

    updated_at: datetime
    need_nlp_extract: bool = True
    nlp_job_id: Optional[str]