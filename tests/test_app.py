from api.app import create_flask_app
import pytest
from pytest_redis import factories
import pytest_flask
from flask import url_for
import json
from time import sleep
from unittest.mock import patch
from api import app

redis_proc = factories.redis_proc(host="redis", port=6379, logsdir="/tmp")
redis_mock_status = factories.redisdb("redis_nooproc", 1)
redis_mock_visited = factories.redisdb("redis_nooproc", 2)
redis_mock_scores = factories.redisdb("redis_nooproc", 3)
redis_mock_traversed = factories.redisdb("redis_nooproc", 4)


def test_build_root_path():
    assert app.build_root_path("path1", "path2") == "path1-path2"


@pytest.fixture
def flask_app(celery_app, redis_mock_status):
    flask_app = create_flask_app(celery_app, redis_mock_status, {"TESTING": True, "SERVER_NAME": "api"})
    return flask_app


@pytest.fixture
def client(flask_app):
    """A test client for the app."""
    return flask_app.test_client()


def test_find(client, flask_app, redis_mock_status):
    def mock_find(*args, **kwargs):
        redis_mock_status.hset("Mike Tyson-New York City", "active", "done")
        redis_mock_status.hset("Mike Tyson-New York City", "results", json.dumps(["mock1", "mock2"]))
        return None

    with flask_app.app_context():
        url = url_for("find", start_path="Mike Tyson", end_path="New York City")

    assert url == "http://api/find/Mike%20Tyson/New%20York%20City"
    res = client.get(url)
    assert res.data.decode() == "Pending"

    with patch("find.find.find", new_callable=mock_find):
        while res.data.decode() == "Pending":
            sleep(0.5)
            res = client.get(url)
    assert json.loads(res.data.decode()) == ["mock1", "mock2"]


def test_add(client, flask_app):
    with flask_app.app_context():
        assert "status of" in client.get(url_for("add", param1=2, param2=5)).data.decode()


# TODO get rid of this
# left here for use later

# @pytest.fixture()
# def mock_app(monkeypatch, celery_app, redis_mock_status):
#     from api import app
#     monkeypatch.setattr(app, "config_celery_app", celery_app)
#     monkeypatch.setattr(app, "config_status_db", redis_mock_status)
#     return app



# # flaks app
# @pytest.fixture()
# def app(celery_app, redis_mock_status):
#     app = create_flask_app(celery_app, redis_mock_status)
#     return app

# @pytest.fixture()
# def celery_mock_find(
#         monkeypatch,
#         celery_app,
#         redis_mock_status,
#         redis_mock_visited,
#         redis_mock_scores,
#         redis_mock_traversed
# ):
#     from find import find
#     monkeypatch.setattr(find, "app", celery_app)
#     monkeypatch.setattr(find, "status_db", redis_mock_status)
#     monkeypatch.setattr(find, "visited_db", redis_mock_visited)
#     monkeypatch.setattr(find, "scores_db", redis_mock_scores)
#     monkeypatch.setattr(find, "traversed_db", redis_mock_traversed)
#     return find


# @pytest.fixture()
# def celery_mock_nlp(monkeypatch, celery_app):
#     from common import nlp
#     monkeypatch.setattr(nlp, "app", celery_app)
#     return nlp

