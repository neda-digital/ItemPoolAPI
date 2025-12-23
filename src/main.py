from fastapi import FastAPI
from .controllers import TaskRegistration, TaskRetrieval, TaskCollection
from logging.config import dictConfig
from .Util.logging.logger_config import log_config

dictConfig(log_config)

app = FastAPI()

app.include_router(TaskRegistration.router)
app.include_router(TaskRetrieval.router)
app.include_router(TaskCollection.router)
