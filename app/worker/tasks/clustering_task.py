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
            try:
                history_data = backend.get(
                    f"/internal_api/v1/cluster_history/{history_id}/worker_data"
                )
                history_data.raise_for_status()
                parse_data = history_data.json()
                if parse_data.get("ready_for_cluster"):
                    break
                else:
                    time.sleep(5.0)
            except HTTPStatusError as error:
                time.sleep(5.0)
                continue

        cluster = SSMC_FCM(dataset=parse_data)
        cluster.clustering()
        backend.put(
            f"/interal_api/v1/cluster_history/{history_id}/cluster_result",
            json={
                "data": cluster
            }
        )
        logger.info("Finish cluster, ref_id: %s" % history_id)
    except Exception as error:
        logger.exception(error)
        update_history_data(history_id=history_id, status="FAILED")


def update_history_data(history_id: str, status: str):
    backend.put(
        f"/interal_api/v1/cluster_history/{history_id}/status",
        json={
            "status": status
        }
    )