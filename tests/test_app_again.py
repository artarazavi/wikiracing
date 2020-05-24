from api.app import create_app
import pytest
from pytest_redis import factories
import pytest_flask
import json
from flask import url_for


redis_proc = factories.redis_proc(host="redis", port=6379, logsdir="/tmp")
redis_mock_status = factories.redisdb("redis_nooproc", 1)


@pytest.fixture()
def app(celery_app, redis_mock_status):
    app = create_app(celery_app, redis_mock_status)
    return app


def test_something(client):
    assert "status of" in client.get(url_for("add", param1=2, param2=5)).data.decode()
