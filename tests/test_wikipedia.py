from pytest_redis import factories
from common.status import Status
from common.wikipedia import Wikipedia
import pytest
import requests

# gets you MIKE_TYSON_RESPONSE_1 & MIKE_TYSON_RESPONSE_2
from .wikipedia_data import MIKE_TYSON_RESPONSE_1, MIKE_TYSON_RESPONSE_2


redis_proc = factories.redis_proc(host="redis", port=6379, logsdir="/tmp")
redis_mock_status = factories.redisdb("redis_nooproc")


@pytest.fixture()
def wikipedia_cls(redis_mock_status):
    status = Status(redis_mock_status, "root_path", "start_path", "end_path")
    return Wikipedia(status, "start_path")


class ScrapePageMockResponseContinue:
    @staticmethod
    def json():
        return MIKE_TYSON_RESPONSE_1


class ScrapePageMockResponse:
    @staticmethod
    def json():
        return MIKE_TYSON_RESPONSE_2


def test_scrape_page(monkeypatch, wikipedia_cls):
    wikipedia_cls.start_path = "Mike Tyson"
    assert wikipedia_cls.start_path == "Mike Tyson"

    def mock_get(*args, **kwargs):
        if args[1].get("plcontinue"):
            return ScrapePageMockResponse()
        else:
            return ScrapePageMockResponseContinue()

    monkeypatch.setattr(requests, "get", mock_get)
    result = wikipedia_cls.scrape_page()
    assert len(result) == 20
    assert len(wikipedia_cls.links) == 20


class GetRequestMockResponse:
    @staticmethod
    def json():
        result = dict()
        result["mock_key"] = "mock_response"
        return result


def test_get_request(monkeypatch, wikipedia_cls):
    wikipedia_cls.start_path = "Mike Tyson"
    assert wikipedia_cls.start_path == "Mike Tyson"

    def mock_get(*args, **kwargs):
        return GetRequestMockResponse()

    monkeypatch.setattr(requests, "get", mock_get)
    params = wikipedia_cls.build_payload()
    result = wikipedia_cls.get_request(params)
    assert result["mock_key"] == "mock_response"


def test_build_payload_no_response(wikipedia_cls):
    assert wikipedia_cls.build_payload() == {
        "action": "query",
        "titles": "start_path",
        "format": "json",
        "formatversion": "2",
        "prop": "links",
        "pllimit": "max",
    }


def test_build_payload_with_response(wikipedia_cls):
    assert wikipedia_cls.build_payload(MIKE_TYSON_RESPONSE_1) == {
        "action": "query",
        "titles": "start_path",
        "format": "json",
        "formatversion": "2",
        "prop": "links",
        "pllimit": "max",
        "plcontinue": "39027|0|Ahmed_Salim",
    }
