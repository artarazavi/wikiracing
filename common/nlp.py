from typing import List
from celery import group
from time import sleep

from . import config

from typing import TYPE_CHECKING, Any

app = config.get_celery_app()

if TYPE_CHECKING:
    from .history import History
    from .status import Status


class NLP:
    def __init__(self, status: "Status", history: "History"):
        self.status = status
        self.history = history

    def score_links(self, all_links: List[str]) -> List[List[Any]]:
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
        # waits for subtasks and we can do this because we have multiple queues we dont need to worry.

        return nlp_scored_results.get(disable_sync_subtasks=False)
