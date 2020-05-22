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
REDIS_PORT = environ.get("REDIS_PORT", 6379)
CELERY_DB_ID = environ.get("CELERY_DB", 0)

STATUS_DB = environ.get("STATUS_DB", 1)
VISITED_DB = environ.get("VISITED_DB", 2)
SCORES_DB = environ.get("SCORES_DB", 3)
TRAVERSED_DB = environ.get("TRAVERSED_DB", 4)

FLUSH_ALL = environ.get("FLUSH_ALL")
C_FORCE_ROOT = environ.get("C_FORCE_ROOT")

REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{CELERY_DB_ID}"


# celery setup
def get_celery_app(celery_app_name="tasks", redis_url=REDIS_URL):
    app = Celery("tasks", broker=redis_url, backend=redis_url)
    app.conf.update(
        {"task_serializer": "json", "result_serializer": "json", "accept_content": ["json"]}
    )

    # setup queues
    task_routes = (
        [
            ("tasks.find.*", {"queue": "find"}),
            ("tasks.nlp.*", {"queue": "nlp"}),
        ],
    )

    app.conf.task_queues = (
        Queue('default',    routing_key='task.#'),
        Queue('find_task', routing_key='find.#'),
        Queue('nlp_task', routing_key='nlp.#'),
    )
    return app


# Redis tables setup
def get_status_db():
    return StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=STATUS_DB)


visited_db = StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=VISITED_DB)
scores_db = StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=SCORES_DB)
traversed_db = StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=TRAVERSED_DB)


# if flush set
if FLUSH_ALL:
    scores_db.flushall()
