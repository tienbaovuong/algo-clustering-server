from datetime import datetime, timedelta
from typing import Optional, List

from beanie import PydanticObjectId
from beanie.operators import RegEx, In, Set
from celery.result import AsyncResult

from app.helpers.exceptions import NotFoundException
from app.dto.cluster_history_dto import ClusterHistoryPutRequest, ShortClusterHistory, FullClusterHistory, \
    WorkerClusterHistory, ClusterHistoryResultPutRequest
from app.models.cluster_history import ClusterHistory, MinimumThesisData, ClusterJobStatus, JobStatusType
from app.models.thesis_data import ThesisData
from app.worker.tasks.nlp_task import schedule_preprocess
import logging

_logger = logging.getLogger(__name__)


def parse_thesis_data_to_minimum_data(thesis: ThesisData):
    parse_thesis = MinimumThesisData(
        thesis_id=str(thesis.id),
        student_name=thesis.student_data.student_name,
        student_id=thesis.student_data.student_id,
        thesis_title=thesis.title
    )
    return parse_thesis

class ClusterHistoryService:
    async def list_history(
        self,
        name: Optional[str],
        page: int = 1,
        limit: int = 10,
    ):
        query = []
        skip = limit * (page - 1)
        if name:
            query.append(RegEx(ClusterHistory.name, name, options="i"))
        query_task = ClusterHistory.find_many(*query)
        total = await query_task.count()
        cluster_history_list = await query_task.skip(skip).limit(limit).project(ShortClusterHistory).to_list()
        return cluster_history_list, total

    async def get(
        self,
        cluster_history_id: str
    ):
        cluster_history = await ClusterHistory.find_one({'_id': PydanticObjectId(cluster_history_id)}).project(FullClusterHistory)
        if not cluster_history:
            raise NotFoundException("No cluster history")
        return cluster_history

    async def put(
        self,
        cluster_history_id: str,
        new_cluster_history: ClusterHistoryPutRequest,
    ):
        cluster_history = await ClusterHistory.find_one({'_id': PydanticObjectId(cluster_history_id)})
        if not cluster_history:
            raise NotFoundException("No cluster history")
        await cluster_history.update(**new_cluster_history)
        return cluster_history

    async def delete(
        self,
        cluster_history_id: str
    ):
        cluster_history = await ClusterHistory.find_one({'_id': PydanticObjectId(cluster_history_id)})
        if not cluster_history:
            raise NotFoundException("No cluster history")
        await cluster_history.delete()

    async def update_status(
        self,
        history_id: str,
        status: JobStatusType,
    ):
        cluster_history = await ClusterHistory.find_one({'_id': PydanticObjectId(history_id)})
        if not cluster_history:
            raise NotFoundException("No cluster history")
        await cluster_history.update(Set(ClusterHistory.cluster_job_status.status, status))

    async def update_result(
        self,
        history_id: str,
        data: ClusterHistoryResultPutRequest,
    ):
        cluster_history = await ClusterHistory.find_one({'_id': PydanticObjectId(history_id)})
        if not cluster_history:
            raise NotFoundException("No cluster history")
        _logger.info(data)
        update_data = {
            "cluster_job_status.status": JobStatusType.FINISHED
        }
        await cluster_history.update({"$set": update_data})

    async def get_worker_data(
        self,
        history_id: str,
    ):
        cluster_history = await ClusterHistory.find_one({'_id': PydanticObjectId(history_id)})
        if not cluster_history:
            raise NotFoundException("No cluster history")
        
        minimum_thesis_dict = {str(item.thesis_id): item for item in cluster_history.non_clustered_thesis}
        list_ids = minimum_thesis_dict.keys()

        thesis_list = await ThesisData.find_many(In(ThesisData.id, list_ids)).to_list()
        thesis_dict = {str(item.id): item for item in thesis_list}
        
        nlp_finish_counter = 0
        for key, value in thesis_dict.items():
            if not value.need_nlp_extract:
                nlp_finish_counter += 1
            else:
                res = AsyncResult(value.nlp_job_id)
                state = str(res.state)
                if state == "FAILURE" or (state == "PENDING" and value.updated_at < datetime.utcnow() - timedelta(minutes=5)):
                    schedule_preprocess(value.dict())

        new_total = len(thesis_list)
        old_total = len(list_ids)

        update_data = {}    
        if (old_total > new_total):
            new_minimum_list: List[MinimumThesisData] = []
            for id in list_ids:
                if thesis_dict.get(id):
                    new_minimum_list.append(minimum_thesis_dict.get(id))
            update_data["non_clustered_thesis"] = new_minimum_list

        job_status = ClusterJobStatus(
            total_done_nlp=nlp_finish_counter,
            total_thesis=new_total,
            status=cluster_history.cluster_job_status.status
        )
        ready_for_cluster = False
        if new_total == nlp_finish_counter:
            job_status.status = JobStatusType.CLUSTERING
            ready_for_cluster = True

        update_data["cluster_job_status"] = job_status

        await cluster_history.update({"$set": update_data})

        output = cluster_history.dict()
        output["ready_for_cluster"] = ready_for_cluster
        return WorkerClusterHistory(**output)

