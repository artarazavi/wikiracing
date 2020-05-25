from typing import List
from celery import group
from time import sleep
from . import config
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .history import History
    from .status import Status

app = config.get_celery_app()


class NLP:
    def __init__(self, status: "Status", history: "History"):
        """NLP scores links based on similarity scores.

        NLP class takes care of getting a list of links and scoring them.
        Scoring is based on nlp similarity to the goal end path.
        This class makes use of celery to parallelize score computation & save time.

        Args:
            status: Status of current search.
            history: History of current search.
        """
        self.status = status
        self.history = history

    def score_links(self, all_links: List[str]) -> List[List[Any]]:
        """Scores a list of links based on their nlp similarity scores

        Notes:
            Makes use of celery to parallelize score computation.
            The celery group  takes a list of tasks that should be applied in parallel.
            Using get holds up computation until the async task results are ready.

        Args:
            all_links: New links discovered on page.

        Returns: List of scored links.

        """
        scoring_jobs = group(
            [
                app.signature(
                    "tasks.nlp",
                    kwargs=dict(end_path=self.status.end_path, query=query),
                    queue="nlp",
                )
                # only score non visited links
                for query in all_links
                if not self.history.is_visited(query)
            ]
        )
        nlp_scored_results = scoring_jobs.apply_async(queue="nlp")
        while not nlp_scored_results.ready():
            sleep(0.5)

        # Keeps me from getting yelled at for waiting and possibly deadlocking the queue
        # waits for sub-tasks and we can do this because we have multiple queues we dont need to worry.
        return nlp_scored_results.get(disable_sync_subtasks=False)
