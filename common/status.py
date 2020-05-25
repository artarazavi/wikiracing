from redis import Redis
from datetime import datetime
from typing import List, Union
import json
from .config import get_celery_app
import sys

TESTING = False
if "pytest" in sys.modules:
    TESTING = True


class Status:
    """
    Status redis db breakdown:


    Status:
    Redis data type: (Hash) maps between string fields and string values
    Complexity:
        HSET, HGET:
            O(1)
    status_db:
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
        end_path: str = None,
    ):
        """Status tracks state of search.

        Args:
            redis_client: Redis status db.
            root_path: Search key composed of wiki racer start page and end page.
            start_path: Wiki racer game start page.
            end_path: Wiki racer game end page.
        """

        self.redis_client = redis_client
        self.root_path = root_path

        if not self.exists(self.redis_client, self.root_path):
            with self.redis_client.lock("status-init-lock"):
                self.redis_client.hset(
                    self.root_path,
                    mapping=dict(
                        active="active",
                        results="None",
                        start_time=datetime.now().timestamp(),
                        end_time="None",
                        task_id="None",
                        start_path=start_path,
                        end_path=end_path,
                    ),
                )

    @staticmethod
    def exists(redis_client: Redis, root_path) -> bool:
        """Has there been a status db entry initiated for current search root_path?

        Notes:
            This reads information from the status redis db.

        Args:
            redis_client: Redis status db.
            root_path: Search key composed of wiki racer start page and end page.
        """
        return bool(redis_client.exists(root_path))

    def get_from_redis(self, key: str):
        """Reads data from redis hash status db based on key.

        Notes:
            This reads information from the status redis db.

        Args:
            key: Key in redis hash status db.

        Returns: Value in redis hash status db.
        """
        data = self.redis_client.hget(self.root_path, key)
        if data:
            return data.decode()
        return None

    def set_to_redis(self, key: str, value):
        """Set data to the redis hash status db based on Key Value pairs.

        Notes:
            This sets information in the status redis db.

        Args:
            key: Key in redis hash status db.
            value: Value in redis hash status db.
        """
        self.redis_client.hset(self.root_path, key, value)

    def finalize_results(self, traversed_path: List[str]):
        """ Solution to wiki racer game discovered finalize results in status db.

        When a solution to the wiki racer has been discovered:
        Calculate time taken to solve wiki racer record in redis status db.
        Deactivate the search record in redis status db.
        Record the results (traversed_path) in the redis status db.

        Terminate the parent celery task:
            All child tasks will be killed when parent task is terminated.

        Notes:
            This sets and reads information from the status redis db.

        Args:
            traversed_path: The solution path outlining steps from start path to end path.

        """
        self.set_end_time()
        self.set_no_longer_active()
        self.results = traversed_path
        app = get_celery_app()
        if not TESTING:
            app.control.revoke(
                self.task_id, terminate=True, signal="SIGKILL"
            )  # pragma: no cover

    @property
    def active(self) -> str:
        """Reads "active" status from redis hash status db.

        Returns: "active" || "done".

        """
        return self.get_from_redis("active")

    def set_no_longer_active(self):
        """Sets "active" status in the redis hash status db to "done"."""
        with self.redis_client.lock("active-lock"):
            self.set_to_redis("active", "done")

    def is_active(self) -> bool:
        """Is the search associated with this root_path still active?"""
        return self.active == "active"

    @property
    def results(self) -> List[str]:
        """Reads results from redis hash status db.

        Notes:
            This reads information from the status redis db.

        Returns: The results as a list of traversed path || list() if results not ready.
        """
        if self.get_from_redis("results") != "None":
            return json.loads(self.redis_client.hget(self.root_path, "results"))
        return list()

    @results.setter
    def results(self, traversed_path: List[str]):
        with self.redis_client.lock("results-lock"):
            self.set_to_redis("results", json.dumps(traversed_path))

    def results_str(self) -> str:
        """Reads results from redis hash status db as string.

        Notes:
            This reads information from the status redis db.

        Returns: The results as a string of traversed path || "None" if not ready.

        """
        if self.get_from_redis("results") != "None":
            return self.redis_client.hget(self.root_path, "results").decode()
        return "None"

    def results_pending(self) -> bool:
        """Are the results ready?"""
        return self.results_str() == "None"

    @property
    def start_time(self) -> float:
        """Time the wiki racer game started."""
        return float(self.get_from_redis("start_time"))

    @start_time.setter
    def start_time(self, value: float):
        self.set_to_redis("start_time", value)

    @property
    def end_time(self) -> Union[str, float]:
        """Time the wiki racer game ended || "None" if still active."""
        if self.get_from_redis("end_time") != "None":
            return float(self.get_from_redis("end_time"))
        return "None"

    @end_time.setter
    def end_time(self, value: float):
        self.set_to_redis("end_time", value)

    def set_end_time(self):
        """Calculate end time based on start time."""
        with self.redis_client.lock("time-end-lock"):
            total_seconds = (
                datetime.now() - datetime.fromtimestamp(self.start_time)
            ).total_seconds()
            self.end_time = total_seconds

    @property
    def task_id(self) -> str:
        """The task id of the parent task that started the wiki racer game."""
        return self.get_from_redis("task_id")

    @task_id.setter
    def task_id(self, value: str):
        self.set_to_redis("task_id", value)

    @property
    def start_path(self) -> str:
        """The start path of the wiki racer game."""
        return self.get_from_redis("start_path")

    @start_path.setter
    def start_path(self, value: str):
        self.set_to_redis("start_path", value)

    @property
    def end_path(self) -> str:
        """The end path of the wiki racer game."""
        return self.get_from_redis("end_path")

    @end_path.setter
    def end_path(self, value: str):
        self.set_to_redis("end_path", value)
