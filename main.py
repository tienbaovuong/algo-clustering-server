from fastapi import FastAPI

from app import database
from app.routers import routers
from app.worker.handler import init_celery
from app.helpers.nlp_preload import nlp_service
from app.helpers.asynchronous import async_wrap
from app.middlewares.limiters import add_limiters
from app.middlewares.exception_handlers import add_exception_handlers
from app.middlewares.cors import apply_cors
from app.settings import AppSettings

app = FastAPI(title="Clustering")

@app.on_event("startup")
async def app_init():
    # Common settings
    app_settings = AppSettings()

    # middleware
    add_limiters(app)
    apply_cors(app, app_settings.allowed_origins)
    add_exception_handlers(app)

    # INIT DATABASE
    await database.initialize()

    # ADD ROUTES
    for router in routers:
        app.include_router(**router)

    # Load nlp model
    await async_wrap(nlp_service.initialize)()

    init_celery()


@app.get("/ping", summary="Health check usage only")
def ping():
    return "PONG!"
