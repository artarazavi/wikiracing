import pytest
import redis.connection


def _redis_Connection_del(*args, **kwargs):
    return


redis.connection.Connection.__del__ = _redis_Connection_del


@pytest.fixture(scope="session")
def celery_worker_parameters():
    return {
        "queues": ("default", "find_task", "nlp_task", "celery", "nlp", "find"),
    }
