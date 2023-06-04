from app.dto.cluster_history_dto import ClusterHistoryPutRequest

class ClusterHistoryService:
    async def list(
        self,
        name: str,
        page: int = 1,
        limit: int = 10,
    ):
        pass

    async def get(
        self,
        cluster_history_id: str
    ):
        pass

    async def put(
        self,
        cluster_history_id: str,
        new_cluster_history: ClusterHistoryPutRequest,
    ):
        pass

    async def delete(
        self,
        cluster_history_id: str
    ):
        pass