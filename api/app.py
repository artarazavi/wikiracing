import celery.states as states
from flask import Flask, url_for


from common import config
from common.status import Status
from time import sleep


config_celery_app = config.get_celery_app()
config_status_db = config.get_status_db()


def build_root_path(start_path: str, end_path: str):
    return f"{start_path}-{end_path}"


def create_flask_app(celery_app, status_db, testing_config=None):

    app_router = Flask(__name__)
    app = celery_app

    if testing_config:
        app_router.config.update(testing_config)

    @app_router.route("/find/<string:start_path>/<string:end_path>")
    def find(start_path: str, end_path: str) -> str:
        root_path = build_root_path(start_path, end_path)

        if Status.exists(status_db, root_path):
            status = Status(status_db, root_path)
            return "Pending" if status.results_pending() else status.results_str()

        # Initialize status
        status = Status(status_db, root_path, start_path, end_path)

        task = app.send_task(
            "tasks.find",
            kwargs=dict(root_path=root_path, start_path=start_path,),
            queue="find",
        )

        # Assign associated task id to status table
        status.task_id = task.id

        return "Pending"

    #########################################################
    # testing sample functions only used for sanity testing
    #########################################################

    # test function
    @app_router.route("/add/<int:param1>/<int:param2>")
    def add(param1: int, param2: int) -> str:
        task = app.send_task("tasks.add", args=[param1, param2], kwargs={})
        response = f"<a href='{url_for('check_task', task_id=task.id, external=True)}'>check status of {task.id} </a>"
        return response

    # test function
    @app_router.route("/check/<string:task_id>")
    def check_task(task_id: str) -> str:
        res = app.AsyncResult(task_id)
        if res.state == states.PENDING:
            return res.state
        else:
            return str(res.result)

    # test function
    @app.task(bind=True, name="tasks.mul")
    def mul(self, x: int, y: int):
        return x * y

    @app.task(name="tasks.add")
    def add(x: int, y: int) -> int:
        sleep(5)
        return x + y

    return app_router


flask_app = create_flask_app(config_celery_app, config_status_db)
