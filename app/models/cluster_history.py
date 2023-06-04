from typing import Optional, List
from pydantic import BaseModel

from app.models.base import RootModel


class MinimumThesisData(BaseModel):
    thesis_id: str
    student_name: str
    student_id: str
    thesis_title: str


class ClusterGroupData(BaseModel):
    name: str
    description: Optional[str]
    children: List[MinimumThesisData]


class ClusterHistory(RootModel):
    class Collection:
        name = "cluster_history"

    name: str
    description: Optional[str]
    children: List[ClusterGroupData]