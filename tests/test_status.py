from pytest_redis import factories
from common.status import Status
import pytest
redis_proc = factories.redis_proc(host="redis", port=6379, logsdir='/tmp')
redis_mock_status = factories.redisdb('redis_nooproc')


@pytest.fixture(scope='function')
@pytest.mark.usefixtures('redis_mock_status')
def status_cls(redis_mock_status):
    return Status(redis_mock_status, "root_path", "start_path", "end_path")


@pytest.mark.usefixtures('redis_mock_status')
def test_status_init(redis_mock_status):
    s = Status(redis_mock_status, "root_path", "start_path", "end_path")
    assert s.active == "active"
    assert s.results == []
    assert s.results_str() == "None"
    assert isinstance(
        s.start_time,
        float
    )
    assert s.end_time == "None"
    assert s.task_id == "None"
    assert s.start_path == "start_path"
    assert s.end_path == "end_path"


@pytest.mark.usefixtures('redis_mock_status')
def test_exists(redis_mock_status):
    assert Status.exists(redis_mock_status, "root_path") is False
    Status(redis_mock_status, "root_path", "start_path", "end_path")
    assert Status.exists(redis_mock_status, "root_path") is True


@pytest.mark.usefixtures('status_cls')
def test_set_to_redis(status_cls):
    value = "done"
    assert status_cls.get_from_redis("active") == "active"
    status_cls.set_to_redis("active", value)
    assert status_cls.get_from_redis("active") == value


@pytest.mark.usefixtures('status_cls')
def test_finalize_results(status_cls):
    path = ["path1", "path2", "path3"]
    status_cls.finalize_results(path)
    assert isinstance(
        status_cls.end_time,
        float
    )
    assert status_cls.is_active() is False
    assert status_cls.results == path


@pytest.mark.usefixtures('status_cls')
def test_set_no_longer_active(status_cls):
    status_cls.set_no_longer_active()
    assert status_cls.active == "done"

# TODO fix this
@pytest.mark.usefixtures('status_cls')
def test_unknown_status(status_cls):
    assert status_cls.is_active() is True
    status_cls.set_to_redis("active", "Broken")
    assert status_cls.is_active() is False
    status_cls.set_to_redis("active", "active")
    assert status_cls.is_active() is True


@pytest.mark.usefixtures('status_cls')
def test_is_active(status_cls):
    assert status_cls.is_active() is True
    status_cls.set_no_longer_active()
    assert status_cls.is_active() is False


@pytest.mark.usefixtures('status_cls')
def test_results_pending(status_cls):
    path = ["path1", "path2", "path3"]
    assert status_cls.results_pending() is True
    status_cls.finalize_results(path)
    assert status_cls.results == path


@pytest.mark.usefixtures('status_cls')
def test_set_and_get_end_time(status_cls):
    status_cls.set_end_time()
    assert status_cls.end_time != "None"
    assert isinstance(
        status_cls.end_time,
        float
    )
    status_cls.end_time = 2.5
    assert status_cls.end_time != "None"
    assert isinstance(
        status_cls.end_time,
        float
    )


@pytest.mark.usefixtures('status_cls')
def test_set_and_get_start_time(status_cls):
    status_cls.start_time = 2.5
    assert isinstance(
        status_cls.start_time,
        float
    )
    assert status_cls.start_time == 2.5


@pytest.mark.usefixtures('status_cls')
def test_set_and_get_paths(status_cls):
    new_start_path = "new_start_path"
    new_end_path = "new_end_path"
    status_cls.start_path = new_start_path
    assert status_cls.start_path == new_start_path
    status_cls.end_path = new_end_path
    assert status_cls.end_path == new_end_path


@pytest.mark.usefixtures('status_cls')
def test_set_and_get_task_id(status_cls):
    new_id = "new_id"
    assert status_cls.task_id == "None"
    status_cls.task_id = new_id
    assert status_cls.task_id == new_id


@pytest.mark.usefixtures('status_cls')
def set_and_get_results(status_cls):
    new_results = ["path1", "path2", "path3"]
    assert status_cls.results == "None"
    status_cls.results = new_results
    assert status_cls.results == new_results
