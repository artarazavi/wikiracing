# from celery.contrib.testing import app
import pytest
import pytest_redis
from pytest_redis import port, plugin, factories
#from find.find import add
from common.config import get_celery_app

import celery
from unittest.mock import patch
redis_mock = factories.redisdb('redis_nooproc')
redis_proc = factories.redis_proc(host="localhost", port=6379, logsdir='/tmp')
from celery.contrib.testing.app import TestApp

from kombu import Queue

# @celery.task(name="tasks.add", bind=True)
# def add_mock(self, a,b):
#     return a+b

from unittest.mock import MagicMock


@pytest.fixture(scope='session')
def celery_session_app(celery_session_app):
    # app = get_celery_app("tasks", 'redis://localhost:6379/0')
    app = TestApp("tasks", backend='redis://localhost:6379/0', broker='redis://localhost:6379/0')
    # celery.tasks["tasks.add"] = MagicMock(return_value=10)
    from celery.contrib.testing import tasks
    #celery.conf = celery.conf
    app.Task = celery.Task
    # app.conf.task_queues = (
    #     Queue('default', routing_key='task.#'),
    #     Queue('find_task', routing_key='find.#'),
    #     Queue('nlp_task', routing_key='nlp.#'),
    # )

    yield app

# @pytest.fixture(scope='session')
# def celery_config(celery_config):
#     #print(plugin.pytest_addoption(""))
#     return {
#         'broker_url': 'redis://localhost:6379/0',
#         'result_backend': 'redis://localhost:6379/0',
#         'TESTING': True
#     }

# @pytest.fixture(scope="session")
# def celery():
#     return