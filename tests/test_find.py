# from pytest_redis import factories
# from pytest_redis.plugin import redisdb
# import celery
# from find.find import add
# from celery import signature
# redis_mock = factories.redisdb('redis_nooproc')
# redis_proc = factories.redis_proc(host="localhost", port=6379, logsdir='/tmp', executable="/usr/local/bin/redis-server")
# from unittest.mock import patch
# from unittest import TestCase
# import pytest
# #from find.find import app
# from common.config import get_celery_app
# app = get_celery_app()
# from celery.contrib.testing.worker import start_worker
# from celery import Celery
#
# from common.history import History
# from common.status import Status
#
# redis_mock1 = factories.redisdb('redis_nooproc', 1)
# redis_mock2 = factories.redisdb('redis_nooproc', 2)
# redis_mock3 = factories.redisdb('redis_nooproc', 3)
# redis_mock4 = factories.redisdb('redis_nooproc', 4)
#
#
# class MockStatus:
#     def __init__(self, db, r, s, e):
#         print("MockStatus Init")
#         self = Status(redis_mock4, r, s, e)
#
# class MockHistory:
#     def __init__(self,status, db1,db2,db3, s, t):
#         print("MockHistory Init")
#         self = History(status, redis_mock1, redis_mock2, redis_mock3, s, t)
#
#
#
# #@pytest.mark.usefixtures('celery_session_app')
# @celery.task(name="tasks.add", bind=True)
# def mock_add(self, a=0,b=0):
#     return a+b
#
# from celery.contrib.testing.app import TestApp
#
# @pytest.fixture(scope='session')
# @patch("find.find.add")
# @patch("common.status.Status")
# @patch("common.history.History")
# def celery_app(mock_add, MockStatus, MockHistory):
#     #celery_app = app
#     celery_app = TestApp("tasks") #, set_as_current=True, backend='redis://localhost:6379/0', broker='redis://localhost:6379/0')
#     #elery_app = Celery("tasks", backend=redis_mock, broker=redis_mock)
#     celery_app.conf.update(CELERY_ALWAYS_EAGER=True)
#     #print(celery.backend)
#     #celery.tasks["tasks.add"] = mock_add
#     from celery.contrib.testing import tasks
#     #celery_session_app.conf = celery.conf
#     celery_app.backend
#     #celery.Task =
#     # celery_session_app.backend = celery.backend
#     # celery_session_app.backend_cls = celery.backend_cls
#
#     yield celery_app
#
# #
# # @pytest.fixture(scope='session')
# # def celery_config():
# #     return {
# #         'broker_url': 'memory://',
# #         'result_backend': 'redis://'
# #     }
#
# #@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
# @patch('find.find.add')
# @patch("common.status.Status")
# @patch("common.history.History")
# @patch('find.find.app')
# @pytest.mark.usefixtures('celery_app')
# @pytest.mark.usefixtures('celery_session_worker')
# def test_celery_add(mock_add, MockStatus, MockHistory, celery_app, celery_session_worker):
#
#
#     #celery_session_app.events.autoadd_celery_args = True
#     #app = next(celery_session_app)
#     print(celery_app.tasks.__dict__)
#     #print('settinf alse')
#     # import pdb; pdb.set_trace()
#     #celery.signals.task_prerun.send(sender='foo', task=add,
#     #    args=[1, 2])
#     #celery.signals.task_postrun.send(sender='foo')
#     r = add.apply_async((2,2))
#     #print(f"Worker: {celery_session_worker.__dict__}")
#     #r = add.delay(4,4)
#     #r = celery_app.send_task("tasks.find", (4,4))
#     print(r.__dict__)
#     print(celery_app.tasks.__dict__)
#     print(r.get())
#     mock_add.assert_called_with(4, 4)
#     #print(celery_session_app.tasks)
#     assert 1==3
#
# # @pytest.mark.usefixtures('celery_session_app')
# # @celery.task(name="tasks.add", bind=True)
# # def add_mock(self, a,b):
# #     return a+b
#
# # @pytest.fixture(scope="session")
# # @pytest.mark.usefixtures('celery_session_app')
# # @celery_session_app.task(name="tasks.add", bind=True)
# # def add_mock(self, a,b):
# #     return a+b
#
# # @pytest.mark.celery(result_backend="redis://localhost:6379/0", brokeer_url="redis://localhost:6379/0")
# # class TestFind:
#     # @pytest.mark.usefixtures('celery_session_app')
#     # @celery.task(name="tasks.add", bind=True)
#     # def add_mock(self, a, b):
#     #     return a + b
#
#     # @pytest.mark.celery(result_backend="redis://localhost:6379/0", brokeer_url="redis://localhost:6379/0")
#     # @patch('find.find.add')
#     # @pytest.mark.usefixtures('celery_app')
#     # def test_celery_app(self, add_mock, celery_app):
#     #     app = next(celery_app)
#     #     print(app.tasks)
#     #
#     #     #app.tasks["tasks.add"] = add_mock
#     #
#     #     #r = celery_session_app.send_task("tasks.add", args=(4,4))
#     #     #r = signature("tasks.add", args=(4,4)).apply_async()
#     #
#     #     r = app.send_task("tasks.add", queue="find", args=(None, 4,4))
#     #     #r = add_mock.s(4,4)
#     #     #r = add.apply_async((4, 4))
#     #     #print(r.get())
#     #     #s = signature("tasks.add")
#     #     final = r.get()
#     #     add_mock.assert_called_with(4,4)
#     #     #print(add_mock.__dict__)
#     #     assert final == 8
#
#
# #
# # def add_mock(self, a, b):
# #     return a+b
# #
# # #@pytest.mark.usefixtures('celery_worker')
# # #@pytest.mark.usefixtures('celery_session_worker')
# # #@pytest.mark.celery(result_backend="redis://localhost:6379/0", brokeer_url="redis://localhost:6379/0")
# # class TestAdd(TestCase):
# #     def setUp(self):
# #         app.conf['TESTING'] = True
# #
# #     @patch("find.find.add")
# #     def test_add(self, add_mock):
# #         add.delay(self, 4, 4)
# #         add.assert_called_with(4, 4)
#
# # @pytest.mark.usefixtures('celery_app')
# # @celery_app.task(name='add')
# # def add(a, b):
# #     return a, b
# #
# #
# # def test_create_task(celery_app, celery_worker):
# #     @celery_app.task
# #     def add(x, y):
# #         return x * y
# #
# #     assert find.delay(4, 4).get() == 8
#
# # @patch('find.find.add')
# # @celery_app.task()
# # def test_add(celery_app):
# #     result = add.delay(4,4)
# #     result.ready()
# #     celery_app.assert_called_with(4,3)
#
