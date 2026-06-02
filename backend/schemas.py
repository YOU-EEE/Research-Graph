from pydantic import BaseModel, ConfigDict
from typing import Optional, List


class PaperBase(BaseModel):
    title: str
    abstract: Optional[str] = None
    year: Optional[int] = None
    venue: Optional[str] = None
    doi: Optional[str] = None
    arxiv_id: Optional[str] = None
    url: Optional[str] = None
    reading_status: Optional[str] = "unread"


class PaperCreate(PaperBase):
    author_names: List[str] = []
    tag_names: List[str] = []


class PaperUpdate(PaperBase):
    pass


class PaperOut(PaperBase):
    model_config = ConfigDict(from_attributes=True)

    paper_id: int


class NoteCreate(BaseModel):
    paper_id: Optional[int] = None
    title: str
    content: str
    note_type: Optional[str] = "summary"


class NoteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    note_id: int
    paper_id: Optional[int]
    title: str
    content: str
    note_type: Optional[str]


class TagSuggestionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    suggestion_id: int
    paper_id: int
    tag_name: str
    confidence: Optional[float]
    reason: Optional[str]
    is_accepted: bool