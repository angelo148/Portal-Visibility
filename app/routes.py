from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from .database import get_db
from .models import User, Content, Membership, ContentAudience
from .schemas import ContentOut

router = APIRouter()


def visible_content_filter(user_id: int):
    """Build a SQL predicate for content a user may see.

    Visible if the item is public, OR it is restricted to at least one
    group the user belongs to. Expressed as a single predicate so the
    database does the filtering (and pagination), not Python.
    """
    user_group_ids = select(Membership.group_id).where(
        Membership.user_id == user_id
    )
    allowed_content_ids = select(ContentAudience.content_id).where(
        ContentAudience.group_id.in_(user_group_ids)
    )
    return or_(
        Content.is_public.is_(True),
        Content.id.in_(allowed_content_ids),
    )


@router.get("/contents", response_model=list[ContentOut])
def get_contents(
    user_id: int,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    stmt = (
        select(Content)
        .where(visible_content_filter(user_id))
        .order_by(Content.id)
        .limit(limit)
        .offset(offset)
    )
    return db.execute(stmt).scalars().all()


@router.get("/contents/{content_id}", response_model=ContentOut)
def get_content_details(
    content_id: int,
    user_id: int,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    if content.is_public:
        return content

    user_group_ids = {group.id for group in user.groups}
    content_group_ids = {group.id for group in content.groups}

    if user_group_ids & content_group_ids:
        return content

    raise HTTPException(status_code=403, detail="Forbidden")