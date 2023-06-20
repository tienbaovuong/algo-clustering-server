from typing import Dict
import time

from celery.utils.log import get_task_logger
from httpx import HTTPStatusError

from app.services.clustering_service import SSMC_FCM
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
    try:
        while(True):
            history_data = backend.get(
                f"/internal_api/v1/cluster_history/{history_id}/worker_data"
            )
            history_data.raise_for_status()
            parse_data = history_data.json()
            if parse_data.get("ready_for_cluster"):
                break
            else:
                time.sleep(5.0)

        cluster = SSMC_FCM(dataset=parse_data)
        cluster.clustering()
        cluster_result = backend.put(
            f"/interal_api/v1/cluster_history/{history_id}",
            json={
                "data": cluster
            }
        )
        logger.info("Finish cluster, ref_id: %s" % history_id)
    except HTTPStatusError as error:
        return error.response.json()