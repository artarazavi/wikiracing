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

        Initiates status based on API request received.
        Send async task to find in order to start searching.
        Record task id of find parent task in order to terminate sub-tasks when done.

        Args:
            start_path: Wiki racer game start path.
            end_path: Wiki racer game end path.

        Returns: results traversed path || "Pending" if not done

        """
        root_path = build_root_path(start_path, end_path)

        if Status.exists(status_db, root_path):
            status = Status(status_db, root_path)
            return "Pending" if status.results_pending() else f"solution is: {status.results_str()} time spent: {str(status.end_time)} seconds"

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
