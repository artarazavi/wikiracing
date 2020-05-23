from pytest_redis import factories
from common.history import History
from common.status import Status
from common.nlp import NLP
from nlp import nlp
import pytest

redis_proc = factories.redis_proc(host="redis", port=6379, logsdir='/tmp')
redis_mock_status = factories.redisdb('redis_nooproc', 1)
redis_mock_visited = factories.redisdb('redis_nooproc', 2)
redis_mock_scores = factories.redisdb('redis_nooproc', 3)
redis_mock_traversed = factories.redisdb('redis_nooproc', 4)


@pytest.fixture()
def nlp_cls(redis_mock_status, redis_mock_visited, redis_mock_scores, redis_mock_traversed):
    status = Status(redis_mock_status, "root_path", "start_path", "end_path")
    history = History(status, redis_mock_visited, redis_mock_scores, redis_mock_traversed, "start_path")
    nlp_ini = NLP(status, history)
    return nlp_ini


@pytest.fixture()
def get_celery_app_override(monkeypatch, celery_app):
    from common import nlp
    monkeypatch.setattr(nlp, "app", celery_app)


def test_nlp_score_links(nlp_cls, celery_app, celery_worker, get_celery_app_override):
    nlp_cls.status.end_path = "broccoli"
    celery_app.task(name="tasks.nlp")(nlp.nlp_score)
    links = ["potato", "carrot", "tomato"]
    scored_links = nlp_cls.score_links(links)
    assert scored_links == [["potato", 0.7085011885392024],
                            ["carrot", 0.7561327100917855],
                            ["tomato", 0.7396226929531468]]
