from os import environ
from celery import Celery
from redis import StrictRedis
import logging
from kombu import Queue

# logging set up to figure out errors before importing anything
LOGGING_LEVEL = environ.get("LOGGING_LEVEL", "INFO")
logger = logging.getLogger()
logger.setLevel(LOGGING_LEVEL)

# gather environment variables
REDIS_HOST = environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(environ.get("REDIS_PORT", 6379))
CELERY_DB_ID = int(environ.get("CELERY_DB", 0))

STATUS_DB = int(environ.get("STATUS_DB", 1))
VISITED_DB = int(environ.get("VISITED_DB", 2))
SCORES_DB = int(environ.get("SCORES_DB", 3))
TRAVERSED_DB = int(environ.get("TRAVERSED_DB", 4))

FLUSH_ALL = True if environ.get("FLUSH_ALL", "False").lower() == "true" else False
C_FORCE_ROOT = True if environ.get("C_FORCE_ROOT", "True").lower() == "true" else False

REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{CELERY_DB_ID}"


# celery setup
def get_celery_app(celery_app_name="tasks", redis_url=REDIS_URL):
    celery_app = Celery(celery_app_name, broker=redis_url, backend=redis_url)
    celery_app.conf.update(
        {
            "task_serializer": "json",
            "result_serializer": "json",
            "accept_content": ["json"],
        }
    )
    celery_app.conf.task_default_queue = "default"

    celery_app.conf.task_queues = (
        Queue("default", routing_key="task.#"),
        Queue("find_task", routing_key="find.#"),
        Queue("nlp_task", routing_key="nlp.#"),
    )

    # setup queues
    celery_app.conf.task_routes = (
        [
            ("tasks.find.*", {"queue": "find_task"}),
            ("tasks.nlp.*", {"queue": "nlp_task"}),
        ],
    )
    return celery_app


# Redis tables setup
def get_status_db():
    return StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=STATUS_DB)


def get_visited_db():
    return StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=VISITED_DB)


def get_scores_db():
    return StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=SCORES_DB)


def get_traversed_db():
    return StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=TRAVERSED_DB)


# if flush set
if FLUSH_ALL:
    get_scores_db().flushall()
