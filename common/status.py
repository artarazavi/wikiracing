from redis import Redis
from datetime import datetime
from typing import List, Union
import json
from .config import get_celery_app
import sys

app = get_celery_app()


TESTING = False
if "pytest" in sys.modules:
    TESTING = True


class Status:
    """
    status_db
        root_path
            active = "active" / "done"
            results = "None" / traversed path
            start_time = datetime
            end_time = "None" / datetime
            task_id = string id
            start_path = string
            end_path = string
    """

    def __init__(
            self,
            redis_client: Redis,
            root_path: str,
            start_path: str = None,
            end_path: str = None
    ):

        self.redis_client = redis_client
        self.root_path = root_path

        if not self.exists(self.redis_client, self.root_path):
            with self.redis_client.lock("status-init-lock"):
                self.redis_client.hset(self.root_path, mapping=dict(
                    active="active",
                    results="None",
                    start_time=datetime.now().timestamp(),
                    end_time="None",
                    task_id="None",
                    start_path=start_path,
                    end_path=end_path
                ))

    @staticmethod
    def exists(redis_client: Redis, root_path) -> bool:
        return bool(redis_client.exists(root_path))

    def get_from_redis(self, key: str):
        data = self.redis_client.hget(self.root_path, key)
        if data:
            return data.decode()
        return None

    def set_to_redis(self, key: str, value):
        self.redis_client.hset(self.root_path, key, value)

    def finalize_results(self, traversed_path: List[str]):
        self.set_end_time()
        self.set_no_longer_active()
        self.results = traversed_path
        if not TESTING:
            app.control.revoke(self.task_id, terminate=True, signal='SIGKILL')  # pragma: no cover

    @property
    def active(self) -> str:
        return self.get_from_redis("active")

    def set_no_longer_active(self):
        with self.redis_client.lock("active-lock"):
            self.set_to_redis("active", "done")

    def is_active(self) -> bool:
        return self.active == "active"

    @property
    def results(self) -> List[str]:
        if self.get_from_redis("results") != "None":
            return json.loads(self.redis_client.hget(self.root_path, "results"))
        return list()

    @results.setter
    def results(self, traversed_path: List[str]):
        with self.redis_client.lock("results-lock"):
            self.set_to_redis("results", json.dumps(traversed_path))

    def results_str(self) -> str:
        if self.get_from_redis("results") != "None":
            return self.redis_client.hget(self.root_path, "results")
        return "None"

    def results_pending(self) -> bool:
        return self.results == "None"

    @property
    def start_time(self) -> float:
        return float(self.get_from_redis("start_time"))

    @start_time.setter
    def start_time(self, value: float):
        self.set_to_redis("start_time", value)

    @property
    def end_time(self) -> Union[str, float]:
        if self.get_from_redis("end_time") != "None":
            return float(self.get_from_redis("end_time"))
        return "None"

    @end_time.setter
    def end_time(self, value: float):
        self.set_to_redis("end_time", value)

    def set_end_time(self):
        with self.redis_client.lock("time-end-lock"):
            total_seconds = (
                    datetime.now() - datetime.fromtimestamp(self.start_time)
            ).total_seconds()
            self.end_time = total_seconds

    @property
    def task_id(self) -> str:
        return self.get_from_redis("task_id")

    @task_id.setter
    def task_id(self, value: str):
        self.set_to_redis("task_id", value)

    @property
    def start_path(self) -> str:
        return self.get_from_redis("start_path")

    @start_path.setter
    def start_path(self, value: str):
        self.set_to_redis("start_path", value)

    @property
    def end_path(self) -> str:
        return self.get_from_redis("end_path")

    @end_path.setter
    def end_path(self, value: str):
        self.set_to_redis("end_path", value)
