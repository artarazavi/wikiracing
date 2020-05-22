# from find.find import add
# from unittest.mock import patch
#
# from pytest_redis import factories
# from pytest_redis.plugin import redisdb
# import celery
# from find.find import add, find
# from celery import signature
#
# redis_mock = factories.redisdb("redis-nooproc")
# redis_proc = factories.redis_proc(host="localhost", port=6379, logsdir='/tmp')
# from celery.canvas import signature
# from unittest.mock import patch
# from unittest import TestCase
# import pytest
# #from find.find import get
# from common.config import get_celery_app
# from celery.contrib.testing.worker import start_worker
# from celery import Celery
# from common.config import get_status_db, scores_db, visited_db, traversed_db
# from common import config
# from common.history import History
# from common.status import Status
#
#
# mock_status_db = factories.redisdb('redis-nooproc', 1)
#
# @pytest.mark.usefixtures('mock_status_db')
# def mock_get_status_db(mock_status_db):
#     print("MOCKING STATUS DB")
#     return mock_status_db
#
# @pytest.mark.usefixtures('celery_session_app')
# def mock_get_app(celery_session_app):
#     return celery_session_app
#
# # @patch("config.status_db", new_callable=factories.redisdb('redis_nooproc', 1))
#
# status_db = factories.redisdb('redis_nooproc', 1)
# # scores_db = factories.redisdb('redis_nooproc', 2)
# # visited_db = factories.redisdb('redis_nooproc', 3)
# # traversed_db = factories.redisdb('redis_nooproc', 4)
#
#
#
#
# # print(factories.get_config(app.conf.defaults))
# @patch("common.status.Status")
# class MockStatus:
#     def __init__(self, db, r, s, e):
#         print("MockStatus Init")
#         self = Status(config.get_status_db(), r, s, e)
#
# @patch("common.history.History")
# class MockHistory:
#     def __init__(self, status, db1, db2, db3, s, t):
#         print("MockHistory Init")
#         self = History(status, visited_db, scores_db, traversed_db, s, t)
#
#
# # c_app = get_celery_app()
# # @c_app.task(name="tasks.find", bind=True)
# # def find(self, a=0, b=0):
# #     print("mock_add")
# #     return a + b
#
#
# from unittest.mock import MagicMock
#
# from celery.task import Task  #
#
# import json
# from common.wikipedia import Wikipedia
#
# class MockWiki:
#     @property
#     def links(self):
#         return ["Airplane", "CNN"]
#
#
# @patch("common.config.get_status_db")
# @patch("common.config.get_celery_app")
# @patch("find.find.find.apply_async")  # , new_callable=mock_add, create=True)
# @pytest.mark.usefixtures('celery_session_app')
# @pytest.mark.usefixtures('celery_session_worker')
# @pytest.mark.usefixtures('status_db')
# @pytest.mark.usefixtures('scores_db')
# @pytest.mark.usefixtures('visited_db')
# @pytest.mark.usefixtures('traversed_db')
# @patch("common.wikipedia.Wikipedia")
# #@patch("common.config.status_db")
# #@patch("common.config.scores_db")
# #@patch("common.config.visited_db")
# #@patch("common.config.traversed_db")
# def test_create_task(mock_get_status_db, mock_get_app,mock_add, celery_session_app, celery_session_worker,
#                       status_db, scores_db, visited_db, traversed_db, monkeypatch):
#
#     def mock_links(*args, **kwargs):
#         return ["Airplane", "CNN"]
#
#     # app = get_celery_app()
#     monkeypatch.setattr(Wikipedia, "links", mock_links)
#     #monkeypatch.setattr(config, "status_db", factories.redisdb('redis_nooproc', 1))
#
#     s = Status(status_db, "rp", "Dynamic IP", "Computer")
#     print(s.end_path)
#
#     task = celery_session_app.send_task(
#         "tasks.find",
#         kwargs=dict(
#             root_path="rp",
#             start_path="Dynamic IP",
#         ),
#         queue='find'
#     )
#
#
#     s.task_id = str(task)
#     assert s.task_id == str(task)
#     assert s.end_path == "Computer"
#
#
#     ft = find.delay(args=("rp","Dynamic IP"), queue="find")
#     # config.scores_db = scores_db
#     # config.status_db = config.get_status_db()
#     # config.visited_db = visited_db
#     # config.traversed_db = traversed_db
#     #celery_session_worker(celery_session_app)
#     #ft = find.delay("rp", "s", queue="find")
#
#     #start_worker(celery_session_app.tasks)
#     s = celery_session_app.send_task("tasks.find", args=("rp","Computer"), queue="find")
#     #ft.get()
#     from time import sleep
#     sleep(1)
#
#
#     #monkeypatch.setattr(Wikipedia, "links", links)
#
#
#     #ft.get()
#
#     print(s.app.__dict__)
#
#     # r.get = MagicMock(return_value=8)
#     # assert r.get() == 8
#     # mock_add.assert_called_with(("rp", "s"), {})
#
#     h = History(Status(config.get_status_db(), "rp", "Dynamic IP", "Computer"), config.visited_db, config.scores_db, config.traversed_db, "Dynamic IP", [])
#     # h.add_to_visited("blah")
#     # assert h.is_visited("blah") is True
#     # h.traversed_path = ["blah"]
#     # print(h.traversed_path)
#     # assert h.status.is_active()
#     # assert 1 == 1
#     # assert h.traversed_path == ["blah"]
#     # h.status.set_no_longer_active()
#     # assert h.status.is_active() is False
#     #
#     # h.add_to_scores(0.43, "msn.com")
#     # h.add_to_scores(0.21, "cnn.com")
#     # print(h.scores)
#     # assert h.status.is_active() is False
#     # assert h.scores == [(b'cnn.com', 0.21), (b'msn.com', 0.43)]
