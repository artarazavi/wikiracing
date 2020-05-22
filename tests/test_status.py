from pytest_redis import factories
from common.status import Status
redis_mock = factories.redisdb('redis_nooproc')




def test_status_init(redis_mock):
    s = Status(redis_mock, "root_path", "start_path", "end_path")
    assert s.active == "active"
    assert s.results == "None"
    assert isinstance(
        s.start_time,
        float
    )
    assert s.end_time == "None"
    assert s.task_id == "None"
    assert s.start_path == "start_path"
    assert s.end_path == "end_path"


def test_exists(redis_mock):
    assert Status.exists(redis_mock, "root_path") is False
    Status(redis_mock, "root_path", "start_path", "end_path")
    assert Status.exists(redis_mock, "root_path") is True


def test_get_from_redis(redis_mock):
    s = Status(redis_mock, "root_path", "start_path", "end_path")
    assert s.get_from_redis("active") == "active"


def test_set_to_redis(redis_mock):
    value = "done"
    s = Status(redis_mock, "root_path", "start_path", "end_path")
    assert s.get_from_redis("active") == "active"
    s.set_to_redis("active", value)
    assert s.get_from_redis("active") == value


def test_finalize_results(redis_mock):
    path = ["path1", "path2", "path3"]
    s = Status(redis_mock, "root_path", "start_path", "end_path")
    s.finalize_results(path)
    assert isinstance(
        s.end_time,
        float
    )
    assert s.is_active() is False
    assert s.results == path


def test_set_no_longer_active(redis_mock):
    s = Status(redis_mock, "root_path", "start_path", "end_path")
    s.set_no_longer_active()
    assert s.active == "done"


def test_is_active(redis_mock):
    s = Status(redis_mock, "root_path", "start_path", "end_path")
    assert s.is_active() is True
    s.set_no_longer_active()
    assert s.is_active() is False


def test_results_pending(redis_mock):
    path = ["path1", "path2", "path3"]
    s = Status(redis_mock, "root_path", "start_path", "end_path")
    assert s.results_pending() is True
    s.finalize_results(path)
    assert s.results == path


def test_set_and_get_end_time(redis_mock):
    s = Status(redis_mock, "root_path", "start_path", "end_path")
    s.set_end_time()
    assert s.end_time != "None"
    assert isinstance(
        s.end_time,
        float
    )
    s.end_time = 2.5
    assert s.end_time != "None"
    assert isinstance(
        s.end_time,
        float
    )


def test_set_and_get_start_time(redis_mock):
    s = Status(redis_mock, "root_path", "start_path", "end_path")
    s.start_time = 2.5
    assert isinstance(
        s.start_time,
        float
    )
    assert s.start_time == 2.5


def test_set_and_get_paths(redis_mock):
    new_start_path = "new_start_path"
    new_end_path = "new_end_path"
    s = Status(redis_mock, "root_path", "start_path", "end_path")
    s.start_path = new_start_path
    assert s.start_path == new_start_path
    s.end_path = new_end_path
    assert s.end_path == new_end_path


def test_set_and_get_task_id(redis_mock):
    new_id = "new_id"
    s = Status(redis_mock, "root_path", "start_path", "end_path")
    s.task_id = new_id
    assert s.task_id == new_id


def set_and_get_results(redis_mock):
    new_results = ["path1", "path2", "path3"]
    s = Status(redis_mock, "root_path", "start_path", "end_path")
    assert s.results == "None"
    s.results = new_results
    assert s.results == new_results