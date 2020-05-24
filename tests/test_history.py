from pytest_redis import factories
from common.history import History
from common.status import Status
import pytest

redis_proc = factories.redis_proc(host="redis", port=6379, logsdir="/tmp")
redis_mock_status = factories.redisdb("redis_nooproc", 1)
redis_mock_visited = factories.redisdb("redis_nooproc", 2)
redis_mock_scores = factories.redisdb("redis_nooproc", 3)
redis_mock_traversed = factories.redisdb("redis_nooproc", 4)


@pytest.fixture()
def history_cls(
    redis_mock_status, redis_mock_visited, redis_mock_scores, redis_mock_traversed
):
    status = Status(redis_mock_status, "root_path", "start_path", "end_path")
    history = History(
        status,
        redis_mock_visited,
        redis_mock_scores,
        redis_mock_traversed,
        "start_path",
    )
    return history


def test_history_init(
    redis_mock_status, redis_mock_visited, redis_mock_scores, redis_mock_traversed
):
    status = Status(redis_mock_status, "root_path", "start_path", "end_path")
    history = History(
        status,
        redis_mock_visited,
        redis_mock_scores,
        redis_mock_traversed,
        "start_path",
    )
    assert isinstance(history.status, Status)
    assert history.status == history.status
    assert history.redis_client_visited == redis_mock_visited
    assert history.redis_client_scores == redis_mock_scores
    assert history.redis_client_traversed == redis_mock_traversed
    assert history.start_path == "start_path"
    assert history.scores == []


def test_is_visited(history_cls):
    assert history_cls.visited == set()
    assert history_cls.is_visited("some_path") is False
    history_cls.add_to_visited("some_path")
    assert history_cls.is_visited("some_path") is True


def test_history_add_to_visited(history_cls):
    assert history_cls.visited == set()
    history_cls.add_to_visited("path")
    assert history_cls.visited == {b"path"}


def test_history_add_to_score(history_cls):
    assert history_cls.scores == list()
    history_cls.add_to_scores(0.7, "link1")
    assert history_cls.scores == [(b"link1", 0.7)]
    history_cls.add_to_scores(0.9, "link2")
    assert history_cls.scores == [(b"link1", 0.7), (b"link2", 0.9)]


def test_history_bulk_add_to_score(history_cls):
    assert history_cls.scores == list()
    history_cls.bulk_add_to_scores([["path1", 0.7], ["path2", 0.9], ["path3", 0.1]])
    assert history_cls.scores == [(b"path3", 0.1), (b"path1", 0.7), (b"path2", 0.9)]


def test_history_next_highest_score(history_cls):
    assert history_cls.scores == list()
    history_cls.bulk_add_to_scores([["path1", 0.7], ["path2", 0.9], ["path3", 0.1]])
    assert history_cls.scores == [(b"path3", 0.1), (b"path1", 0.7), (b"path2", 0.9)]
    assert history_cls.next_highest_score() == "path2"


def test_set_traversed_path(history_cls):
    assert history_cls.traversed_path == []
    history_cls.traversed_path = ["path4", "path5", "path6"]
    assert history_cls.traversed_path == ["path4", "path5", "path6"]


def test_new_links_set_get_traversed_path(history_cls):
    assert history_cls.traversed_path == []
    history_cls.traversed_path = ["path4", "path5", "path6"]
    history_cls.new_links_set_traversed_path("path7")
    assert history_cls.get_new_links_traversed_path("path7") == [
        "path4",
        "path5",
        "path6",
        "path7",
    ]


def test_bulk_add_to_new_links_traversed_paths(history_cls):
    new_links = ["path4", "path5", "path6"]
    assert history_cls.traversed_path == []
    history_cls.traversed_path = ["path1", "path2", "path3"]
    history_cls.bulk_add_to_new_links_traversed_paths(new_links)
    assert history_cls.get_new_links_traversed_path("path4") == [
        "path1",
        "path2",
        "path3",
        "path4",
    ]
    assert history_cls.get_new_links_traversed_path("path5") == [
        "path1",
        "path2",
        "path3",
        "path5",
    ]
    assert history_cls.get_new_links_traversed_path("path6") == [
        "path1",
        "path2",
        "path3",
        "path6",
    ]
    assert history_cls.get_new_links_traversed_path("path7") == []
