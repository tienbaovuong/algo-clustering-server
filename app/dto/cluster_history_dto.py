from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime

from app.dto.common import (
    BasePaginationResponseData, BaseResponseData, BeanieDocumentWithId
)
from app.models.cluster_history import ClusterGroupData, ClusterJobStatus, MinimumThesisData, ClusterConfig, JobStatusType
from app.models.thesis_data import ThesisData


# DTO for list response (Inherit BeanieDocumentWithId so the response include databaseID)
class ShortClusterHistory(BeanieDocumentWithId):
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    cluster_job_status: ClusterJobStatus


# DTO for detail response
class FullClusterHistory(ShortClusterHistory):
    clusters: List[ClusterGroupData]
    non_clustered_thesis: List[MinimumThesisData]
    config: ClusterConfig


# DTO for worker response
class WorkerClusterHistory(FullClusterHistory):
    ready_for_cluster: Optional[bool]
    detail_thesis_dict: Optional[Dict[str, ThesisData]]


class ClusterHistoryResponse(BaseResponseData):
    data: Optional[FullClusterHistory]


class ClusterHistoryPaginationData(BasePaginationResponseData):
    items: List[ShortClusterHistory]


class WorkerClusterHistoryResponse(BaseResponseData):
    data: Optional[WorkerClusterHistory]


class ClusterHistoryPaginationResponse(BaseResponseData):
    data: ClusterHistoryPaginationData


#DTO for update request
class ClusterHistoryPutRequest(BaseModel):
    name: Optional[str]
    description: Optional[str]
    clusters: Optional[List[ClusterGroupData]]


class ClusterHistoryResultPutRequest(BaseModel):
    cluster_result: List[dict]


class ClusterHistoryStatusPutRequest(BaseModel):
    status: JobStatusType