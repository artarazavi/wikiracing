from flask import Flask
import sys
from common import config
from common.status import Status

config_celery_app = config.get_celery_app()
config_status_db = config.get_status_db()


def build_root_path(start_path: str, end_path: str):
    """Build a search key from start path and end path"""
    return f"{start_path}-{end_path}"


def create_flask_app(celery_app, status_db, testing_config=None):
    """ Creates a flask app and sets up routes.

    Args:
        celery_app: Celery app which is a distributed tasks queue
        status_db: Redis status db that tracks state of search.
        testing_config: Notify flask we are in testing mode to use pytest_flask

    Returns: Flask app with routes set up.

    """

    app_router = Flask(__name__)
    app = celery_app

    if testing_config:
        app_router.config.update(testing_config)

    @app_router.route("/find/<string:start_path>/<string:end_path>")
    def find(start_path: str, end_path: str) -> str:
        """ Kicks off wikipedia game based on API request received.

        Find kick off the same search going forward and in reverse.
        For both forward and reverse search:
            Initiates status based on API request received.
            Send async task to find in order to start searching.
            Record task id of find parent task in order to terminate sub-tasks when done.

        Args:
            start_path: Wiki racer game start path.
            end_path: Wiki racer game end path.

        Returns: results traversed path || "Pending" if not done
            Upon first request to find returns "Pending".
            Subsequent requests to find until the solution is found will return "Pending" as well.
            If solution is found request to find will return the traversed path and the time it took to complete in seconds.

        """
        root_path_forward = build_root_path(start_path, end_path)
        root_path_backward = build_root_path(end_path, start_path)

        if Status.exists(status_db, root_path_forward):
            status = Status(status_db, root_path_forward)
            return "Pending" if status.results_pending() else f"solution is: {status.results_str()} time spent: {str(status.end_time)} seconds"

        # GOING FORWARD###########################################################
        # Initialize status
        status_forward = Status(status_db, root_path_forward, start_path, end_path)

        task_forward = app.send_task(
            "tasks.find",
            kwargs=dict(root_path=root_path_forward, start_path=start_path, rev_root_path=root_path_backward),
            queue="find",
        )

        # Assign associated task id to status table
        status_forward.task_id = task_forward.id

        # GOING BACKWARD###########################################################
        # Initialize status
        status_backwards = Status(status_db, root_path_backward, end_path, start_path)

        task_backward = app.send_task(
            "tasks.find",
            kwargs=dict(root_path=root_path_backward, start_path=end_path, rev_root_path=root_path_forward, rev=True),
            queue="find_rev",
        )

        # Assign associated task id to status table
        status_forward.task_id = task_backward.id

        return "Pending"

    return app_router


if __name__ == '__main__':
    args = sys.argv[1:]
    host = "localhost"
    port = 5000

    for x in range(len(args)):
        if args[x] == "--host":
            host = args[x+1]
            x += 1
        if args[x] == "--port":
            port = int(args[x+1])
            x += 1

    flask_app = create_flask_app(config_celery_app, config_status_db)
    flask_app.run(host=host, port=port)
