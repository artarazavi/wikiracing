from api import app


class TestMul:
    def test_success(self, celery_app, celery_worker):
        mul = celery_app.task(bind=True, name="tasks.mul")(app.mul)
        assert mul.delay(4, 4).get(timeout=10) == 16