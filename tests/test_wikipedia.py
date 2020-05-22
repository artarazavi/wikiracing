from pytest_redis import factories
from common.status import Status
from common.wikipedia import Wikipedia
import pytest
import requests

redis_proc = factories.redis_proc(host="redis", port=6379, logsdir='/tmp')
redis_mock_status = factories.redisdb('redis_nooproc')


MIKE_TYSON_RESPONSE_1 = {
    "continue": {
        "plcontinue": "39027|0|Ahmed_Salim",
        "continue": "||"
    },
    "query": {
        "pages": [
            {
                "pageid": 39027,
                "ns": 0,
                "title": "Mike Tyson",
                "links": [
                    {
                        "ns": 0,
                        "title": "1984 Summer Olympics"
                    },
                    {
                        "ns": 0,
                        "title": "20/20 (US television show)"
                    },
                    {
                        "ns": 0,
                        "title": "ABC-CLIO"
                    },
                    {
                        "ns": 0,
                        "title": "ABC Sports"
                    },
                    {
                        "ns": 0,
                        "title": "Aaron Pryor"
                    },
                    {
                        "ns": 0,
                        "title": "About.com"
                    },
                    {
                        "ns": 0,
                        "title": "Adam Walsh Child Protection and Safety Act"
                    },
                    {
                        "ns": 0,
                        "title": "Adonis Stevenson"
                    },
                    {
                        "ns": 0,
                        "title": "Adult Swim"
                    },
                    {
                        "ns": 0,
                        "title": "Adultery"
                    }
                ]
            }
        ]
    }
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
                    {
                        "ns": 0,
                        "title": "Ahmed Salim"
                    },
                    {
                        "ns": 0,
                        "title": "Alan Dershowitz"
                    },
                    {
                        "ns": 0,
                        "title": "Albany, New York"
                    },
                    {
                        "ns": 0,
                        "title": "Alcoholism"
                    },
                    {
                        "ns": 0,
                        "title": "Alex Stewart (boxer)"
                    },
                    {
                        "ns": 0,
                        "title": "Alexander the Great"
                    },
                    {
                        "ns": 0,
                        "title": "Alfonso Ratliff"
                    },
                    {
                        "ns": 0,
                        "title": "Amateur boxing"
                    },
                    {
                        "ns": 0,
                        "title": "American Broadcasting Company"
                    },
                    {
                        "ns": 0,
                        "title": "Andre Ward"
                    }
                ]
            }
        ]
    }
}


@pytest.fixture(scope='function')
@pytest.mark.usefixtures('redis_mock_status')
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


@pytest.mark.usefixtures('wikipedia_cls')
def test_get_request_again(monkeypatch, wikipedia_cls):
    wikipedia_cls.start_path = "Mike Tyson"
    assert wikipedia_cls.start_path == "Mike Tyson"

    def mock_get(*args,  **kwargs):
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


@pytest.mark.usefixtures('wikipedia_cls')
def test_get_request(monkeypatch, wikipedia_cls):
    wikipedia_cls.start_path = "Mike Tyson"
    assert wikipedia_cls.start_path == "Mike Tyson"

    def mock_get(*args,  **kwargs):
        return GetRequestMockResponse()

    monkeypatch.setattr(requests, "get", mock_get)
    params = wikipedia_cls.build_payload()
    result = wikipedia_cls.get_request(params)
    assert result["mock_key"] == "mock_response"


@pytest.mark.usefixtures('wikipedia_cls')
def test_build_payload_no_response(wikipedia_cls):
    assert wikipedia_cls.build_payload() == {
        "action": "query",
        "titles": "start_path",
        "format": "json",
        "formatversion": "2",
        "prop": "links",
        "pllimit": "max",
    }


@pytest.mark.usefixtures('wikipedia_cls')
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
