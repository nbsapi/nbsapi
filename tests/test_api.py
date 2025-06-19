from fastapi.testclient import TestClient

from nbsapi.main import app

client = TestClient(app)


def test_nbsapi():
    t = True
    assert t, True  # noqa: RUF040
