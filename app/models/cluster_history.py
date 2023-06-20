from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

from app.models.base import RootModel, RootEnum


class MinimumThesisData(BaseModel):
    thesis_id: str
    student_name: str
    student_id: str
    thesis_title: str


class ClusterGroupData(BaseModel):
    name: str
    description: Optional[str]
    children: List[MinimumThesisData]


class JobStatusType(str, RootEnum):
    FAILED = "FAILED"
    WAITING_NLP = "WAITING NLP"
    CLUSTERING = "CLUSTERING"
    FINISHED = "FINISHED"


class ClusterJobStatus(BaseModel):
    total_done_nlp: int
    total_thesis: int
    status: JobStatusType


class ClusterConfig(BaseModel):
    order: list = [0, 1, 2, 3]
    number_of_clusters: int = 10
    max_item_each_cluster: int = 10


class ClusterHistory(RootModel):
    class Collection:
        name = "cluster_history"

    name: str
    description: Optional[str]
    clusters: List[ClusterGroupData]
    non_clustered_thesis: List[MinimumThesisData]
    updated_at: datetime
    cluster_job_status: ClusterJobStatus
    config: ClusterConfig