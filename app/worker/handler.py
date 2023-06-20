from celery import Celery

from app.settings.app_settings import AppSettings

celery = Celery(__name__)

def init_celery():
    app_settings = AppSettings()
    celery.conf.broker_url = app_settings.celery_broker_url
    celery.conf.result_backend = app_settings.celery_result_backend

    celery.conf.task_routes = {
        "app.worker.tasks.nlp_task.*": {"queue": "nlp"},
        "app.worker.tasks.clustering_task.*": {"queue": "clustering"},
    }

