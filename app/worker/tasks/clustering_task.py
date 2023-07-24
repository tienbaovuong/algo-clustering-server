import time
import math

from celery.utils.log import get_task_logger
from httpx import HTTPStatusError

from app.worker.handler import celery
from app.worker.adapters import backend
from app.worker.thesis_cluster_class import ThesisClusterObject, ThesisClusterService
from app.helpers.cluster.clustering_helper import ClusteringAlgorithm


logger = get_task_logger(__name__)
field_weights = [8, 4, 2, 1]


def schedule_clustering(history_id) -> str:
    task = cluster_thesis.delay(history_id)
    logger.info("Created a celery task id=%s" % task.id)
    return task.id


@celery.task(
    rate_limit="1/m",
    time_limit=1200,
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

        config = parse_data.get("config")
        thesis_list = parse_data.get("non_clustered_thesis")
        detail_thesis_dict = parse_data.get("detail_thesis_dict")

        service = ThesisClusterService(
            field_weights=get_field_weights(config.get("order")),
            field_balance_multipliers=get_field_balance(detail_thesis_dict)
        )
        algo_instance = ClusteringAlgorithm(
            dataset=get_data_sets(thesis_list, detail_thesis_dict),
            model=service,
            n_clusters=config.get("number_of_clusters"),
            max_size_cluster=config.get("max_item_each_cluster")
        )

        # Cluster loop
        for result_label, loss_values in algo_instance.clustering():
            result_data = []
            for index, result in enumerate(result_label):
                if len(result) == 0:
                    continue
                children = []
                for item in result:
                    children.append(item)
                new_cluster = {
                    "name": f"Cluster {index + 1}",
                    "children": children
                }
                result_data.append(new_cluster)

            res = backend.put(
                f"/internal_api/v1/cluster_history/{history_id}/cluster_result",
                json={
                    "cluster_result": result_data,
                    "loss_values": loss_values
                }
            )
            res.raise_for_status()
            time.sleep(1)

        update_history_data(history_id=history_id, status="FINISHED")
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

def get_field_weights(input: list):
    result = []
    for i in input:
        result.append(field_weights[i])
    return result

def get_field_balance(input: list):
    title_balance = 1
    category_balance = 1
    expected_balance = 1
    problem_balance = 1

    return [title_balance, category_balance, expected_balance, problem_balance]

def get_data_sets(input_list: list, input_dict: dict):
    result = []
    for item in input_list:
        thesis_id = item.get("thesis_id")
        related_thesis = input_dict.get(thesis_id)
        data = ThesisClusterObject(
            title_vector=related_thesis.get("title_vector"),
            category_vector=related_thesis.get("category_vector"),
            expected_result_vector=related_thesis.get("expected_result_vector"),
            problem_solve_vector=related_thesis.get("problem_solve_vector")
        )
        result.append(data)
    return result