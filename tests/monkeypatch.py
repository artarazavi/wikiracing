import pytest
from _pytest.monkeypatch import MonkeyPatch


@pytest.fixture(scope="session")
def monkeysession():
    mp = MonkeyPatch()
    yield mp
    mp.undo()


@pytest.fixture(scope="module")
def monkeymodule():
    mp = MonkeyPatch()
    yield mp
    mp.undo()


@pytest.fixture(scope="class")
def monkeyclass():
    mp = MonkeyPatch()
    yield mp
    mp.undo()
