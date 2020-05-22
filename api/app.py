import celery.states as states
from flask import Flask, url_for

from common.config import get_celery_app , get_status_db, logger
from common.status import Status

app = Flask(__name__)

celery = get_celery_app()
status_db = get_status_db()

def build_root_path(start_path: str, end_path: str):
    return f"{start_path}-{end_path}"


@app.route("/find/<string:start_path>/<string:end_path>")
def find(start_path: str, end_path: str) -> str:
    root_path = build_root_path(start_path, end_path)

    if Status.exists(status_db, root_path):
        status = Status(status_db, root_path)
        return "Pending" if status.results_pending() else status.results

    # Initialize status
    status = Status(status_db, root_path, start_path, end_path)

    task = celery.send_task(
        "tasks.find",
        kwargs=dict(
            root_path=root_path,
            start_path=start_path,
        ),
        queue='find'
    )

    status.task_id = task.id

    return "Pending"


# test function
@app.route("/add/<int:param1>/<int:param2>")
def add(param1: int, param2: int) -> str:
    task = celery.send_task("tasks.add", args=[param1, param2], kwargs={})
    response = f"<a href='{url_for('check_task', task_id=task.id, external=True)}'>check status of {task.id} </a>"
    return response


# test function
@app.route("/check/<string:task_id>")
def check_task(task_id: str) -> str:
    res = celery.AsyncResult(task_id)
    if res.state == states.PENDING:
        return res.state
    else:
        return str(res.result)
