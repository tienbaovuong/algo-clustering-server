from typing import Dict

from celery.utils.log import get_task_logger
from celery.exceptions import TimeLimitExceeded
from httpx import HTTPStatusError

from app.helpers.nlp_preload import nlp_service
from app.worker.handler import celery
from app.worker.adapters import backend

logger = get_task_logger(__name__)


def schedule_preprocess(thesis: Dict) -> str:
    task = preprocess_thesis.delay(thesis)
    logger.info("Created a celery task id=%s" % task.id)
    return task.id


@celery.task(
    bind=True,
    max_retries=3,
    rate_limit="50/s",
    time_limit=60
)
def preprocess_thesis(self,thesis: Dict):
    try:
        input_line = [
            thesis.get("title", ""),
            thesis.get("category", ""),
            thesis.get("expected_result", ""),
            thesis.get("problem_solve", "")
        ]
        output_features = nlp_service.extract_feature(input_line)
        try:
            thesis_id = thesis.get('_id')
            if not thesis_id:
                thesis_id = thesis.get('id')
            res = backend.put(
                f"/internal_api/v1/thesis_data/{thesis_id}/update_nlp",
                json={
                    "title_vector": output_features[0],
                    "category_vector": output_features[1],
                    "expected_result": output_features[2],
                    "problem_solve": output_features[3]
                },
            )
            res.raise_for_status()
            logger.info("Processed: %s" % thesis.get("title"))
            return res.json()
        except HTTPStatusError as error:
            return error.response.json()
    except TimeLimitExceeded:
        return
    except Exception as ex:
        logger.exception(ex)
        self.retry(countdown=5)