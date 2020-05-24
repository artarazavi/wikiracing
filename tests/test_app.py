# import pytest
#
# from flask import Response, url_for
# #from api import app
# from api.app import create_app
# from pytest_flask import fixtures, plugin
# import pytest
# import re
# from pytest_redis import factories
#
# redis_proc = factories.redis_proc(host="redis", port=6379, logsdir='/tmp')
# redis_mock_status = factories.redisdb('redis_nooproc', 1)
#
# class MyResponse(Response):
#     '''Implements custom deserialization method for response objects.'''
#
#     @property
#     def json(self):
#         '''What is the meaning of life, the universe and everything?'''
#         return 42
#
#     @property
#     def data(self):
#         return 42
#
#
#
#
#
#
#
# # @pytest.fixture()
# # def get_celery_app_override(monkeypatch, celery_app, redis_mock_status):
# #     from api import app
# #     monkeypatch.setattr(app, "app", celery_app)
# #     monkeypatch.setattr(app, "status_db", redis_mock_status)
#
# @pytest.fixture
# def flask_app(celery_app, redis_mock_status):
#     flask_app = create_app(celery_app, redis_mock_status, {"TESTING":True, "SERVER_NAME":"api"})
#     flask_app.response_class = MyResponse
#     return flask_app
#
# @pytest.fixture
# def client(flask_app):
#     """A test client for the app."""
#     return flask_app.test_client()
#
#
# class TestFlask:
#     def test_my_json_response(self, flask_app, client, celery_app, celery_worker):
#         with flask_app.app_context():
#             url = url_for("add", param1=4, param2=4, _external=False)
#
#         res = client.get(url)
#         response_text = next(res.response).decode()
#         task_id_re = re.compile(r"<a href='(?P<task_url>/check/[a-z0-9\-]+)")
#         task_url = task_id_re.match(response_text).group("task_url")
#
#         status = "PENDING"
#         while status == "PENDING":
#             res = client.get(task_url)
#             status = next(res.response).decode()
#
#         assert status == "8"
#
#
# # class TestMul:
# #     def test_success(self, celery_app, celery_worker):
# #         mul = celery_app.task(bind=True, name="tasks.mul")(app.mul)
# #         assert mul.delay(4, 4).get(timeout=10) == 16
#
#
# # def test_build_root_path(client):
# #     assert client.build_root_path("path1", "path2") == "path1-path2"
#
