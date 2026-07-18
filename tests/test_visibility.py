import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app, seed


@pytest.fixture()
def client():
    """A TestClient backed by a fresh in-memory database.

    Each test gets an isolated SQLite database that is created, seeded and
    thrown away in memory, so tests never depend on or mutate portal.db.
    The get_db dependency is overridden to use this database.
    """
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(
        bind=engine, autoflush=False, autocommit=False
    )
    Base.metadata.create_all(bind=engine)

    seed_db = TestingSessionLocal()
    seed(seed_db)
    seed_db.close()

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


# --- required: allowed / denied access ---

def test_allowed_group_member_can_view_restricted(client):
    # Alice (Series A) may view the Series A Update.
    assert client.get("/contents/1?user_id=1").status_code == 200


def test_denied_non_member_cannot_view_restricted(client):
    # Charlie (no group) may not view the Board Minutes.
    assert client.get("/contents/2?user_id=3").status_code == 403


# --- public content ---

def test_public_content_visible_to_ungrouped_user(client):
    # Charlie (no group) may view public content.
    assert client.get("/contents/3?user_id=3").status_code == 200


# --- list endpoint returns exactly the visible set ---

def test_list_returns_public_plus_own_group_content(client):
    ids = {item["id"] for item in client.get("/contents?user_id=1").json()}
    assert ids == {1, 3}


def test_list_for_ungrouped_user_is_public_only(client):
    ids = {item["id"] for item in client.get("/contents?user_id=3").json()}
    assert ids == {3}


def test_response_shape_is_consistent(client):
    # Every item has the same keys and never leaks the audience groups.
    for item in client.get("/contents?user_id=1").json():
        assert set(item) == {"id", "title", "body", "is_public"}


# --- edge cases ---

def test_unknown_user_returns_404(client):
    assert client.get("/contents?user_id=999").status_code == 404


def test_unknown_content_returns_404(client):
    assert client.get("/contents/999?user_id=1").status_code == 404


def test_pagination_limit_is_respected(client):
    assert len(client.get("/contents?user_id=1&limit=1").json()) == 1


def test_invalid_pagination_is_rejected(client):
    assert client.get("/contents?user_id=1&limit=-1").status_code == 422