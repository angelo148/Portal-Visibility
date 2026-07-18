from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from .database import Base


class Membership(Base):
    __tablename__ = "memberships"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    group_id = Column(Integer, ForeignKey("groups.id"), primary_key=True)


class ContentAudience(Base):
    __tablename__ = "content_audience"

    content_id = Column(Integer, ForeignKey("contents.id"), primary_key=True)
    group_id = Column(Integer, ForeignKey("groups.id"), primary_key=True)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)

    groups = relationship(
        "Group",
        secondary="memberships",
        back_populates="users"
    )


class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)

    users = relationship(
        "User",
        secondary="memberships",
        back_populates="groups"
    )

    contents = relationship(
        "Content",
        secondary="content_audience",
        back_populates="groups"
    )


class Content(Base):
    __tablename__ = "contents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    body = Column(String)
    is_public = Column(Boolean, default=False)

    groups = relationship(
        "Group",
        secondary="content_audience",
        back_populates="contents"
    )