from redis import Redis
from typing import List, Any
import json
from .status import Status
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .status import Status


class History:
    """
    History redis db breakdown:

    Visited:
    Redis data type: (Set) Unordered collection of non repeating Strings
    Complexity:
        SISMEMBER, SADD:
            O(1)
    visited_db:
        root_path: Set(visited pages)


    Scores:
    Redis data type: (Sorted set) similar to Redis Sets
        Each data point in a Sorted Set is associated with a score.
        The score is used to order the set members from smallest to the greatest score.
    Complexity:
        ZADD:
            O(log(N)) for each item added
        ZPOPMAX:
            O(log(N)*M)
            N being the number of elements in the sorted set.
            M being the number of elements popped.
    scores_db:
        root_path: Sorted Set(next pages to visit)


    Traversed:
    Redis data type: (Hash) maps between string fields and string values
    Complexity:
        HSET, HGET:
            O(1)
    traversed_db:
        root_path:
            page:   traversed_path_str
            page    traversed_path_str

    """
    def __init__(
        self,
        status: "Status",
        redis_client_visited: Redis,
        redis_client_scores: Redis,
        redis_client_traversed: Redis,
        start_path: str,
    ):
        """History tracks works done during search.

        History class deals with keeping track of work done and results obtained:
        Tracks pages we have already visited so we dont go in circles.
        Maintain a sorted list of pages to be visiting next based on highest similarity scores.
        For every page that is scored, keep track of the path traversed to that page.

        Args:
            status: Status of current search.
            redis_client_visited: Redis visited pages db.
            redis_client_scores: Redis scored pages db.
            redis_client_traversed: Redis traversed path db.
            start_path: Page being queried in find.

        """

        # db
        self.redis_client_visited = redis_client_visited
        self.redis_client_scores = redis_client_scores
        self.redis_client_traversed = redis_client_traversed
        self.status = status

        # args
        self.start_path = start_path

    @property
    def visited(self) -> List[str]:
        """List of pages that have been visited.

        Notes:
            This reads information from the visited redis db.

        """
        return self.redis_client_visited.smembers(self.status.root_path)

    def is_visited(self, value: str) -> bool:
        """Have we visited this page?

        Args:
            value: Page title.

        Notes:
            This reads information from the visited redis db.

        """
        return bool(self.redis_client_visited.sismember(self.status.root_path, value))

    def add_to_visited(self, value: str):
        """Add page to set of visited pages.

        Args:
            value: Page title.

        Notes:
            This sets information in the visited redis db.

        """
        self.redis_client_visited.sadd(self.status.root_path, value)

    @property
    def scores(self) -> List[str]:
        """List of current scored pages in sorted scores db.

        Notes:
            This reads information from the scores redis db.

        """
        scores = self.redis_client_scores.zscan(self.status.root_path, 0)
        if scores:
            return scores[1]
        return list()

    def add_to_scores(self, score: float, link_name: str):
        """Add a scored page into the sorted scores db.

        Notes:
            This sets information in the scores redis db.

        Args:
            score: Page score.
            link_name: Page title.

        """
        if not self.is_visited(link_name):
            self.redis_client_scores.zadd(self.status.root_path, {link_name: score})

    def bulk_add_to_scores(self, scores: List[List[Any]]):
        """Add a list of scored pages into sorted scores db.

        Args:
            scores: List of scored pages.

        """
        for link_score in scores:
            link, score = link_score
            # only add on links we have not seen to scores
            if not self.is_visited(link):
                self.add_to_scores(score, link)

    def next_highest_score(self) -> str:
        """Pops the highest scoring page from the sorted scores db.

        Notes:
            This reads information from the scores redis db.

        Returns: Page title.

        """
        return self.redis_client_scores.zpopmax(self.status.root_path)[0][0].decode()

    @property
    def traversed_path(self) -> List[str]:
        """Traversed path taken to discover the current page.

        Notes:
            This reads information from the traversed path redis db.

        """
        if not self.redis_client_traversed.hget(self.status.root_path, self.start_path):
            return list()
        return json.loads(
            self.redis_client_traversed.hget(
                self.status.root_path, self.start_path
            ).decode()
        )

    @traversed_path.setter
    def traversed_path(self, value: List[str]):
        self.redis_client_traversed.hset(
            self.status.root_path, self.start_path, json.dumps(value)
        )

    def get_new_links_traversed_path(self, link) -> List[str]:
        """Gets traversed path taken to any page.

        Notes:
            This reads information from the traversed path redis db.

        Args:
            link: Link you want to get traversed path for.

        Returns: list of pages representing path taken to discover that page.

        """
        if not self.redis_client_traversed.hget(self.status.root_path, link):
            return list()
        return json.loads(
            self.redis_client_traversed.hget(self.status.root_path, link).decode()
        )

    def new_links_set_traversed_path(self, link: str):
        """Each newly discovered page has its traversed path (path taken to discover that page)
        set to the querying page's traversed path appended by itself.

        Notes:
            This sets information in the traversed path redis db.

        Args:
            link: Newly discovered page.

        """
        updated_path = self.traversed_path.copy()
        # wikipedia has these weird things called transclusions where a page links to itself
        if updated_path[-1] != link:
            updated_path.append(link)
        self.redis_client_traversed.hset(
            self.status.root_path, link, json.dumps(updated_path)
        )

    def bulk_add_to_new_links_traversed_paths(self, links: List[str]):
        """sets the traversed path for a list of newly discovered pages.

        Args:
            links: List of newly discovered pages.

        """
        for link in links:
            self.new_links_set_traversed_path(link)

    def traversed_keys(self, root_path: str) -> List[str]:
        """Dumps the keys in the redis traversed db for root_path specified.

        Notes:
            This reads information from the redis traversed path redis db.

        Args:
            root_path: The key to the hash were looking up in the redis traversed db.

        """
        return self.redis_client_traversed.hkeys(root_path)

    def traversed_intersection(self, root_path:str, rev_root_path: str) -> List[str]:
        """The intersection between traversed paths of find and find in reverse.

        Args:
            root_path: Find root_path.
            rev_root_path: The reverse find root_path.

        """
        return list(set(self.traversed_keys(root_path)) & set(self.traversed_keys(rev_root_path)))

    def any_traversed_path(self, root_path: str, page: str) -> List[str]:
        """Gets traversed path of any page in the redis traversed db based on hash key and page title.

        Notes:
            This reads information from the redis traversed path redis db.

        Args:
            root_path: The key to the hash were looking up in the redis traversed db.
            page: Title of page as key under that hash in redis traversed db.

        """
        if not self.redis_client_traversed.hget(root_path, page):
            return list()
        return json.loads(
            self.redis_client_traversed.hget(
                root_path, page
            ).decode()
        )

    def intersection_path(self, root_path: str, rev_root_path: str) -> List[str]:
        """The end result path based on an intersecting page in search and search reversed.

        Args:
            root_path: Find root_path.
            rev_root_path: The reverse find root_path.

        Returns: path find + reversed (path find reversed + pop last item)

        """
        intersection = self.traversed_intersection(root_path, rev_root_path)
        intersection_page = intersection[0].decode()
        traversed_path_root_path = self.any_traversed_path(root_path, intersection_page)
        traversed_path_rev_root_path = self.any_traversed_path(rev_root_path, intersection_page)
        traversed_path_rev_root_path.pop()
        traversed_path_rev_root_path.reverse()
        path_to_goal = traversed_path_root_path + traversed_path_rev_root_path
        return path_to_goal
