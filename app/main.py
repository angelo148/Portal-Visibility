from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy.orm import Session

from .database import Base, engine, SessionLocal
from .models import User, Group, Content
from .routes import router


def seed(db: Session) -> None:
    """Insert the demo shareholders, groups and content once.

    Takes a session so it can be reused by the app (against SQLite on disk)
    and by the tests (against an isolated in-memory database).
    """
    if db.query(User).first():
        return

    series_a = Group(name="Series A")
    board = Group(name="Board Observers")

    alice = User(name="Alice")
    bob = User(name="Bob")
    charlie = User(name="Charlie")

    alice.groups.append(series_a)
    bob.groups.append(board)

    public = Content(
        title="Public News",
        body="Visible to everyone",
        is_public=True,
    )
    update = Content(
        title="Series A Update",
        body="Only Series A",
        is_public=False,
    )
    minutes = Content(
        title="Board Minutes",
        body="Only Board",
        is_public=False,
    )

    update.groups.append(series_a)
    minutes.groups.append(board)

    db.add_all([alice, bob, charlie, series_a, board, public, update, minutes])
    db.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed(db)
    finally:
        db.close()
    yield


app = FastAPI(title="Portal Content Visibility", lifespan=lifespan)

app.include_router(router)