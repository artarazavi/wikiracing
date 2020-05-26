import json
from time import sleep
from unittest.mock import patch

import pytest
import pytest_flask
from flask import url_for
from pytest_redis import factories
from common import config

from api import app
from api.app import create_flask_app

redis_proc = factories.redis_proc(host="redis", port=6379, logsdir="/tmp")
redis_mock_status = factories.redisdb("redis_nooproc", 1)
redis_mock_visited = factories.redisdb("redis_nooproc", 2)
redis_mock_scores = factories.redisdb("redis_nooproc", 3)
redis_mock_traversed = factories.redisdb("redis_nooproc", 4)


def test_build_root_path():
    assert app.build_root_path("path1", "path2") == "path1-path2"


@pytest.fixture
def flask_app(celery_app, redis_mock_status):
    flask_app = create_flask_app(
        celery_app, redis_mock_status, {"TESTING": True, "SERVER_NAME": "api"}
    )
    return flask_app


@pytest.fixture
def client(flask_app):
    """A test client for the app."""
    return flask_app.test_client()


def test_find(client, flask_app, redis_mock_status):
    def mock_find(*args, **kwargs):
        redis_mock_status.hset("Mike Tyson-New York City", "active", "done")
        redis_mock_status.hset(
            "Mike Tyson-New York City", "results", json.dumps(["mock1", "mock2"])
        )
        redis_mock_status.hset("Mike Tyson-New York City", "end_time", 20.5)
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
    assert (
        res.data.decode() == 'solution is: ["mock1", "mock2"] time spent: 20.5 seconds'
    )
