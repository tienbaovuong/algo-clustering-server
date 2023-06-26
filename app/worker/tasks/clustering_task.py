import time
import math

from celery.utils.log import get_task_logger
from httpx import HTTPStatusError

from app.worker.handler import celery
from app.worker.adapters import backend

logger = get_task_logger(__name__)


def schedule_clustering(history_id) -> str:
    task = cluster_thesis.delay(history_id)
    logger.info("Created a celery task id=%s" % task.id)
    return task.id


@celery.task(
    rate_limit="1/m",
    time_limit=600,
)
def cluster_thesis(history_id: str):
    logger.info(backend.base_url)
    try:
        update_history_data(history_id=history_id, status="WAITING_NLP")
        while(True):
            try:
                history_data = backend.get(
                    f"/internal_api/v1/cluster_history/{history_id}/worker_data"
                )
                if history_data.status_code == 404:
                    return
                history_data.raise_for_status()
                parse_data = history_data.json().get("data")
                if parse_data.get("ready_for_cluster"):
                    break
                else:
                    time.sleep(2.0)
            except HTTPStatusError as error:
                time.sleep(2.0)
                continue

        result_data = []
        thesis_list = parse_data.get("non_clustered_thesis")
        min_size = math.floor(len(thesis_list) / 3)
        cluster_1 = {
            "name": "Cluster 1",
            "children": thesis_list[:min_size]
        }
        cluster_2 = {
            "name": "Cluster 2",
            "children": thesis_list[min_size : min_size * 2]
        }
        cluster_3 = {
            "name": "Cluster 3",
            "children": thesis_list[min_size * 2:]
        }
        result_data.append(cluster_1)
        result_data.append(cluster_2)
        result_data.append(cluster_3)
        res = backend.put(
            f"/internal_api/v1/cluster_history/{history_id}/cluster_result",
            json={
                "cluster_result": result_data
            }
        )
        res.raise_for_status()
        logger.info("Finish cluster, ref_id: %s" % history_id)
    except Exception as error:
        logger.exception(error)
        update_history_data(history_id=history_id, status="FAILED")


def update_history_data(history_id: str, status: str):
    backend.put(
        f"/internal_api/v1/cluster_history/{history_id}/status",
        json={
            "status": status
        }
    )