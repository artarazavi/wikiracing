from time import sleep
from typing import List

# from celery import Celery

# TODO fix all dbs to get_db logic like get status db to make testing easier
from common.config import (
    get_celery_app,
    get_status_db,
    get_visited_db,
    get_scores_db,
    get_traversed_db,
    logger,
    # REDIS_URL
)

from common.history import History
from common.nlp import NLP
from common.wikipedia import Wikipedia
from common.status import Status

status_db = get_status_db()
visited_db = get_visited_db()
scores_db = get_scores_db()
traversed_db = get_traversed_db()
app = get_celery_app()


def found_in_page(status: Status, history: History, all_links: List[str]) -> bool:
    if status.end_path in all_links:
        path = history.traversed_path
        path.append(status.end_path)
        status.finalize_results(path)
        logger.info(f"End link found!! path traversed and time to complete: {path}")
        return True
    return False


@app.task(name="tasks.find")
def find(
    root_path: str, start_path: str,
):
    status = Status(status_db, root_path)

    # Dont start find if task is done
    if not status.is_active():
        return

    # Populates history
    history = History(status, visited_db, scores_db, traversed_db, start_path,)

    if start_path == status.start_path:
        history.traversed_path = [status.start_path]

    if not history.is_visited(start_path):
        history.add_to_visited(start_path)

        # links from wikipedia
        all_links = Wikipedia(status, start_path).scrape_page()

        # return if found
        if found_in_page(status, history, all_links):
            return

        # score found links
        nlp_scores = NLP(status, history).score_links(all_links)

        # set their new traversed paths
        history.bulk_add_to_new_links_traversed_paths(all_links)

        # add them onto scores set
        history.bulk_add_to_scores(nlp_scores)

    else:
        history.add_to_visited(start_path)

    # Dont kick off next find find if task is done
    if not status.is_active():
        return

    app.send_task(
        "tasks.find",
        kwargs=dict(root_path=root_path, start_path=history.next_highest_score(),),
        queue="find",
    )
