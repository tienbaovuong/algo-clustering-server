from datetime import datetime
from fastapi import APIRouter, Depends
from app.helpers.auth_helpers import get_current_user
from app.dto.clustering_dto import (ClusterHistoryCreateResponse, ClusterHistoryCreateRequest,
    ClusterNameSuggestionRequest, ClusterNameSuggestionResponse)
from app.dto.cluster_history_dto import ShortClusterHistory
from app.services.thesis_data_service import ThesisDataService
from app.services.cluster_history_service import ClusterHistoryService
from app.models.cluster_history import ClusterConfig

route = APIRouter(tags=['Clustering'], prefix="/clustering")


@route.post(
    "/start",
    response_model=ClusterHistoryCreateResponse
)
async def init_clustering(
    data: ClusterHistoryCreateRequest,
    user: str = Depends(get_current_user),
):
    filter_data = data.filter
    created_at = None
    if filter_data.created_at:
        created_at = datetime.strptime(filter_data.created_at, '%Y-%m-%dT%H:%M:%SZ')
    thesis_list, total = await ThesisDataService().list_thesis(
        title=filter_data.title,
        semester=filter_data.semester,
        created_at=created_at,
        limit=-1,
    )

    config_data = data.config
    parse_config_data = ClusterConfig(**config_data.dict())

    history = await ClusterHistoryService().create_history(
        config=parse_config_data,
        thesis_list=thesis_list
    )

    return ClusterHistoryCreateResponse(
        message="Start a clustering job successfully",
        data=ShortClusterHistory(_id=history.id,**history.dict())
    )


@route.post(
    "/suggestions",
    response_model=ClusterNameSuggestionResponse
)
async def get_cluster_name_suggestion(
    data: ClusterNameSuggestionRequest,
    user: str = Depends(get_current_user),
):
    suggestions = await ThesisDataService().suggest_cluster_name(data.thesis_list_id)
    return ClusterNameSuggestionResponse(
        message="Get name suggestion successfully",
        data=suggestions
    )