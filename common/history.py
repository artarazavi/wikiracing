from redis import Redis
from typing import List, Any
import json
from .status import Status
from .config import (
    logger,
)

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .status import Status


class History:
    def __init__(
            self,
            status: 'Status',
            redis_client_visited: Redis,
            redis_client_scores: Redis,
            redis_client_traversed: Redis,
            start_path: str,
    ):

        # db
        self.redis_client_visited = redis_client_visited
        self.redis_client_scores = redis_client_scores
        self.redis_client_traversed = redis_client_traversed
        self.status = status

        # args
        self.start_path = start_path

    @property
    def visited(self) -> List[str]:
        return self.redis_client_visited.smembers(self.status.root_path)

    def is_visited(self, value: str) -> bool:
        return bool(self.redis_client_visited.sismember(self.status.root_path, value))

    def add_to_visited(self, value: str):
        return self.redis_client_visited.sadd(self.status.root_path, value)

    @property
    def scores(self) -> List[str]:
        scores = self.redis_client_scores.zscan(self.status.root_path, 0)
        if scores:
            return scores[1]
        return []

    def add_to_scores(self, score: float, link_name: str):
        self.redis_client_scores.zadd(self.status.root_path, {link_name: score})

    def bulk_add_to_scores(self, scores: List[List[Any]]):
        for link_score in scores:
            link, score = link_score
            # only add on links we have not seen to scores
            if not self.is_visited(link):
                self.add_to_scores(score, link)

    def next_highest_score(self) -> str:
        return self.redis_client_scores.zpopmax(self.status.root_path)[0][0].decode()

    @property
    def traversed_path(self) -> List[str]:
        if not self.redis_client_traversed.hget(self.status.root_path, self.start_path):
            return list()
        return json.loads(self.redis_client_traversed.hget(self.status.root_path, self.start_path).decode())

    @traversed_path.setter
    def traversed_path(self, value: List[str]):
        self.redis_client_traversed.hset(self.status.root_path, self.start_path, json.dumps(value))

    def get_new_links_traversed_path(self, link) -> List[str]:
        if not self.redis_client_traversed.hget(self.status.root_path, link):
            return list()
        return json.loads(self.redis_client_traversed.hget(self.status.root_path, link).decode())

    def new_links_set_traversed_path(self, link: str):
        updated_path = self.traversed_path.copy()
        updated_path.append(link)
        self.redis_client_traversed.hset(self.status.root_path, link, json.dumps(updated_path))

    def bulk_add_to_new_links_traversed_paths(self, links: List[str]):
        for link in links:
            self.new_links_set_traversed_path(link)
