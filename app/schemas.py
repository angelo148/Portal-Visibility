from pydantic import BaseModel


class ContentOut(BaseModel):
    """Shape returned to shareholders.

    Deliberately omits the audience groups: a shareholder should see the
    content, not the internal access-control list that governs it.
    """

    id: int
    title: str
    body: str
    is_public: bool

    model_config = {"from_attributes": True}