from typing import List
import json

from common.config import (
    get_celery_app,
    get_status_db,
    get_visited_db,
    get_scores_db,
    get_traversed_db,
    logger,
)
from common.history import History
from common.nlp import NLP
from common.status import Status
from common.wikipedia import Wikipedia

app = get_celery_app()
status_db = get_status_db()
visited_db = get_visited_db()
scores_db = get_scores_db()
traversed_db = get_traversed_db()


def found_in_page(status: Status, history: History, all_links: List[str], rev_root_path: str) -> bool:
    """Whether wiki race end path was found in newly discovered links.

    If the  wiki race end path was discovered on current page:
    Results traversed path: end path appended to the current query page's traversed path.
    Finalize results: by sending the finalized results traversed path to status.

    Args:
        status: Status of current search.
        history: History of current search.
        all_links: List of new links discovered on current query page.
        rev_root_path: The path reversed of this one.
    """
    # python intersect
    # redis supports this throgh SINTER key1 key2
    status_rev = Status(status_db, rev_root_path)
    intersection = list(set(history.redis_client_traversed.hkeys(status.root_path)) & set(history.redis_client_traversed.hkeys(rev_root_path)))
    if status.end_path in all_links:
        path = history.traversed_path.copy()
        path.append(status.end_path)
        status.finalize_results(path)
        path_rev = path.copy()
        path_rev.reverse()
        status_rev.finalize_results(path_rev)
        logger.info(f"End link found!! path traversed and time to complete: {path} or {path_rev}")
        return True
    elif intersection:
        logger.info("INTERSECTION FOUND HOLY SHIT COOL")
        intersection_page = intersection[0].decode()
        traversed_path_root_path = json.loads(history.redis_client_traversed.hget(status.root_path, intersection_page).decode())
        traversed_path_rev_root_path = json.loads(history.redis_client_traversed.hget(rev_root_path, intersection_page).decode())
        traversed_path_rev_root_path.pop()
        traversed_path_rev_root_path.reverse()
        path_to_goal = traversed_path_root_path + traversed_path_rev_root_path
        status.finalize_results(path_to_goal)
        path_to_goal_rev = path_to_goal.copy()
        path_to_goal_rev.reverse()
        status_rev.finalize_results(path_to_goal_rev)
        logger.info(f"Intersection End link found from page {intersection_page}!! path traversed and time to complete: {path_to_goal} or {path_to_goal_rev}")
        return True
    return False


@app.task(name="tasks.find")
def find(
    root_path: str, start_path: str, rev_root_path: str, rev=False
):
    """Celery task that plays wiki racer game.

    This task only kicks off if the search is still active.
    Sets history: Based on search status and current page bering queried.
    Keeps track of visited: If a node is already visited do not visit again (prevent cycles)
    Upon discovery of a new page: Scrape page for new links.
    When new links obtained: Score links based on similarity to wiki race end path.
    Track game completion: When wiki game end path is found in newly discovered links end the game.
    If wiki page end game not found, send another task to find with:
        start_path/query: [highest scoring page discovered so far].


    Args:
        root_path: Search key composed of wiki racer start page and end page.
        start_path: Page being queried.
        rev_root_path: The path reversed of this one.
        rev: are we going in reverse?
    """
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
        all_links = Wikipedia(status, start_path, rev).scrape_page()

        # return if found
        if found_in_page(status, history, all_links, rev_root_path):
            return

        # score found links
        nlp_scores = NLP(status, history).score_links(all_links)

        # set their new traversed paths
        history.bulk_add_to_new_links_traversed_paths(all_links)

        # add them onto scores set
        history.bulk_add_to_scores(nlp_scores)

    # Dont kick off next find find if task is done or no more pages left to search
    if not status.is_active() or len(history.scores) < 1:
        return

    # kick off another find task with highest scoring page found so far
    app.send_task(
        "tasks.find",
        kwargs=dict(root_path=root_path, start_path=history.next_highest_score(), rev_root_path=rev_root_path, rev=rev),
        queue="find_rev" if rev else "find",
    )
