from time import sleep
from typing import TYPE_CHECKING, List
from celery import Celery
from common.config import (
    get_celery_app,
    get_status_db,
    visited_db,
    scores_db,
    traversed_db,
    logger,
    REDIS_URL
)

from common.history import History
from common.nlp import NLP
from common.wikipedia import Wikipedia
from common.status import Status

status_db = get_status_db()
app = get_celery_app()


@app.task(name="tasks.add", bound=True)
def add(self, x: int, y: int) -> int:
    sleep(5)
    return x + y


def found_in_page(status: 'Status', history: History, all_links: List[str]) -> bool:
    if status.end_path in all_links:
        path = history.traversed_path
        path.append(status.end_path)
        status.finalize_results(path)
        logger.info(f"End link found!! path traversed and time to complete: {path}")
        return True
    return False


def pop_prev_pages(start_path: str, traversed_path: List[str]) -> List[str]:
    if not traversed_path:
        traversed_path = list()
    if start_path in traversed_path:
        while not True:
            x = traversed_path.pop()
            if x == start_path:
                break
    return traversed_path


@app.task(name="tasks.find")
def find(
    root_path: str,
    start_path: str,
    traversed_path: List[str] = None,
):
    status = Status(status_db, root_path)
    # Dont start find if task is done
    if not status.is_active():
        return

    if not traversed_path:
        traversed_path = list()

    traversed_path = pop_prev_pages(start_path, traversed_path)
    traversed_path.append(start_path)

    # Populates history
    history = History(
        status,
        visited_db,
        scores_db,
        traversed_db,
        start_path,
        traversed_path
    )

    if not history.is_visited(start_path):
        history.add_to_visited(start_path)

        # links from wikipedia
        all_links = Wikipedia(status, start_path).scrape_page()

        # return if found
        if found_in_page(status, history, all_links):
            return

        # score found links
        nlp_scores = NLP(status, history).score_links(all_links)
        history.bulk_add_to_scores(nlp_scores)

    else:
        history.add_to_visited(start_path)

    # Dont kick off next find find if task is done
    if not status.is_active():
        return

    app.send_task(
        "tasks.find",
        kwargs=dict(
            root_path=root_path,
            start_path=history.next_highest_score(),
            traversed_path=traversed_path,
        ),
        queue='find'
    )





