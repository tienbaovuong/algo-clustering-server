from pydantic import BaseModel
from typing import List, Optional

from app.dto.common import BaseResponseData
from app.dto.cluster_history_dto import ShortClusterHistory


class ClusterHistoryCreateResponse(BaseResponseData):
    data: Optional[ShortClusterHistory]


class ClusterHistoryConfig(BaseModel):
    order: list = [0, 1, 2, 3]
    number_of_clusters: int = 10
    max_item_each_cluster: int = 10


class ClusterHistoryThesisFilter(BaseModel):
    title: Optional[str]
    semester: Optional[str]
    created_at: Optional[str]


class ClusterHistoryCreateRequest(BaseModel):
    config: ClusterHistoryConfig
    filter: ClusterHistoryThesisFilter


class ClusterNameSuggestionRequest(BaseModel):
    thesis_list_id: List[str]


class ClusterNameSuggestionResponse(BaseResponseData):
    data: List[str]