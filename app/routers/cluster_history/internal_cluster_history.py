from fastapi import APIRouter
from app.dto.common import BaseResponse
from app.dto.cluster_history_dto import WorkerClusterHistoryResponse, ClusterHistoryResultPutRequest, ClusterHistoryStatusPutRequest
from app.services.cluster_history_service import ClusterHistoryService


internal_route = APIRouter(tags=['Cluster History'], prefix="/cluster_history")


@internal_route.get(
    "/{history_id}/worker_data",
    response_model=WorkerClusterHistoryResponse
)
async def get_worker_data(
    history_id: str,
):
    data = await ClusterHistoryService().get_worker_data(history_id=history_id)
    
    return WorkerClusterHistoryResponse(
        message="Get worker data successfully",
        data=data
    )


@internal_route.put(
    "/{history_id}/cluster_result",
    response_model=BaseResponse
)
async def update_cluster_result(
    history_id: str,
    data: ClusterHistoryResultPutRequest
):
    await ClusterHistoryService().update_result(
        history_id=history_id,
        data=data
    )
    return BaseResponse(
        message="Update result successfully"
    )


@internal_route.put(
    "/{history_id}/status",
    response_model=BaseResponse
)
async def update_history_job_status(
    history_id: str,
    data: ClusterHistoryStatusPutRequest
):
    await ClusterHistoryService().update_status(
        history_id=history_id,
        status=data.status
    )
    return BaseResponse(
        message="Update status successfully"
    )