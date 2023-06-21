from datetime import datetime, timedelta
from typing import Optional, List

from beanie import PydanticObjectId
from beanie.operators import RegEx, In, Set
from celery.result import AsyncResult

from app.helpers.exceptions import NotFoundException
from app.dto.thesis_data_dto import ShortThesisData
from app.dto.cluster_history_dto import ClusterHistoryPutRequest, ShortClusterHistory, FullClusterHistory, \
    WorkerClusterHistory, ClusterHistoryResultPutRequest
from app.models.cluster_history import ClusterHistory, MinimumThesisData, ClusterJobStatus, JobStatusType, \
    ClusterConfig, ClusterGroupData
from app.models.thesis_data import ThesisData
from app.services.thesis_data_service import ThesisDataService
from app.worker.tasks.nlp_task import schedule_preprocess
from app.worker.tasks.clustering_task import schedule_clustering
import logging

_logger = logging.getLogger(__name__)


def parse_thesis_data_to_minimum_data(thesis: ShortThesisData):
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


    async def create_history(
        self,
        config: ClusterConfig = ClusterConfig(),
        thesis_list: List[ShortThesisData] = [],
    ):
        minimum_thesis_list: List[MinimumThesisData] = []
        for thesis in thesis_list:
            minimum_thesis_list.append(parse_thesis_data_to_minimum_data(thesis))
        new_history = ClusterHistory(
            name="New cluster history",
            clusters=[],
            non_clustered_thesis=minimum_thesis_list,
            updated_at=datetime.utcnow(),
            cluster_job_status=ClusterJobStatus(total_done_nlp=0, total_thesis=len(minimum_thesis_list), status=JobStatusType.WAITING_NLP),
            config=config
        )
        await new_history.save()
        schedule_clustering(str(new_history.id))
        return new_history
    


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
        
        update_data = {
            "cluster_job_status.status": JobStatusType.FINISHED
        }

        cluster_list: List[ClusterGroupData] = []
        for cluster in data.cluster_result:
            list_ids = []
            thesis_list: List[MinimumThesisData] = []
            for thesis in cluster.get("children"):
                list_ids.append(thesis.get("thesis_id"))
                thesis_list.append(MinimumThesisData(**thesis))
            suggest_name = (await ThesisDataService().suggest_cluster_name(list_ids))[0]
            parse_cluster = ClusterGroupData(
                name=suggest_name,
                children=thesis_list
            )
            cluster_list.append(parse_cluster)
        update_data["clusters"] = cluster_list

        await cluster_history.update({"$set": update_data})


    async def get_worker_data(
        self,
        history_id: str,
    ):
        cluster_history = await ClusterHistory.find_one({'_id': PydanticObjectId(history_id)})
        if not cluster_history:
            raise NotFoundException("No cluster history")
        
        minimum_thesis_dict = {str(item.thesis_id): item for item in cluster_history.non_clustered_thesis}
        list_ids = list(minimum_thesis_dict.keys())

        thesis_list = await ThesisDataService().get_list_by_ids(list_ids)
        thesis_dict = {str(item.id): item for item in thesis_list}
        
        nlp_finish_counter = 0
        for key, value in thesis_dict.items():
            if not value.need_nlp_extract:
                nlp_finish_counter += 1
            else:
                if value.nlp_job_id:
                    res = AsyncResult(value.nlp_job_id)
                    state = str(res.state)
                    if state == "FAILURE" or (state == "PENDING" and value.updated_at < datetime.utcnow() - timedelta(minutes=5)):
                        task_id = schedule_preprocess(value.dict())
                        await value.update({"$set": {
                            "nlp_job_id": task_id,
                            "updated_at": datetime.utcnow()
                        }})
                else:
                    task_id = schedule_preprocess(value.dict())
                    await value.update({"$set": {
                            "nlp_job_id": task_id,
                            "updated_at": datetime.utcnow()
                        }})

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
        if ready_for_cluster:
            output["detail_thesis_dict"] = thesis_dict
        output["ready_for_cluster"] = ready_for_cluster
        return WorkerClusterHistory(_id=cluster_history.id,**output)

