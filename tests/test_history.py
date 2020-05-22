from pytest_redis import factories
from common.history import History
from common.status import Status

redis_mock_status = factories.redisdb('redis_nooproc', 1)
redis_mock_visited = factories.redisdb('redis_nooproc', 2)
redis_mock_scores = factories.redisdb('redis_nooproc', 3)
redis_mock_traversed = factories.redisdb('redis_nooproc', 4)


def mock_history(redis_mock_status, redis_mock_visited, redis_mock_scores, redis_mock_traversed):
    status = Status(redis_mock_status, "root_path", "start_path", "end_path")
    history = History(status, redis_mock_visited, redis_mock_scores, redis_mock_traversed, "start_path",
                      ["path1", "path2", "path3"])
    return history


def test_history_init(redis_mock_status, redis_mock_visited, redis_mock_scores, redis_mock_traversed):
    status = Status(redis_mock_status, "root_path", "start_path", "end_path")
    history = History(status, redis_mock_visited, redis_mock_scores, redis_mock_traversed, "start_path",
                      ["path1", "path2", "path3"])
    assert isinstance(history.status, Status)
    assert history.status == history.status
    assert history.redis_client_visited == redis_mock_visited
    assert history.redis_client_scores == redis_mock_scores
    assert history.redis_client_traversed == redis_mock_traversed
    assert history.start_path == "start_path"
    assert history.traversed_path == ["path1", "path2", "path3"]


def test_history_visited(redis_mock_status, redis_mock_visited, redis_mock_scores, redis_mock_traversed):
    history = mock_history(redis_mock_status, redis_mock_visited, redis_mock_scores, redis_mock_traversed)
    assert history.visited == set()


def test_is_visited(redis_mock_status, redis_mock_visited, redis_mock_scores, redis_mock_traversed):
    history = mock_history(redis_mock_status, redis_mock_visited, redis_mock_scores, redis_mock_traversed)
    assert history.is_visited("some_path") is False
    history.add_to_visited("some_path")
    assert history.is_visited("some_path") is True


def test_history_add_to_visited(redis_mock_status, redis_mock_visited, redis_mock_scores, redis_mock_traversed):
    history = mock_history(redis_mock_status, redis_mock_visited, redis_mock_scores, redis_mock_traversed)
    assert history.visited == set()
    history.add_to_visited("path")
    assert history.visited == {b'path'}


def test_history_scores(redis_mock_status, redis_mock_visited, redis_mock_scores, redis_mock_traversed):
    history = mock_history(redis_mock_status, redis_mock_visited, redis_mock_scores, redis_mock_traversed)
    assert history.scores == list()


def test_history_add_to_score(redis_mock_status, redis_mock_visited, redis_mock_scores, redis_mock_traversed):
    history = mock_history(redis_mock_status, redis_mock_visited, redis_mock_scores, redis_mock_traversed)
    assert history.scores == list()
    history.add_to_scores(0.7, "link1")
    assert history.scores == [(b'link1', 0.7)]


def test_history_bulk_add_to_score(redis_mock_status, redis_mock_visited, redis_mock_scores, redis_mock_traversed):
    history = mock_history(redis_mock_status, redis_mock_visited, redis_mock_scores, redis_mock_traversed)
    assert history.scores == list()
    history.bulk_add_to_scores([["path1", 0.7], ["path2", 0.9], ["path3", 0.1]])
    assert history.scores == [(b'path3', 0.1), (b'path1', 0.7), (b'path2', 0.9)]


def test_history_next_highest_score(redis_mock_status, redis_mock_visited, redis_mock_scores, redis_mock_traversed):
    history = mock_history(redis_mock_status, redis_mock_visited, redis_mock_scores, redis_mock_traversed)
    assert history.scores == list()
    history.bulk_add_to_scores([["path1", 0.7], ["path2", 0.9], ["path3", 0.1]])
    assert history.scores == [(b'path3', 0.1), (b'path1', 0.7), (b'path2', 0.9)]
    assert history.next_highest_score() == "path2"


def test_traversed_path(redis_mock_status, redis_mock_visited, redis_mock_scores, redis_mock_traversed):
    history = mock_history(redis_mock_status, redis_mock_visited, redis_mock_scores, redis_mock_traversed)
    assert history.traversed_path == ["path1", "path2", "path3"]


def test_set_traversed_path(redis_mock_status, redis_mock_visited, redis_mock_scores, redis_mock_traversed):
    history = mock_history(redis_mock_status, redis_mock_visited, redis_mock_scores, redis_mock_traversed)
    assert history.traversed_path == ["path1", "path2", "path3"]
    history.traversed_path = ["path4", "path5", "path6"]
    assert history.traversed_path == ["path4", "path5", "path6"]