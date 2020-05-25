import json
from time import sleep
from unittest.mock import patch

import pytest
import requests
import celery
from pytest_redis import factories

from common.history import History
from common.nlp import NLP
from common.status import Status
from find import find

MIKE_TYSON_RESPONSE_1 = {
    "continue": {"plcontinue": "39027|0|Ahmed_Salim", "continue": "||"},
    "query": {
        "pages": [
            {
                "pageid": 39027,
                "ns": 0,
                "title": "Mike Tyson",
                "links": [
                    {"ns": 0, "title": "Adult Swim"},
                    {"ns": 0, "title": "Adultery"},
                ],
            }
        ]
    },
}


MIKE_TYSON_RESPONSE_2 = {
    "batchcomplete": True,
    "query": {
        "pages": [
            {
                "pageid": 39027,
                "ns": 0,
                "title": "Mike Tyson",
                "links": [
                    {"ns": 0, "title": "Albany, New York"},
                    {"ns": 0, "title": "Alcoholism"},
                ],
            }
        ]
    },
}


redis_proc = factories.redis_proc(host="redis", port=6379, logsdir="/tmp")
redis_mock_status = factories.redisdb("redis_nooproc", 1)
redis_mock_visited = factories.redisdb("redis_nooproc", 2)
redis_mock_scores = factories.redisdb("redis_nooproc", 3)
redis_mock_traversed = factories.redisdb("redis_nooproc", 4)


@pytest.fixture()
def celery_mock_find(
        monkeypatch,
        celery_app,
        redis_mock_status,
        redis_mock_visited,
        redis_mock_scores,
        redis_mock_traversed
):
    monkeypatch.setattr(find, "app", celery_app)
    monkeypatch.setattr(find, "status_db", redis_mock_status)
    monkeypatch.setattr(find, "visited_db", redis_mock_visited)
    monkeypatch.setattr(find, "scores_db", redis_mock_scores)
    monkeypatch.setattr(find, "traversed_db", redis_mock_traversed)


@pytest.fixture()
def status_cls(redis_mock_status):
    return Status(redis_mock_status, "Mike Tyson-Albany, New York", "Mike Tyson", "Albany, New York")


@pytest.fixture()
def history_cls(
    redis_mock_status, redis_mock_visited, redis_mock_scores, redis_mock_traversed
):
    status = Status(redis_mock_status, "Mike Tyson-Albany, New York", "Mike Tyson", "Albany, New York")
    history = History(
        status,
        redis_mock_visited,
        redis_mock_scores,
        redis_mock_traversed,
        "Mike Tyson",
    )
    return history


class ScrapePageMockResponseContinue:
    @staticmethod
    def json():
        return MIKE_TYSON_RESPONSE_1


class ScrapePageMockResponse:
    @staticmethod
    def json():
        return MIKE_TYSON_RESPONSE_2


def mock_get(*args, **kwargs):
    if args[1].get("plcontinue"):
        return ScrapePageMockResponse()
    else:
        return ScrapePageMockResponseContinue()


def test_find_on_first_page(celery_app, monkeypatch, celery_worker, celery_mock_find, status_cls):
    monkeypatch.setattr(requests, "get", mock_get)
    find.find("Mike Tyson-Albany, New York", "Mike Tyson")
    sleep(5)
    assert status_cls.results_str() == json.dumps(["Mike Tyson", "Albany, New York"])


class MockNLP(NLP):
    def score_links(self, all_links):
        return [["Adultery", 0.5], ["Adult Swim", 0.9], ["Adult Movie", 0.7]]


def test_find_not_on_first_page(celery_app, celery_worker, monkeypatch,  celery_mock_find, history_cls):

    def mock_apply_async(*args, **kwargs):
        return

    def mock_send_task(*args, **kwargs):
        return mock_apply_async

    monkeypatch.setattr(requests, "get", mock_get)
    monkeypatch.setattr(celery_app, "send_task", mock_send_task)

    status_cls.end_path = "New York"
    with patch("find.find.app.send_task", new_callable=mock_send_task):
        monkeypatch.setattr(find, "NLP", MockNLP)
        history_cls.status.end_path = "New York"
        find.find("Mike Tyson-Albany, New York", "Mike Tyson")
        assert history_cls.status.results_str() == "None"
        assert history_cls.status.results_pending()
        assert history_cls.scores == [(b'Adultery', 0.5), (b'Adult Movie', 0.7)]


def test_found_in_page(history_cls):
    history_cls.traversed_path = ["some_start_path", "some_other_path"]
    all_links = ["Albany, New York", "Boston", "cat"]
    assert find.found_in_page(history_cls.status, history_cls, all_links)
    assert history_cls.status.results_str() == json.dumps(["some_start_path", "some_other_path", "Albany, New York"])
    assert not history_cls.status.is_active()


def test_not_found_in_page(history_cls):
    history_cls.traversed_path = ["some_start_path", "some_other_path"]
    all_links = ["New York", "Boston", "cat"]
    assert not find.found_in_page(history_cls.status, history_cls, all_links)
    assert history_cls.status.results_str() == "None"
    assert history_cls.status.is_active()