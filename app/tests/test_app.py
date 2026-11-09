import sys
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1] / "src")
)

from app import app


def test_home():
    response = app.test_client().get("/")

    assert response.status_code == 200
    assert response.json["status"] == "running"


def test_health():
    class FakeConnection:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def execute(self, query):
            return None

    def fake_connection():
        return FakeConnection()

    app.config["TESTING"] = True

    from app import get_connection
    original = get_connection

    try:
        import app as app_module
        app_module.get_connection = fake_connection

        response = app.test_client().get("/health")
        assert response.status_code == 200
        assert response.json["database"] == "connected"
    finally:
        app_module.get_connection = original


def test_visits():
    class FakeConnection:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def execute(self, query):
            class Result:
                def fetchone(self):
                    return {"id": 1, "visited_at": "test"}
            return Result()

    import app as app_module
    original = app_module.get_connection

    try:
        app_module.get_connection = lambda: FakeConnection()
        response = app.test_client().get("/visits")
        assert response.status_code == 201
        assert response.json["id"] == 1
    finally:
        app_module.get_connection = original
