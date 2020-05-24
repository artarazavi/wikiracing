from common import config
import logging
from celery import Celery
from kombu import Queue
import redis


def test_config_init():
    assert config.LOGGING_LEVEL == "INFO"
    assert isinstance(config.logger, logging.RootLogger)
    assert config.logger.level == 20
    assert config.REDIS_HOST in ["localhost", "redis"]
    assert config.REDIS_PORT == 6379
    assert config.CELERY_DB_ID == 0
    assert config.STATUS_DB == 1
    assert config.VISITED_DB == 2
    assert config.SCORES_DB == 3
    assert config.TRAVERSED_DB == 4
    assert config.FLUSH_ALL in [True, False]
    assert config.C_FORCE_ROOT
    assert config.REDIS_URL in [
            "redis://redis:6379/0",
            "redis://localhost:6379/0"
        ]


def test_get_celery_app():
    app = config.get_celery_app()
    assert isinstance(app, Celery)
    assert app.conf.broker_url in [
            "redis://redis:6379/0",
            "redis://localhost:6379/0"
        ]
    assert app.conf.result_backend in [
            "redis://redis:6379/0",
            "redis://localhost:6379/0"
        ]
    assert app.conf.task_serializer == "json"
    assert app.conf.result_serializer == "json"
    assert app.conf.accept_content == ["json"]
    assert app.conf.task_default_queue == "default"
    assert len(app.conf.task_queues) == 3
    assert Queue("default", routing_key="task.#") in app.conf.task_queues
    assert Queue("find_task", routing_key="find.#") in app.conf.task_queues
    assert Queue("nlp_task", routing_key="nlp.#") in app.conf.task_queues
    # Need index 0 because of the way task_routes is stored
    assert ("tasks.find.*", {"queue": "find_task"}) in app.conf.task_routes[0]
    assert ("tasks.nlp.*", {"queue": "nlp_task"}) in app.conf.task_routes[0]


def valid_redis_database(redis_db):
    return isinstance(redis_db, redis.StrictRedis) and redis_db.config_get("port") == {'port': '6379'}


def test_get_status_db():
    status_db = config.get_scores_db()
    assert valid_redis_database(status_db)


def test_get_visited_db():
    visited_db = config.get_visited_db()
    assert valid_redis_database(visited_db)


def test_get_scores_db():
    scores_db = config.get_scores_db()
    assert valid_redis_database(scores_db)


def test_get_traversed_db():
    traversed_db = config.get_traversed_db()
    assert valid_redis_database(traversed_db)

