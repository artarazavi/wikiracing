import pytest

@pytest.fixture(scope='session')
def celery_worker_parameters():
    return {
        'queues':  ('default', 'find_task', 'nlp_task', 'celery', 'nlp'),
    }

